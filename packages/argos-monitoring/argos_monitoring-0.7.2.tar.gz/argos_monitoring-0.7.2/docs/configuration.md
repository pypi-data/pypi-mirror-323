---
description: How to configure Argos.
---
# Configuration

Argos uses a simple YAML configuration file to define the server’s configuration, the websites to monitor and the checks to run on these websites.

See [here](checks.md) for more informations about the checks you can use.

Here is a simple self-documented configuration file, which you can get with [`argos server generate-config`](cli.md#server-generate-config):

```{literalinclude} ../conf/config-example.yaml
---
caption: argos-config.yaml
---
```
