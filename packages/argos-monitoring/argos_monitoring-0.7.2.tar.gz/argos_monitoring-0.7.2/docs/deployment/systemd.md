---
description: Here are the systemd files that can be used to deploy the server and the agents.
---
# Using systemd

Here are the systemd files that can be used to deploy the server and the agents.

## Agent

```{literalinclude} ../../conf/default-argos-agent
---
caption: /etc/default/argos-agent
---
```

```{literalinclude} ../../conf/systemd-agent.service
---
caption: /etc/systemd/system/argos-agent.service
---
```

## Server

```{literalinclude} ../../conf/default-argos-server
---
caption: /etc/default/argos-server
---
```

```{literalinclude} ../../conf/systemd-server.service
---
caption: /etc/systemd/system/argos-server.service
---
```
