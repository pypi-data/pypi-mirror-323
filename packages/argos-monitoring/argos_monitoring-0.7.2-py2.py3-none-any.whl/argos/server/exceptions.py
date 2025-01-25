from fastapi import Request
from fastapi.responses import RedirectResponse


class NotAuthenticatedException(Exception):
    pass


def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    response = RedirectResponse(url=request.url_for("login_view"))
    manager = request.app.state.manager
    manager.set_cookie(response, "")
    return response
