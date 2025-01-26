---
description: How to use Argos from the command line.
---
# Command-line interface

<!-- [[[cog
    from argos.commands import cli
    from click.testing import CliRunner
    def help(args):
        title = "argos " + " ".join(args)
        cog.out("\n```man\n")
        result = CliRunner().invoke(cli, args)
        output = result.output.replace("Usage: cli ", "Usage: argos ")
        cog.out(output)
        cog.out("```\n\n")
 ]]] -->
<!-- [[[end]]] -->

## The argos cli
<!--
.. [[[cog
    help(["--help"])
.. ]]] -->

```man
Usage: argos [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  agent    Get and run tasks for the provided server.
  server   Commands for managing server, server’s configuration and users
  version  Prints Argos’ version and exits
```

<!--[[[end]]]
-->

## Agent command
<!--
.. [[[cog
    help(["agent", "--help"])
.. ]]] -->

```man
Usage: argos agent [OPTIONS] SERVER_URL AUTH

  Get and run tasks for the provided server. Will wait for new tasks.

  Usage: argos agent https://argos.example.org "auth-token-here"

  Alternatively, you can use the following environment variables to avoid
  passing arguments to the agent on the command line:

      ARGOS_AGENT_SERVER_URL=https://argos.example.org
      ARGOS_AGENT_TOKEN=auth-token-here

Options:
  --max-tasks INTEGER             Number of concurrent tasks this agent can run
  --wait-time INTEGER             Waiting time between two polls on the server
                                  (seconds)
  --log-level [DEBUG|INFO|WARNING|ERROR|CRITICAL]
  --help                          Show this message and exit.
```

<!--[[[end]]]
-->

## Server commands
<!--
.. [[[cog
    help(["server", "--help"])
.. ]]] -->

```man
Usage: argos server [OPTIONS] COMMAND [ARGS]...

  Commands for managing server, server’s configuration and users

Options:
  --help  Show this message and exit.

Commands:
  cleandb          Clean the database (to run routinely)
  generate-config  Output a self-documented example config file.
  generate-token   Generate a token for agents
  migrate          Run database migrations
  nagios           Nagios compatible severities report
  reload-config    Load or reload tasks’ configuration
  start            Starts the server (use only for testing or development!)
  test-apprise     Send a test apprise notification
  test-gotify      Send a test gotify notification
  test-mail        Send a test email
  user             User management
  watch-agents     Watch agents (to run routinely)
```

<!--[[[end]]]
-->

### Server start
<!--
.. [[[cog
    help(["server", "start", "--help"])
.. ]]] -->

```man
Usage: argos server start [OPTIONS]

  Starts the server (use only for testing or development!)

  See https://argos-monitoring.framasoft.org/deployment/systemd.html#server for
  advices on how to start the server for production.

Options:
  --host TEXT     Host to bind
  --port INTEGER  Port to bind
  --config TEXT   Path of the configuration file. If ARGOS_YAML_FILE environment
                  variable is set, its value will be used instead. Default
                  value: argos-config.yaml and /etc/argos/config.yaml as
                  fallback.
  --reload        Enable hot reloading
  --help          Show this message and exit.
```

<!--[[[end]]]
-->

### Server migrate

<!--
.. [[[cog
    help(["server", "migrate", "--help"])
.. ]]] -->

```man
Usage: argos server migrate [OPTIONS]

  Run database migrations

Options:
  --config TEXT  Path of the configuration file. If ARGOS_YAML_FILE environment
                 variable is set, its value will be used instead. Default value:
                 argos-config.yaml and /etc/argos/config.yaml as fallback.
  --help         Show this message and exit.
```

<!--[[[end]]]
-->


### Server cleandb
<!--
.. [[[cog
    help(["server", "cleandb", "--help"])
.. ]]] -->

```man
Usage: argos server cleandb [OPTIONS]

  Clean the database (to run routinely)

  - Removes old results from the database.
  - Removes locks from tasks that have been locked for too long.

Options:
  --max-results INTEGER       Number of results per task to keep
  --max-lock-seconds INTEGER  The number of seconds after which a lock is
                              considered stale, must be higher than 60 (the
                              checks have a timeout value of 60 seconds)
  --config TEXT               Path of the configuration file. If ARGOS_YAML_FILE
                              environment variable is set, its value will be
                              used instead. Default value: argos-config.yaml and
                              /etc/argos/config.yaml as fallback.
  --help                      Show this message and exit.
```

