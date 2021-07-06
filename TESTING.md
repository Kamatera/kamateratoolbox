# Testing

Tools to run integration testing for the Kamatera 3rd party drivers

## The testing framework

[Pytest](https://docs.pytest.org/en/latest/) is the testing framework used to run all tests.

Install

```
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Activate the environment

```
. venv/bin/activate
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

Run a single test with full output, by specifying part of the test method name

```
pytest -sk "server_list"
```

Or by specifying the specific test file name:

```
pytest -s tests/cloudcli_server/test_server_list.py
```

Pytest has many options, check the help message or [pytest documentation](https://docs.pytest.org/en/latest/) for details

You can run tests in parallel, the following command runs 6 parallel test sessions:

```
pytest --dist=loadfile -n6
```

### Reuse servers to speed-up the tests 

Keep created session servers to speed up test iterations (remember to terminate them when you're done)

Set env vars so the test framework will not terminate the servers after each test session:

```
export SESSION_SERVER_POWERED_ON_KEEP=yes
export SESSION_SERVER_POWERED_OFF_KEEP=yes
```

Run a test that uses those session servers to create them, check the output for the server details

```
pytest -sk "test_server_attach_only_one_server"
```

The test output should contain the following output, run it so that next runs will use these existing servers

```
export SESSION_SERVER_POWERED_ON_NAME=
export SESSION_SERVER_POWERED_ON_PASSWORD=
export SESSION_SERVER_POWERED_OFF_NAME=
export SESSION_SERVER_POWERED_OFF_PASSWORD=
```

Some tests also use a temporary server which is meant to only be used for a specific test.
While not recommended, you can reuse one of the existing servers for this server using a command like this:
**note that this may cause some tests to fail, if they rely on the server being temporary**

```
TEMP_SERVER_KEEP=yes TEMP_SERVER_NAME=$SESSION_SERVER_POWERED_ON_NAME TEMP_SERVER_PASSWORD=$SESSION_SERVER_POWERED_ON_PASSWORD \
    pytest -sk "test_server_description_set"
```

## Tested components

### cloudcli-server

This is the server-side that supports all the other tools.

Relevant tests are under tests/cloudcli_server

By default, the production cloudcli server is used for testing.

You can also run a local server to debug problems:

Download the latest server code (can skip if you already have a clone of the repository)

```
rm -rf .cloudcli-server &&\
mkdir .cloudcli-server &&\
wget https://github.com/cloudwm/cloudcli-server/archive/master.zip \
     -O .cloudcli-server/cloudcli-server.zip &&\
( cd .cloudcli-server && unzip -q cloudcli-server.zip ) &&\
rm .cloudcli-server/cloudcli-server.zip
```

Build the server Docker image (if you want to use an existing repository clone - replace the path with the path to the repository)

```
docker build -t cloudcli-server .cloudcli-server/cloudcli-server-master
```

Run the server locally

```
docker run -e CLOUDCLI_PROVIDER=proxy -e CLOUDCLI_API_SERVER=https://console.kamatera.com \
           -e LOG_CHANNEL=errorlog -e APP_DEBUG=true \
           --name cloudcli-server --rm -d -p 8000:80 cloudcli-server
```

Set env var to use the local server

```
export KAMATERA_API_SERVER=http://localhost:8000
```

Any pytest tests you run will use this local server

Verify that commands run on this server by checking the logs

```
docker logs cloudcli-server
```

### cloudcli

Cloudcli provide CLI access to all features

By default, the production version is downloaded and used.

You can use your own binary for testing:

```
export CLOUDCLI_BINARY=/path/to/cloudcli
```

The cloudcli schema is also downloaded on each startup, you can speed it up by using your existing schema

First, make sure you have the latest schema: `cloudcli init`

Set the schema file in env var:

```
export CLOUDCLI_SCHEMA_FILE="${HOME}/.cloudcli.schema.json"
```

You can also compile your own cloudcli binary:

Download cloudcli source (skip this if you already have a clone of the repository)

```
rm -rf .cloudcli &&\
mkdir .cloudcli &&\
wget https://github.com/cloudwm/cloudcli/archive/master.zip \
     -O .cloudcli/cloudcli.zip &&\
( cd .cloudcli && unzip -q cloudcli.zip ) &&\
rm .cloudcli/cloudcli.zip
```

Build the binary (if you have a local repository clone, replace .cloudcli/cloudcli-master with the path to your repository clone)

```
mkdir -p .cloudcli/etc &&\
export CLOUDCLI_ETC_PATH=`pwd`/.cloudcli/etc &&\
( cd .cloudcli/cloudcli-master && bin/build.sh start_build_environment && bin/build.sh build )
```

Set env var so the tests use this binary (if you have a local repository clone, replace the path with the path to your local repository):

```
export CLOUDCLI_BINARY=`pwd`/.cloudcli/cloudcli-master/cloudcli
```

## Using curl for quick reproduction and debugging

There are some useful Bash scripts which use curl to allow to easily reproduce and debug cloudcli server and related components.

The scripts are under tests/curl, you should run them from the root of the kamateratoolbox directory, for example:

```
kamateratoolbox$ tests/curl/create_server.sh '{"name": "test1", ...}'
```
