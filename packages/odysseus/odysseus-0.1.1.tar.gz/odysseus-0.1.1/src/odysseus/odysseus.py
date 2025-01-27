import datetime
import requests
import urllib.parse

from threading import Lock, Timer
from typing import Optional, Any, TypeVar, Generic, Dict
from tzlocal import get_localzone
from uuid import uuid4, UUID

########################################################################################################################
log_silent = False
log_tag = 'Odysseus'

def internal_log(message: str):
    if log_silent:
        return
    ts = datetime.datetime.now(tz=get_localzone())
    time = "{:02d}:{:02d}:{:02d}".format(ts.hour, ts.minute, ts.second)
    print(f"[{time}] [INFO] {log_tag}: {message}")


class OdysseusLog:

    def __init__(self, message: str, session_id: UUID,
                 severity: int = 0, tag: Optional[str] = None,
                 file: Optional[str] = None, line: Optional[int] = None,
                 user: Optional[str] = None, timestamp: Optional[datetime.datetime] = None,
                 context: Optional[Dict[str, Any]] = None):

        self.session_id = session_id.hex
        self.message = message
        self.severity = severity
        self.tag = tag
        self.timestamp = datetime.datetime.now(tz=get_localzone()).isoformat() if timestamp is None else timestamp.isoformat()
        self.file = file
        self.line = line
        self.user = user
        self.context = context


class OdysseusEvent:

    def __init__(self, id: UUID, name: str, session_id: UUID, type: int = 0, stream_id: Optional[UUID] = None, position: int = 0,
                 user: Optional[str] = None, timestamp: Optional[datetime.datetime] = None,
                 data: Optional[Dict[str, Any]] = None, meta: Optional[Dict[str, Any]] = None):

        self.id = id.hex
        self.session_id = session_id.hex
        self.name = name
        self.type = type
        self.timestamp = datetime.datetime.now(tz=get_localzone()).isoformat() if timestamp is None else timestamp.isoformat()
        self.stream_id = uuid4().hex if stream_id is None else stream_id.hex
        self.position = position
        self.user = user
        self.data = data
        self.meta = meta


T = TypeVar('T')

class OdysseusCollection(Generic[T]):

    def __init__(self, endpoint: str, entity_name: str, delay: int = 5):
        self.entries: [T] = []
        self.to_upload: [T] = []
        self.endpoint = endpoint
        self.entity_name = entity_name
        self.delay = delay
        self.timer = None
        self.lock = Lock()

    def add(self, item: T):
        with self.lock:
            self.entries.append(item)

            if self.timer is None:
                self.timer = Timer(self.delay, self.execute_upload)
                self.timer.start()

    def execute_upload(self):

        # copy the entries aside and try to upload them
        with self.lock:
            self.to_upload = self.entries
            self.entries = []

        success = False
        try:
            success = self.upload_entries(self.to_upload)
            if success:
                # once upload finished successfully, clear all temporary data
                with self.lock:
                    self.to_upload = []
                    self.timer = None
        except Exception as e:
            internal_log(f"Failed to upload {self.entity_name} to Odysseus: {e}")

        if not success or len(self.entries) > 0:
            with self.lock:
                self.to_upload.extend(self.entries)
                self.entries = []

                # restart the timer
                self.timer = Timer(self.delay, self.execute_upload)
                self.timer.start()

    def upload_entries(self, data: [T]) -> bool:
        url = "https://odysseus.codetitans.dev" + self.endpoint
        # url = "http://192.168.2.183:5757" + self.endpoint
        response = requests.post(url, json=[x.__dict__ for x in data])

        global log_silent
        if 200 <= response.status_code < 300:
            if not log_silent:
                text = response.text
                internal_log(f"Successfully uploaded {self.entity_name} to Odysseus: {response.status_code} (\"{text}\")")
            return True
        else:
            if not log_silent:
                text = response.text
                internal_log(f"Failed to upload {self.entity_name} to Odysseus: {response.status_code} ({text})")
            return False


class OdysseusClient:

    def __init__(self, app_id: str, app_key: str, user: Optional[str] = None, session: Optional[UUID] = None,
                 min_severity: int = 1, silent: bool = False):
        global log_silent
        log_silent = silent

        self.user_id = user
        self.session_id = uuid4() if session is None else session
        self.min_severity_level = min_severity
        self.app_id = app_id
        self.app_key = app_key
        self.logs = OdysseusCollection[OdysseusLog](endpoint="/api/logs" + urllib.parse.quote('/' + app_id + '/' + app_key), delay=5, entity_name="logs")
        self.events = OdysseusCollection[OdysseusEvent](endpoint="/api/events" + urllib.parse.quote('/' + app_id + '/' + app_key), delay=5, entity_name="events")

        internal_log(f"Initialised for application: \"{self.app_id}\" (session: \"{self.session_id.hex}\", delay: {self.logs.delay}s)")

    @property
    def user(self) -> Optional[str]:
        return self.user_id

    @user.setter
    def user(self, value: Optional[str] = None):
        self.user_id = value

    @property
    def session(self) -> UUID:
        return self.session_id

    @session.setter
    def session(self, value: UUID):
        self.session_id = value

    @property
    def min_severity(self) -> int:
        return self.min_severity_level

    @min_severity.setter
    def min_severity(self, value: int):
        self.min_severity_level = value

    def log(self, message: str, severity: int, tag: Optional[str] = None,
            file: Optional[str] = None, line: Optional[int] = None, timestamp: Optional[datetime.datetime] = None,
            context: Optional[Dict[str, Any]] = None) -> Optional[OdysseusLog]:
        if severity < self.min_severity_level:
            return None

        return self.add_log(OdysseusLog(message, self.session_id, severity=severity, tag=tag,
                                        user=self.user_id, timestamp=timestamp, file=file, line=line, context=context))

    def add_log(self, entry: OdysseusLog) -> Optional[OdysseusLog]:
        if entry.severity < self.min_severity_level:
            return None

        self.logs.add(entry)
        return entry

    def event(self, name: str, id: Optional[UUID] = None, type: int = 0, stream_id: Optional[UUID] = None, position: Optional[int] = None,
              timestamp: Optional[datetime.datetime] = None,
              data: Optional[Dict[str, Any]] = None, meta: Optional[Dict[str, Any]] = None) -> OdysseusEvent:
        return self.add_event(OdysseusEvent(
            uuid4() if id is None else id,
            name=name, session_id=self.session_id, type=type, stream_id=stream_id, position=position,
            user=self.user, timestamp=timestamp, data=data, meta=meta))

    def add_event(self, event: OdysseusEvent) -> OdysseusEvent:
        self.events.add(event)
        return event




