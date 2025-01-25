---
description: Here are the checks that Argos proposes, with a description of what they do and how to configure them.
---
# Checks

At its core, Argos runs checks and return the results to the service. Here are the implemented checks, with a description of what they do and how to configure them.

## Simple checks

These checks are the most basic ones. They simply check that the response from the service matches what you expect.

| Check | Description | Configuration |
| --- | --- | --- |
| `status-is` | Check that the returned status code matches what you expect. | <pre><code>status-is: \"200\"</code></pre> |
| `status-in` | Check that the returned status code is in the list of codes you expect. | <pre><code>status-in:<br>    - 200<br>    - 302</code></pre> |
| `body-contains` | Check that the returned body contains a given string. | <pre><code>body-contains: "Hello world"</code></pre> |
| `body-like` | Check that the returned body matches a given regex. | <pre><code>body-like: "Hel+o w.*"</code></pre> |
| `headers-contain` | Check that the response contains the expected headers. | <pre><code>headers-contain:<br>    - "content-encoding"<br>    - "content-type"</code></pre> |
| `headers-have` | Check that the response contains the expected headers with the expected value. | <pre><code>headers-have:<br>    content-encoding: "gzip"<br>    content-type: "text/html"</code></pre> |
| `headers-like` | Check that response headers contains the expected headers and that the values matches the provided regexes. | <pre><code>headers-like:<br>    content-encoding: "gzip\|utf"<br>    content-type: "text/(html\|css)"</code></pre> |
| `json-contains` | Check that JSON response contains the expected structure. | <pre><code>json-contains:<br>    - /foo/bar/0<br>    - /timestamp</code></pre> |
| `json-has` | Check that JSON response contains the expected structure and values. | <pre><code>json-has:<br>    /maintenance: false<br>    /productname: "Nextcloud"</code></pre> |
| `json-like` | Check that JSON response contains the expected structure and that the values matches the provided regexes. | <pre><code>json-like:<br>    /productname: ".\*cloud"<br>    /versionstring: "29\\\\..\*"</code></pre> |
| `json-is` | Check that JSON response is the exact expected JSON object. | <pre><code>json-is: '{"foo": "bar", "baz": 42}'</code></pre> |
| `http-to-https` | Check that the HTTP version of the domain redirects to HTTPS. Multiple choices of configuration. | <pre><code>http-to-https: true<br>http-to-https: 301<br>http-to-https:<br>    start: 301<br>    stop: 308<br>http-to-https:<br>    - 301<br>    - 302<br>    - 307</code></pre> |

```{code-block} yaml
---
caption: argos-config.yaml
---
- domain: "https://example.org"
  paths:
    - path: "/"
      checks:
        - status-is: 200
        - body-contains: "Hello world"
        - body-like: "Hel+o w.*"
        - headers-contain:
            - "content-encoding"
            - "content-type"
        # Check that there is a HTTP to HTTPS redirection with 3xx status code
        - http-to-https: true
        # Check that there is a HTTP to HTTPS redirection with 301 status code
        - http-to-https: 301
        # Check that there is a HTTP to HTTPS redirection with a status code
        # in the provided range (stop value excluded)
        - http-to-https:
            start: 301
            stop: 308
        # Check that there is a HTTP to HTTPS redirection with a status code
        # in the provided list
        - http-to-https:
            - 301
            - 302
            - 307
    - path: "/foobar"
      checks:
        - status-in:
            - 200
            - 302
        # It’s VERY important to respect the 4 spaces indentation here!
        - headers-have:
            content-encoding: "gzip"
            content-type: "text/html"
        # It’s VERY important to respect the 4 spaces indentation here!
        # You have to double the escape character \
        - headers-like:
            content-encoding: "gzip|utf"
            content-type: "text/(html|css)"
        - json-contains:
            - /foo/bar/0
            - /timestamp
        # It’s VERY important to respect the 4 spaces indentation here!
        - json-has:
            /maintenance: false
            /productname: "Nextcloud"
        # It’s VERY important to respect the 4 spaces indentation here!
        # You have to double the escape character \
        - json-like:
            /productname: ".*cloud"
            /versionstring: "29\\..*"
        - json-is: '{"foo": "bar", "baz": 42}'
```

## SSL certificate expiration

 Checks that the SSL certificate will not expire soon. You need to define the thresholds in the configuration, and set the `on-check` option to enable the check.


```{code-block} yaml
---
caption: argos-config.yaml
---
ssl:
  thresholds:
    - "1d": critical
    - "5d": warning

- domain: "https://example.org"
  paths:
    - path: "/"
      checks:
        - ssl-certificate-expiration: "on-check"
```
