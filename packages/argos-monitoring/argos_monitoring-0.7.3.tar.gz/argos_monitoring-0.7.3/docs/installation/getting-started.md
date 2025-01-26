---
description: Install Argos, with all the explanations you want.
---
# Installation

NB: if you want a quick-installation guide, we [got you covered](tl-dr.md).

## Requirements

- Python 3.11+
- PostgreSQL 13+ (for production)

### Optional dependencies

If you want to use LDAP authentication, you will need to install some packages (here for a Debian-based system):

```bash
apt-get install build-essential python3-dev libldap-dev libsasl2-dev
```

## Recommendation

Create a dedicated user for argos:

```bash
adduser --home /opt/argos --disabled-login --disabled-password --system argos
```

Do all the manipulations below in `/opt/argos/`, with the user `argos`.
Either use `sudo` or login as `argos` with the following command:

```bash
su argos -s /bin/bash
```

## Install with pip

```bash
pip install argos-monitoring
```

You may want to install Argos in a virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
pip install argos-monitoring
```

For production, we recommend the use of [Gunicorn](https://gunicorn.org/), which you can install at the same time as Argos:

```bash
pip install "argos-monitoring[gunicorn]"
```

If you want to use LDAP authentication, you’ll need to install Argos this way:

```bash
pip install "argos-monitoring[ldap]"
```

And for an installation with Gunicorn and LDAP authentication:

```bash
pip install "argos-monitoring[gunicorn,ldap]"
```

## Install from sources

Once you got the source locally, create a virtualenv and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

To install gunicorn, use `pip install -e ".[gunicorn]"` instead of `pip install -e .`

## Configure

The quickest way to get started is to generate the configuration file from argos and edit it:

```bash
argos server generate-config > argos-config.yaml
```

You can read more about the configuration in the [configuration section](../configuration.md).

For production, we suggest to put your config in `/etc/argos/config.yaml` and restricts the file’s permissions.
As root:
```bash
mkdir /etc/argos
chown argos: /etc/argos
chmod 700 /etc/argos
```

Then, as `argos`:
```bash
argos server generate-config > /etc/argos/config.yaml
chmod 600 /etc/argos/config.yaml
```

Please note that the only supported database engines are SQLite for development and [PostgreSQL](postgresql.md) for production.

## Apply migrations to database

Create the schema in the database with:

```bash
argos server migrate
```

## Inject tasks into the database

Argos keeps tasks’ configuration in database, taken from the config file.

Populate the database with the tasks:

```bash
argos server reload-config
```

## Generating a token

The agent needs an authentication token to be able to communicate with the server.

You can generate an authentication token with the following command:
```bash
argos server generate-token
```

Add the token in the configuration file, in the following setting:

```yaml
service:
  secrets:
    - "auth-token"
```

## Starting the server

Then you can start the server:

```bash
argos server start
```

This way to start the server is not suitable for production, use it only for developing or testing.

## Starting the server for production

For production, you can use [Gunicorn](https://gunicorn.org/) to start the server.

To install Gunicorn in the virtualenv, if you didn’t already install Argos that way:

```bash
pip install "argos-monitoring[gunicorn]"
```

To start the server:

```bash
gunicorn "argos.server.main:get_application()" -k uvicorn.workers.UvicornWorker
```

There is some gunicorn’s options that you should use:
- `-w INT, --workers INT`: the number of worker processes for handling requests. Default is `1`.
- `-b ADDRESS, --bind ADDRESS`: the socket to bind. Default is `127.0.0.1:8000`.
- `--forwarded-allow-ips STRING`: front-end's IPs from which allowed to handle set secure headers as a comma-separated list. Default is `127.0.0.1`.

So, to start the server with 4 workers while listening to `127.0.0.1:8001`:

```bash
gunicorn "argos.server.main:get_application()" -k uvicorn.workers.UvicornWorker -w 4 -b 127.0.0.1:8001
```

Gunicorn has a lot of other options, have a look at `gunicorn --help`.

Argos uses FastAPI, so you can use other ways to start the server.
See <https://fastapi.tiangolo.com/deployment/manually/#asgi-servers> (but Gunicorn is recommended).

See [here](../deployment/systemd.md#server) for a systemd service example and [here](../deployment/nginx.md) for a nginx configuration example.

## Running the agent

You can run the agent on the same machine as the server, or on a different machine.
The only requirement is that the agent can reach the server through HTTP or HTTPS.

```bash
argos agent http://localhost:8000 "auth-token"
```

## Cleaning the database

You have to run cleaning task periodically. `argos server cleandb --help` will give you more information on how to do that.

Here is a crontab example, which will clean the db each hour:

```bash
# Run the cleaning tasks every hour (at minute 7)
# Keeps 10 results per task, and remove tasks’ locks older than 1 hour
7 * * * * argos server cleandb --max-results 10 --max-lock-seconds 3600
```

## Watch the agents

In order to be sure that agents are up and communicate with the server, you can periodically run the `argos server watch-agents` command.

Here is a crontab example, which will check the agents every 5 minutes:

```bash
*/5 * * * * argos server watch-agents --time-without-agent 10
```

Check the documentation of the command with `argos server watch-agents --help`
