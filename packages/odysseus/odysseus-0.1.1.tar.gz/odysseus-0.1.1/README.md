# Odysseus Platform - Python client

This repository contains full source code of the simple Python project capable of uploading log entries or events happening on a backend application - back to the [Odysseus Logging Platform](https://odysseus.codetitans.dev).

Once it's added as a dependency of your Python application, it has to be connected with your existing logging system and logs serialization has to be redirected to be able to process them and pass back to the server.

## Disclaimer

Full utilization of the Odysseus Logging Platform services is subject to the proper contract and not part of that client functionality. By using this software you essentially agree that since it's an open-source project you read it and understand all repercussions of using it. Thus you will never claim or call for any compensations or damages in connection with downtime of your own services caused by this software.

## Build

To create the new bundled release simply call following command:

```shell
$ ./build.sh package
```

What it does internally, is only performs several checks around missing environmental setup and calls the build command:

```shell
$ python3 -m build
```

-----
CodeTitans Sp. z o.o. (2025-)
