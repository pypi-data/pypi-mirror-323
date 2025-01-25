"""Define the available checks"""

import json
import re
from datetime import datetime

from httpx import Response
from jsonpointer import resolve_pointer, JsonPointerException

from argos.checks.base import (
    BaseCheck,
    ExpectedIntValue,
    ExpectedStringValue,
    Severity,
    Status,
)


class HTTPStatus(BaseCheck):
    """Checks that the HTTP status code is the expected one."""

    config = "status-is"
    expected_cls = ExpectedIntValue

    async def run(self, response: Response) -> dict:
        return self.response(
            status=response.status_code == self.expected,
            expected=self.expected,
            retrieved=response.status_code,
        )


class HTTPStatusIn(BaseCheck):
    """Checks that the HTTP status code is in the list of expected values."""

    config = "status-in"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        return self.response(
            status=response.status_code in json.loads(self.expected),
            expected=self.expected,
            retrieved=response.status_code,
        )


class HTTPToHTTPS(BaseCheck):
    """Checks that the HTTP to HTTPS redirection status code is the expected one."""

    config = "http-to-https"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        expected_dict = json.loads(self.expected)
        expected = range(300, 400)
        if "range" in expected_dict:
            expected = range(expected_dict["range"][0], expected_dict["range"][1])
        if "value" in expected_dict:
            expected = range(expected_dict["value"], expected_dict["value"] + 1)
        if "list" in expected_dict:
            expected = expected_dict["list"]

        return self.response(
            status=response.status_code in expected,
            expected=self.expected,
            retrieved=response.status_code,
        )


class HTTPHeadersContain(BaseCheck):
    """Checks that response headers contains the expected headers
    (without checking their values)"""

    config = "headers-contain"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        status = True
        for header in json.loads(self.expected):
            if header not in response.headers:
                status = False
                break

        return self.response(
            status=status,
            expected=self.expected,
            retrieved=json.dumps(list(dict(response.headers).keys())),
        )


class HTTPHeadersHave(BaseCheck):
    """Checks that response headers contains the expected headers and values"""

    config = "headers-have"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        status = True
        for header, value in json.loads(self.expected).items():
            if header not in response.headers:
                status = False
                break
            if response.headers[header] != value:
                status = False
                break

        return self.response(
            status=status,
            expected=self.expected,
            retrieved=json.dumps(dict(response.headers)),
        )


class HTTPHeadersLike(BaseCheck):
    """Checks that response headers contains the expected headers and that the values
    matches the provided regexes"""

    config = "headers-like"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        status = True
        for header, value in json.loads(self.expected).items():
            if header not in response.headers:
                status = False
                break
            if not re.search(rf"{value}", response.headers[header]):
                status = False
                break

        return self.response(
            status=status,
            expected=self.expected,
            retrieved=json.dumps(dict(response.headers)),
        )


class HTTPBodyContains(BaseCheck):
    """Checks that the HTTP body contains the expected string."""

    config = "body-contains"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        return self.response(status=self.expected in response.text)


class HTTPBodyLike(BaseCheck):
    """Checks that the HTTP body matches the provided regex."""

    config = "body-like"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        if re.search(rf"{self.expected}", response.text):
            return self.response(status=True)

        return self.response(status=False)


class HTTPJsonContains(BaseCheck):
    """Checks that JSON response contains the expected structure
    (without checking the value)"""

    config = "json-contains"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        obj = response.json()

        status = True
        for pointer in json.loads(self.expected):
            try:
                resolve_pointer(obj, pointer)
            except JsonPointerException:
                status = False
                break

        return self.response(
            status=status,
            expected=self.expected,
            retrieved=json.dumps(obj),
        )


class HTTPJsonHas(BaseCheck):
    """Checks that JSON response contains the expected structure and values"""

    config = "json-has"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        obj = response.json()

        status = True
        for pointer, exp_value in json.loads(self.expected).items():
            try:
                value = resolve_pointer(obj, pointer)
                if value != exp_value:
                    status = False
                    break
            except JsonPointerException:
                status = False
                break

        return self.response(
            status=status,
            expected=self.expected,
            retrieved=json.dumps(obj),
        )


class HTTPJsonLike(BaseCheck):
    """Checks that JSON response contains the expected structure and that the values
    matches the provided regexes"""

    config = "json-like"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        obj = response.json()

        status = True
        for pointer, exp_value in json.loads(self.expected).items():
            try:
                value = resolve_pointer(obj, pointer)
                if not re.search(rf"{exp_value:}", value):
                    status = False
                    break
            except JsonPointerException:
                status = False
                break

        return self.response(
            status=status,
            expected=self.expected,
            retrieved=json.dumps(obj),
        )


class HTTPJsonIs(BaseCheck):
    """Checks that JSON response is the exact expected JSON object"""

    config = "json-is"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        obj = response.json()

        status = response.json() == json.loads(self.expected)

        return self.response(
            status=status,
            expected=self.expected,
            retrieved=json.dumps(obj),
        )


class SSLCertificateExpiration(BaseCheck):
    """Checks that the SSL certificate will not expire soon."""

    config = "ssl-certificate-expiration"
    expected_cls = ExpectedStringValue

    async def run(self, response: Response) -> dict:
        """Returns the number of days in which the certificate will expire."""
        network_stream = response.extensions["network_stream"]
        ssl_obj = network_stream.get_extra_info("ssl_object")
        cert = ssl_obj.getpeercert()

        not_after = datetime.strptime(cert.get("notAfter"), "%b %d %H:%M:%S %Y %Z")
        expires_in = (not_after - datetime.now()).days

        return self.response(status=Status.ON_CHECK, expires_in=expires_in)

    @classmethod
    async def finalize(cls, config, result, **context):
        if result.status == Status.ERROR:
            return result.status, Severity.UNKNOWN
        if result.status != Status.ON_CHECK:
            return result.status, Severity.WARNING

        if "expires_in" in context:
            thresholds = config.ssl.thresholds
            thresholds.sort()
            for days, severity in thresholds:
                if context["expires_in"] < days:
                    return Status.FAILURE, severity
            return Status.SUCCESS, Severity.OK

        raise ValueError(
            "The SSLCertificateExpiration check didn't provide an 'expires_in' "
            "context variable."
        )

    @classmethod
    def get_description(cls, config):
        thresholds = config.ssl.thresholds
        thresholds.sort()
        string = SSLCertificateExpiration.__doc__ + "\n"
        for days, severity in thresholds:
            string += f"- {severity} if expiration in less than {days} days\n"
        return string
