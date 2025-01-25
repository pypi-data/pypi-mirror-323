---
description: Adding a new notification way is quite simple.
---
# Add a notification way

Adding a new notification way is quite simple.

First, you need to think about how you will configure it.
As example, here’s how gotify notifications are configured:
```yaml
gotify:
  - url: https://example.org
    tokens:
      - foo
      - bar
```

Feel free to open an issue to discuss about your notification way or its configuration before coding!
See [#50](https://framagit.org/framasoft/framaspace/argos/-/issues/50) for example.

Then, you’ll need to add the pydantic schema matching your config in [`argos/schemas/config.py`](https://framagit.org/framasoft/framaspace/argos/-/blob/main/argos/schemas/config.py).

For gotify, it’s:
```python
class GotifyUrl(BaseModel):
    url: HttpUrl
    tokens: List[str]
```

Add the schema to the `General` schema in the same file (don’t forget to make it optional).

For gotify, we added this:
```python
    gotify: Optional[List[GotifyUrl]] = None
```

Finally, write a function which use your new notification way in [`argos/server/alerting.py`](https://framagit.org/framasoft/framaspace/argos/-/blob/main/argos/server/alerting.py) and use it in the `handle_alert` function of the same file.
