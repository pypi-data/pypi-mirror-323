import ssl
import smtplib
from email.message import EmailMessage

from typing import List
from urllib.parse import urlparse

import apprise
import httpx

from argos.checks.base import Severity
from argos.logging import logger
from argos.schemas.config import Config, Mail, GotifyUrl
from argos.server.models import Task


def need_alert(
    last_severity: str, last_severity_update, severity: str, status: str, task: Task
) -> bool:
    ## Create alert… or not!
    send_notif = False
    # Severity has changed, and no retry before notification
    if last_severity != severity and task.retry_before_notification == 0:
        send_notif = True
    # Seems to be a first check: create a notification
    elif last_severity != severity and last_severity_update is None:
        send_notif = True
        # As we created a notification, avoid resending it on a
        # future failure
        if status != "success":
            task.contiguous_failures = task.retry_before_notification
    # We need retry before notification, so the severity may not have changed
    # since last check
    elif task.retry_before_notification != 0:
        # If we got a success, and we already have created a notification:
        # create notification of success immediately
        if (
            status == "success"
            and task.contiguous_failures >= task.retry_before_notification + 1
        ):
            send_notif = True
            task.contiguous_failures = 0
        # The status is not a success
        elif status != "success":
            # This is a new failure
            task.contiguous_failures += 1
            # Severity has changed, but not to success, that’s odd:
            # create a notification
            if (
                last_severity not in ("ok", severity)
                and last_severity_update is not None
            ):
                send_notif = True
                # As we created a notification, avoid resending it on a
                # future failure
                task.contiguous_failures = task.retry_before_notification
            # Severity has not changed, but there has been enough failures
            # to create a notification
            elif task.contiguous_failures == task.retry_before_notification + 1:
                send_notif = True

    return send_notif


def get_icon_from_severity(severity: str) -> str:
    icon = "❌"
    if severity == Severity.OK:
        icon = "✅"
    elif severity == Severity.WARNING:
        icon = "⚠️"
    elif severity == Severity.UNKNOWN:
        icon = "❔"

    return icon


def handle_alert(config: Config, result, task, severity, old_severity, request):  # pylint: disable-msg=too-many-positional-arguments
    """Dispatch alert through configured alert channels"""

    if "local" in getattr(config.general.alerts, severity):
        logger.error(
            "Alerting stub: task=%i, status=%s, severity=%s",
            task.id,
            result.status,
            severity,
        )

    if config.general.mail is not None and "mail" in getattr(
        config.general.alerts, severity
    ):
        notify_by_mail(
            result, task, severity, old_severity, config.general.mail, request
        )

    if config.general.gotify is not None and "gotify" in getattr(
        config.general.alerts, severity
    ):
        notify_with_gotify(
            result, task, severity, old_severity, config.general.gotify, request
        )

    if config.general.apprise is not None:
        for notif_way in getattr(config.general.alerts, severity):
            if notif_way.startswith("apprise:"):
                group = notif_way[8:]
                notify_with_apprise(
                    result,
                    task,
                    severity,
                    old_severity,
                    config.general.apprise[group],
                    request,
                )


def notify_with_apprise(  # pylint: disable-msg=too-many-positional-arguments
    result, task, severity: str, old_severity: str, group: List[str], request
) -> None:
    logger.debug("Will send apprise notification")

    apobj = apprise.Apprise()
    for channel in group:
        apobj.add(channel)

    icon = get_icon_from_severity(severity)
    title = f"[Argos] {icon} {urlparse(task.url).netloc} (IPv{task.ip_version}): status {severity}"
    msg = f"""\
URL:    {task.url} (IPv{task.ip_version})
Check:  {task.check}
Status: {severity}
Time:   {result.submitted_at}
Previous status: {old_severity}

See result on {request.url_for('get_result_view', result_id=result.id)}

See results of task on {request.url_for('get_task_results_view', task_id=task.id)}#{result.id}
"""

    apobj.notify(title=title, body=msg)


def notify_by_mail(  # pylint: disable-msg=too-many-positional-arguments
    result, task, severity: str, old_severity: str, config: Mail, request
) -> None:
    logger.debug("Will send mail notification")

    icon = get_icon_from_severity(severity)
    msg = f"""\
URL:    {task.url} (IPv{task.ip_version})
Check:  {task.check}
Status: {severity}
Time:   {result.submitted_at}
Previous status: {old_severity}

See result on {request.url_for('get_result_view', result_id=result.id)}

See results of task on {request.url_for('get_task_results_view', task_id=task.id)}#{result.id}
"""

    mail = EmailMessage()
    mail[
        "Subject"
    ] = f"[Argos] {icon} {urlparse(task.url).netloc} (IPv{task.ip_version}): status {severity}"
    mail["From"] = config.mailfrom
    mail.set_content(msg)

    if config.ssl:
        logger.debug("Mail notification: SSL")
        context = ssl.create_default_context()
        smtp = smtplib.SMTP_SSL(host=config.host, port=config.port, context=context)
    else:
        smtp = smtplib.SMTP(
            host=config.host,  # type: ignore
            port=config.port,
        )
        if config.starttls:
            logger.debug("Mail notification: STARTTLS")
            context = ssl.create_default_context()
            smtp.starttls(context=context)

    if config.auth is not None:
        logger.debug("Mail notification: authentification")
        smtp.login(config.auth.login, config.auth.password)

    for address in config.addresses:
        logger.debug("Sending mail to %s", address)
        logger.debug(msg)
        smtp.send_message(mail, to_addrs=address)


def notify_with_gotify(  # pylint: disable-msg=too-many-positional-arguments
    result, task, severity: str, old_severity: str, config: List[GotifyUrl], request
) -> None:
    logger.debug("Will send gotify notification")
    headers = {"accept": "application/json", "content-type": "application/json"}

    icon = get_icon_from_severity(severity)
    priority = 9
    if severity == Severity.OK:
        priority = 1
    elif severity == Severity.WARNING:
        priority = 5
    elif severity == Severity.UNKNOWN:
        priority = 5

    subject = (
        f"{icon} {urlparse(task.url).netloc} (IPv{task.ip_version}): status {severity}"
    )
    msg = f"""\
URL:    <{task.url}> (IPv{task.ip_version})\\
Check:  {task.check}\\
Status: {severity}\\
Time:   {result.submitted_at}\\
Previous status: {old_severity}\\
\\
See result on <{request.url_for('get_result_view', result_id=result.id)}>\\
\\
See results of task on <{request.url_for('get_task_results_view', task_id=task.id)}#{result.id}>
"""
    extras = {
        "client::display": {"contentType": "text/markdown"},
        "client::notification": {
            "click": {
                "url": f"{request.url_for('get_result_view', result_id=result.id)}"
            }
        },
    }

    payload = {"title": subject, "message": msg, "priority": priority, "extras": extras}

    for url in config:
        logger.debug("Sending gotify message(s) to %s", url.url)
        for token in url.tokens:
            try:
                res = httpx.post(
                    f"{url.url}message",
                    params={"token": token},
                    headers=headers,
                    json=payload,
                )
                res.raise_for_status()
            except httpx.RequestError as err:
                logger.error(
                    "An error occurred while sending a message to %s with token %s",
                    err.request.url,
                    token,
                )
