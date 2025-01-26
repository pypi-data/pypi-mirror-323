"""Pydantic schemas for configuration

For database models, see argos.server.models.
"""

import json

from typing import Any, Dict, List, Literal, Tuple

from durations_nlp import Duration
from pydantic import (
    BaseModel,
    ConfigDict,
    HttpUrl,
    PostgresDsn,
    StrictBool,
    EmailStr,
    PositiveInt,
    field_validator,
)
from pydantic.functional_validators import AfterValidator, BeforeValidator
from pydantic.networks import UrlConstraints
from pydantic_core import Url
from typing_extensions import Annotated

from argos.schemas.utils import Method

Severity = Literal["warning", "error", "critical", "unknown"]
Environment = Literal["dev", "test", "production"]
Unauthenticated = Literal["dashboard", "all"]
SQLiteDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=["sqlite"],
    ),
]


def parse_threshold(value):
    """Parse duration threshold for SSL certificate validity"""
    for duration_str, severity in value.items():
        days = Duration(duration_str).to_days()
        # Return here because it's one-item dicts.
        return (days, severity)


class SSL(BaseModel):
    thresholds: List[Annotated[Tuple[int, Severity], BeforeValidator(parse_threshold)]]


class WebsiteCheck(BaseModel):
    key: str
    value: str | List[str] | Dict[str, str]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if isinstance(value, str):
            return {"expected": value}
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            return {"expected": value}

        raise ValueError("Invalid type")


def parse_checks(value):
    """Check that checks are valid (i.e. registered) checks"""

    # To avoid circular imports
    from argos.checks import get_registered_checks

    available_names = get_registered_checks().keys()

    for name, expected in value.items():
        if name not in available_names:
            msg = f"Check should be one of f{available_names}. ({name} given)"
            raise ValueError(msg)
        if name == "http-to-https":
            if isinstance(expected, int) and expected in range(300, 400):
                expected = json.dumps({"value": expected})
            elif isinstance(expected, list):
                expected = json.dumps({"list": expected})
            elif (
                isinstance(expected, dict)
                and "start" in expected
                and "stop" in expected
            ):
                expected = json.dumps({"range": [expected["start"], expected["stop"]]})
            else:
                expected = json.dumps({"range": [300, 400]})
        else:
            if isinstance(expected, int):
                expected = str(expected)
            if isinstance(expected, list):
                expected = json.dumps(expected)
            if isinstance(expected, dict):
                expected = json.dumps(expected)
        return (name, expected)


def parse_request_data(value):
    """Turn form or JSON data into JSON string"""

    return json.dumps(
        {"data": value.data, "json": value.is_json, "headers": value.headers}
    )


class RequestData(BaseModel):
    data: Any = None
    is_json: bool = False
    headers: Dict[str, str] | None = None


class WebsitePath(BaseModel):
    path: str
    method: Method = "GET"
    request_data: Annotated[
        RequestData, AfterValidator(parse_request_data)
    ] | None = None
    checks: List[
        Annotated[
            Tuple[str, str],
            BeforeValidator(parse_checks),
        ]
    ]


class Website(BaseModel):
    domain: HttpUrl
    ipv4: bool | None = None
    ipv6: bool | None = None
    frequency: float | None = None
    recheck_delay: float | None = None
    retry_before_notification: int | None = None
    paths: List[WebsitePath]

    @field_validator("frequency", mode="before")
    def parse_frequency(cls, value):
        """Convert the configured frequency to minutes"""
        if value:
            return Duration(value).to_minutes()

        return None

    @field_validator("recheck_delay", mode="before")
    def parse_recheck_delay(cls, value):
        """Convert the configured recheck delay to minutes"""
        if value:
            return Duration(value).to_minutes()

        return None


class Service(BaseModel):
    """List of agents’ token"""

    secrets: List[str]


class MailAuth(BaseModel):
    """Mail authentication configuration"""

    login: str
    password: str


class Mail(BaseModel):
    """Mail configuration"""

    mailfrom: EmailStr
    host: str = "127.0.0.1"
    port: PositiveInt = 25
    ssl: StrictBool = False
    starttls: StrictBool = False
    auth: MailAuth | None = None
    addresses: List[EmailStr]


class Alert(BaseModel):
    """List of way to handle alerts, by severity"""

    ok: List[str]
    warning: List[str]
    critical: List[str]
    unknown: List[str]


class GotifyUrl(BaseModel):
    url: HttpUrl
    tokens: List[str]


class DbSettings(BaseModel):
    url: PostgresDsn | SQLiteDsn
    pool_size: int = 10
    max_overflow: int = 20


class LdapSettings(BaseModel):
    uri: str
    user_tree: str
    bind_dn: str | None = None
    bind_pwd: str | None = None
    user_attr: str
    user_filter: str | None = None


class General(BaseModel):
    """Frequency for the checks and alerts"""

    db: DbSettings
    env: Environment = "production"
    cookie_secret: str
    session_duration: int = 10080  # 7 days
    remember_me_duration: int | None = None
    unauthenticated_access: Unauthenticated | None = None
    ldap: LdapSettings | None = None
    frequency: float
    recheck_delay: float | None = None
    retry_before_notification: int = 0
    ipv4: bool = True
    ipv6: bool = True
    root_path: str = ""
    alerts: Alert
    mail: Mail | None = None
    gotify: List[GotifyUrl] | None = None
    apprise: Dict[str, List[str]] | None = None

    @field_validator("session_duration", mode="before")
    def parse_session_duration(cls, value):
        """Convert the configured session duration to minutes"""
        return Duration(value).to_minutes()

    @field_validator("remember_me_duration", mode="before")
    def parse_remember_me_duration(cls, value):
        """Convert the configured session duration with remember me feature to minutes"""
        if value:
            return int(Duration(value).to_minutes())

        return None

    @field_validator("frequency", mode="before")
    def parse_frequency(cls, value):
        """Convert the configured frequency to minutes"""
        return Duration(value).to_minutes()

    @field_validator("recheck_delay", mode="before")
    def parse_recheck_delay(cls, value):
        """Convert the configured recheck delay to minutes"""
        if value:
            return Duration(value).to_minutes()

        return None


class Config(BaseModel):
    general: General
    service: Service
    ssl: SSL
    websites: List[Website]
