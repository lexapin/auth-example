from fastapi import Request, HTTPException
from fastapi_permissions import Allow, Deny, Authenticated
from fastapi_permissions import configure_permissions


def get_active_principals(request: Request):
    user = getattr(request.state, "user", None)
    if user:
        # user is logged in
        principals = [Authenticated]
        principals.extend(getattr(user, "principals", []))
    else:
        # user is not logged in
        principals = [Deny]
    return principals


class AccessDeniedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403,)


Permission = configure_permissions(get_active_principals, AccessDeniedException)