<!--[[[end]]]
-->

### Server watch-agents

<!--
.. [[[cog
    help(["server", "cleandb", "--help"])
.. ]]] -->

```man
Usage: argos server cleandb [OPTIONS]

  Clean the database (to run routinely)

  - Removes old results from the database.
  - Removes locks from tasks that have been locked for too long.

Options:
  --max-results INTEGER       Number of results per task to keep
  --max-lock-seconds INTEGER  The number of seconds after which a lock is
                              considered stale, must be higher than 60 (the
                              checks have a timeout value of 60 seconds)
  --config TEXT               Path of the configuration file. If ARGOS_YAML_FILE
                              environment variable is set, its value will be
                              used instead. Default value: argos-config.yaml and
                              /etc/argos/config.yaml as fallback.
  --help                      Show this message and exit.
```

<!--[[[end]]]
-->

### Server reload-config

<!--
.. [[[cog
    help(["server", "reload-config", "--help"])
.. ]]] -->

```man
Usage: argos server reload-config [OPTIONS]

  Read tasks’ configuration and add/delete tasks in database if needed

Options:
  --config TEXT  Path of the configuration file. If ARGOS_YAML_FILE environment
                 variable is set, its value will be used instead. Default value:
                 argos-config.yaml and /etc/argos/config.yaml as fallback.
  --help         Show this message and exit.
```

<!--[[[end]]]
-->

### Server generate-config

<!--
.. [[[cog
    help(["server", "generate-config", "--help"])
.. ]]] -->

```man
Usage: argos server generate-config [OPTIONS]

  Output a self-documented example config file.

  Redirect the output to a file to save it:
      argos server generate-config > /etc/argos/config.yaml

Options:
  --help  Show this message and exit.
```

<!--[[[end]]]
-->

### Server generate-token

<!--
.. [[[cog
    help(["server", "generate-token", "--help"])
.. ]]] -->

```man
Usage: argos server generate-token [OPTIONS]

  Generate a token, which can be used as an agent’s authentication token.

  It’s actually an UUID

Options:
  --help  Show this message and exit.
```

<!--[[[end]]]
-->

### Server user management

You can choose to protect Argos’ web interface with a user system, in which case you’ll need to create at least one user.

See [`unauthenticated_access` in the configuration file](configuration.md) to allow partial or total unauthenticated access to Argos.

See [`ldap` in the configuration file](configuration.md) to authenticate users against a LDAP server instead of Argos’ database.

You can manage Argos’ users only through CLI.

NB: you can’t manage the LDAP users with Argos.

<!--
.. [[[cog
    help(["server", "user", "--help"])
.. ]]] -->

```man
Usage: argos server user [OPTIONS] COMMAND [ARGS]...

  User management

Options:
  --help  Show this message and exit.

Commands:
  add              Add new user
  change-password  Change user’s password
  delete           Delete user
  disable          Disable user
  enable           Enable user
  show             List all users
  verify-password  Test user’s password
```

<!--[[[end]]]
-->

#### Add user

<!--
.. [[[cog
    help(["server", "user", "add", "--help"])
.. ]]] -->

```man
Usage: argos server user add [OPTIONS]

  Add new user

Options:
  --config TEXT    Path of the configuration file. If ARGOS_YAML_FILE
                   environment variable is set, its value will be used instead.
  --name TEXT      Name of the user to create.
  --password TEXT
  --help           Show this message and exit.
```

<!--[[[end]]]
-->

#### Change the password of a user

<!--
.. [[[cog
    help(["server", "user", "change-password", "--help"])
.. ]]] -->

```man
Usage: argos server user change-password [OPTIONS]

  Change user’s password

Options:
  --config TEXT    Path of the configuration file. If ARGOS_YAML_FILE
                   environment variable is set, its value will be used instead.
  --name TEXT      Name of the user you want to change the password.
  --password TEXT
  --help           Show this message and exit.
```

<!--[[[end]]]
-->

#### Delete a user

<!--
.. [[[cog
    help(["server", "user", "delete", "--help"])
.. ]]] -->

```man
Usage: argos server user delete [OPTIONS]

  Delete user

Options:
  --config TEXT  Path of the configuration file. If ARGOS_YAML_FILE environment
                 variable is set, its value will be used instead.
  --name TEXT    Name of the user to delete.  [required]
  --help         Show this message and exit.
```

<!--[[[end]]]
-->

