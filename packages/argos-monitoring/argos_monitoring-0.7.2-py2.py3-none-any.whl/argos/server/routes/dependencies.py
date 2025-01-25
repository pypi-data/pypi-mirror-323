from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_login import LoginManager

auth_scheme = HTTPBearer()


def get_db(request: Request):
    db = request.app.state.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_config(request: Request):
    return request.app.state.config


async def get_manager(request: Request) -> LoginManager:
    if request.app.state.config.general.unauthenticated_access is not None:
        return await request.app.state.manager.optional(request)

    return await request.app.state.manager(request)


async def verify_token(
    request: Request, token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    """Verify agent token"""
    if token.credentials not in request.app.state.config.service.secrets:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token


async def find_ldap_user(config, ldap, user: str) -> str | None:
    """Do a LDAP search for user and return its dn"""
    import ldap.filter as ldap_filter
    from ldapurl import LDAP_SCOPE_SUBTREE

    result = ldap.search_s(
        config.general.ldap.user_tree,
        LDAP_SCOPE_SUBTREE,
        filterstr=ldap_filter.filter_format(
            f"(&(%s=%s){config.general.ldap.user_filter})",
            [
                config.general.ldap.user_attr,
                user,
            ],
        ),
        attrlist=[config.general.ldap.user_attr],
    )

    # If there is a result, there should, logically, be only one entry
    if len(result) > 0:
        return result[0][0]

    return None
