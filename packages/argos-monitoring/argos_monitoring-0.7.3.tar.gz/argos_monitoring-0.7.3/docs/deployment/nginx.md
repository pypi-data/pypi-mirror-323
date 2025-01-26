---
description: How to configure Nginx to use with Argos.
---
# Using Nginx as reverse proxy

Here is a example for Nginx configuration:
```{literalinclude} ../../conf/nginx.conf
---
caption: /etc/nginx/sites-available/argos.example.org
---
```

If you want to use Argos under a subdirectory of your web server, you’ll need to set the `root_path` setting in Argos’s [configuration](../configuration.md) and set Nginx like this:

```{literalinclude} ../../conf/nginx-subdirectory.conf
---
caption: Nginx’s location for Argos in a subdirectory
---
```
