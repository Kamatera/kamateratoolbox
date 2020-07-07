# Testing

Tools to run integration testing for the Kamatera 3rd party drivers

## Using Pytest

[Pytest](https://docs.pytest.org/en/latest/) is the testing framework used to run all tests.

Install

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Set env vars

```
export KAMATERA_API_CLIENT_ID=
export KAMATERA_API_SECRET=
export KAMATERA_API_SERVER=https://cloudcli.cloudwm.com
export TESTING_SSHKEY_PATH=/path/to/key.id_rsa
```

Run all tests

```
pytest
```

Run a single test with full output

```
pytest -sk "server_list"
```

Keep created session servers to speed up test iterations (remember to terminate them when you're done)

```
export SESSION_SERVER_POWERED_ON_KEEP=yes
export SESSION_SERVER_POWERED_OFF_KEEP=yes
```

Run a test that uses those session servers to create them

```
pytest -sk "test_server_attach_only_one_server"
```

check output for the following env vars, set them and next runs will use the existing servers

```
export SESSION_SERVER_POWERED_ON_NAME=
export SESSION_SERVER_POWERED_ON_PASSWORD=
export SESSION_SERVER_POWERED_OFF_NAME=
export SESSION_SERVER_POWERED_OFF_PASSWORD=
```

Some tests use a temporary server which should be used only for a specific test, for local development you can use the created session server for those tests:

```
TEMP_SERVER_KEEP=yes TEMP_SERVER_NAME=$SESSION_SERVER_POWERED_ON_NAME TEMP_SERVER_PASSWORD=$SESSION_SERVER_POWERED_ON_PASSWORD pytest -sk "test_server_description_set"
```

## cloudcli-server

This is the server-side that supports all the other tools.

Relevant tests are undet tests/cloudcli_server

By default, the production server is used for testing. You can also run a local server to debug problems:

Download the latest server code

```
rm -rf .cloudcli-server &&\
mkdir .cloudcli-server &&\
wget https://github.com/cloudwm/cloudcli-server/archive/master.zip \
     -O .cloudcli-server/cloudcli-server.zip &&\
( cd .cloudcli-server && unzip -q cloudcli-server.zip ) &&\
rm .cloudcli-server/cloudcli-server.zip
```

Build the server Docker image

```
docker build -t cloudcli-server .cloudcli-server/cloudcli-server-master
```

Run

```
docker run -e CLOUDCLI_PROVIDER=proxy -e CLOUDCLI_API_SERVER=https://console.kamatera.com \
           -e LOG_CHANNEL=errorlog -e APP_DEBUG=true \
           --name cloudcli-server --rm -d -p 8000:80 cloudcli-server
```

Set env var to use the local server

```
export KAMATERA_API_SERVER=http://localhost:8000
```

## cloudcli

Cloudcli provide CLI access to all features

By default, the production version is downloaded and used, however you can use your own binary for testing:

```
export CLOUDCLI_BINARY=/path/to/cloudcli
```

The cloudcli schema is also downloaded on each startup, you can speed it up by using your existing schema:

```
export CLOUDCLI_SCHEMA_FILE="${HOME}/.cloudcli.schema.json"
```

You can also compile your own cloudcli binary:

```
rm -rf .cloudcli &&\
mkdir .cloudcli &&\
wget https://github.com/cloudwm/cloudcli/archive/master.zip \
     -O .cloudcli/cloudcli.zip &&\
( cd .cloudcli && unzip -q cloudcli.zip ) &&\
rm .cloudcli/cloudcli.zip
```

Build

```
mkdir -p .cloudcli/etc &&\
export CLOUDCLI_ETC_PATH=`pwd`/.cloudcli/etc &&\
( cd .cloudcli/cloudcli-master && bin/build.sh start_build_environment && bin/build.sh build )
```

Set env var so the tests use this binary:

```
export CLOUDCLI_BINARY=`pwd`/.cloudcli/cloudcli-master/cloudcli
```