#### Disable a user

Disabling a user prevents the user to login and access Argos’ web interface but its credentials are still stored in Argos’ database.

<!--
.. [[[cog
    help(["server", "user", "disable", "--help"])
.. ]]] -->

```man
Usage: argos server user disable [OPTIONS]

  Disable user

Options:
  --config TEXT  Path of the configuration file. If ARGOS_YAML_FILE environment
                 variable is set, its value will be used instead.
  --name TEXT    Name of the user to disable.  [required]
  --help         Show this message and exit.
```

<!--[[[end]]]
-->

#### Enable a user

Enabling a user prevents the user to login and access Argos’ web interface.

Obviously, the user needs to exists and to be disabled before using the command.

<!--
.. [[[cog
    help(["server", "user", "enable", "--help"])
.. ]]] -->

```man
Usage: argos server user enable [OPTIONS]

  Enable user

Options:
  --config TEXT  Path of the configuration file. If ARGOS_YAML_FILE environment
                 variable is set, its value will be used instead.
  --name TEXT    Name of the user to reenable  [required]
  --help         Show this message and exit.
```

<!--[[[end]]]
-->

#### List all users

Show all accounts, with their status (enabled or disabled).

<!--
.. [[[cog
    help(["server", "user", "show", "--help"])
.. ]]] -->

```man
Usage: argos server user show [OPTIONS]

  List all users

Options:
  --config TEXT  Path of the configuration file. If ARGOS_YAML_FILE environment
                 variable is set, its value will be used instead.
  --help         Show this message and exit.
```

<!--[[[end]]]
-->

#### Test the password of a user

You can verify that you have the right password for a user with the following command:

<!--
.. [[[cog
    help(["server", "user", "verify-password", "--help"])
.. ]]] -->

```man
Usage: argos server user verify-password [OPTIONS]

  Test user’s password

Options:
  --config TEXT    Path of the configuration file. If ARGOS_YAML_FILE
                   environment variable is set, its value will be used instead.
  --name TEXT      Name of the user you want to test the password for.
                   [required]
  --password TEXT
  --help           Show this message and exit.
```

<!--[[[end]]]
-->

### Use as a nagios probe

You can directly use Argos to get an output and an exit code usable with Nagios.

<!--
.. [[[cog
    help(["server", "nagios", "--help"])
.. ]]] -->

```man
Usage: argos server nagios [OPTIONS]

  Output a report of current severities suitable for Nagios with a Nagios
  compatible exit code

Options:
  --config TEXT  Path of the configuration file. If ARGOS_YAML_FILE environment
                 variable is set, its value will be used instead.
  --help         Show this message and exit.
```

<!--[[[end]]]
-->

### Test the email settings

You can verify that your mail settings are ok by sending a test email.

<!--
.. [[[cog
    help(["server", "test-mail", "--help"])
.. ]]] -->

```man
Usage: argos server test-mail [OPTIONS]

  Send a test email

Options:
  --config TEXT    Path of the configuration file. If ARGOS_YAML_FILE
                   environment variable is set, its value will be used instead.
  --domain TEXT    Domain for the notification
  --severity TEXT  Severity
  --help           Show this message and exit.
```

<!--[[[end]]]
-->

### Test the Gotify settings

You can verify that your Gotify settings are ok by sending a test notification.

<!--
.. [[[cog
    help(["server", "test-gotify", "--help"])
.. ]]] -->

```man
Usage: argos server test-gotify [OPTIONS]

  Send a test gotify notification

Options:
  --config TEXT    Path of the configuration file. If ARGOS_YAML_FILE
                   environment variable is set, its value will be used instead.
  --domain TEXT    Domain for the notification
  --severity TEXT  Severity
  --help           Show this message and exit.
```

<!--[[[end]]]
-->

### Test the Apprise settings

You can verify that your Apprise settings are ok by sending a test notification.

<!--
.. [[[cog
    help(["server", "test-apprise", "--help"])
.. ]]] -->

```man
Usage: argos server test-apprise [OPTIONS]

  Send a test apprise notification

Options:
  --config TEXT         Path of the configuration file. If ARGOS_YAML_FILE
                        environment variable is set, its value will be used
                        instead.
  --domain TEXT         Domain for the notification
  --severity TEXT       Severity
  --apprise-group TEXT  Apprise group for the notification  [required]
  --help                Show this message and exit.
```

<!--[[[end]]]
-->
