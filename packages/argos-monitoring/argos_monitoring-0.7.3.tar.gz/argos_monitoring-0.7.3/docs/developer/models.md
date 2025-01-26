---
description: What’s in the database?
---
# The data model

```{mermaid}
classDiagram
direction RL
class Task {
    - url
    - domain
    - check
    - expected
    - frequency
    - selected_by
    - selected_at
    - completed_at
    - next_run
    - severity
    - last_severity_update
}
class Result{
    - task : Task
    - task_id
    - agent_id
    - submitted_at
    - status
    - severity
    - context
}
class ConfigCache {
    - name
    - val
    - updated_at
}
class User {
    - username
    - password
    - disabled
    - created_at
    - updated_at
    - last_login_at
}
Result "*" o-- "1" Task : has many
```

The `severity` attribute in `Task` is the severity of the last `Result` submitted by an agent.


```{literalinclude} ../../argos/server/models.py
---
caption: models.py
---
```
