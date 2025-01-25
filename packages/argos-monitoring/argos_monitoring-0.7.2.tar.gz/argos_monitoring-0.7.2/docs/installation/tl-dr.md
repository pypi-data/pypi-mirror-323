---
description: You want to install Argos fast? Ok, here we go.
---
# TL;DR: fast installation instructions

You want to install Argos fast? Ok, here we go.

## For testing

This is for testing only!

```bash
sudo apt install python3
mkdir /tmp/argos
cd /tmp/argos
python3 -m venv venv
source venv/bin/activate
pip install argos-monitoring
argos server generate-config |
    sed -e "s@production@dev@" \
        -e "s@url: .postgresql.*@url: \"sqlite:////tmp/argos.db\"@" > argos-config.yaml
argos server migrate
ARGOS_TOKEN=$(argos server generate-token)
sed -e "s@# - secret_token@- $ARGOS_TOKEN@" -i argos-config.yaml
echo "The agent token is $ARGOS_TOKEN"
```

Edit `argos-config.yaml`.
Add some real web sites to test.

Then:

```
argos server reload-config
argos server start --host 0.0.0.0 --port 8000
```

In another terminal:

```
cd /tmp/argos
source venv/bin/activate
argos agent http://127.0.0.1:8000 the_generated_token
```

Then go to `http://127.0.0.1:8000` or `http://the_IP_address_of_your_server:8000`.

## For production

```bash
apt install python3 postgresql
sudo -u postgres createuser -P argos
sudo -u postgres createdb -O argos argos
sudo -u postgres psql -c "ALTER DATABASE argos SET TIMEZONE TO 'UTC';"
adduser --home /opt/argos --disabled-login --disabled-password --system argos

cd /opt/argos
sudo -u argos python3 -m venv venv
sudo -u argos bash -c 'source venv/bin/activate && pip install "argos-monitoring[gunicorn]"'

mkdir /etc/argos
/opt/argos/venv/bin/argos server generate-config > /etc/argos/config.yaml

cat <<EOF > /etc/default/argos-server
ARGOS_YAML_FILE="/etc/argos/config.yaml"
ARGOS_SERVER_WORKERS=4
ARGOS_SERVER_SOCKET=127.0.0.1:8000
# Comma separated list of IP addresses of the web proxy (usually Nginx)
ARGOS_SERVER_FORWARDED_ALLOW_IPS=127.0.0.1
EOF

cat <<EOF > /etc/default/argos-agent
ARGOS_AGENT_TOKEN=Secret
ARGOS_AGENT_SERVER_URL=http://127.0.0.1:8000
ARGOS_AGENT_LOGLEVEL=WARNING
ARGOS_AGENT_MAX_TASKS=20
ARGOS_AGENT_WAIT_TIME=10
EOF

cat <<EOF > /etc/systemd/system/argos-server.service
[Unit]
Description=Argos server
Documentation=https://argos-monitoring.framasoft.org/
Requires=network.target postgresql.service
After=network.target postgresql.service
PartOf=postgresql.service

[Service]
User=argos
WorkingDirectory=/opt/argos/
EnvironmentFile=/etc/default/argos-server
ExecStartPre=/opt/argos/venv/bin/argos server migrate
ExecStartPre=/opt/argos/venv/bin/argos server reload-config
ExecStart=/opt/argos/venv/bin/gunicorn "argos.server.main:get_application()" \\
                                       --workers \$ARGOS_SERVER_WORKERS \\
                                       --worker-class uvicorn.workers.UvicornWorker \\
                                       --bind \$ARGOS_SERVER_SOCKET \\
                                       --forwarded-allow-ips \$ARGOS_SERVER_FORWARDED_ALLOW_IPS
ExecReload=/opt/argos/venv/bin/argos server reload-config
SyslogIdentifier=argos-server

[Install]
WantedBy=multi-user.target
EOF

cat <<EOF > /etc/systemd/system/argos-agent.service
[Unit]
Description=Argos agent
Documentation=https://argos-monitoring.framasoft.org/
Requires=network.target
After=network.target

[Service]
User=argos
EnvironmentFile=/etc/default/argos-agent
WorkingDirectory=/opt/argos/
ExecStart=/opt/argos/venv/bin/argos agent --max-tasks \$ARGOS_AGENT_MAX_TASKS \\
                                          --wait-time \$ARGOS_AGENT_WAIT_TIME \\
                                          --log-level \$ARGOS_AGENT_LOGLEVEL
SyslogIdentifier=argos-agent

[Install]
WantedBy=multi-user.target
EOF

chown -R argos: /etc/default/argos-* /etc/argos/
chmod 700 /etc/argos
chmod 600 /etc/argos/config.yaml

systemctl daemon-reload
```

Then, edit `/etc/argos/config.yaml` to put your database password in it and change the other settings to suit your needs.

Create a token for your agent :

```bash
sudo -u argos /opt/argos/venv/bin/argos server generate-token
```

Edit `/etc/default/argos-agent` to put the generated token in it and change the other settings to suit your needs.

Edit `/etc/argos/config.yaml` to configure Argos (don’t forget to add the generated token in it too).

Enable and start the server and the agent and make sure they works:

```bash
systemctl enable --now argos-server.service argos-agent.service
systemctl status argos-server.service argos-agent.service
```

If all works well, you have to put some cron tasks in `argos` crontab:

```bash
cat <<EOF | crontab -u argos -
*/10 * * * * /opt/argos/venv/bin/argos server cleandb --max-lock-seconds 120 --max-results 1200
*/10 * * * * /opt/argos/venv/bin/argos server watch-agents --time-without-agent 10
EOF
```

See the [this page](../deployment/nginx.md) for using Nginx as reverse proxy.
