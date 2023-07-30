from enum import Enum

from pydantic import BaseModel


class ResponseType(str, Enum):
    code = "code"
    token = "token"


class GrantType(str, Enum):
    refresh_token = "refresh_token"
    token = "token"
    client_credentials = "client_credentials"
    password = "password"
    authorization_code = "authorization_code"


class AuthorizeModel(BaseModel):
    client_id: int
    state: str
    redirect_uri: str
    scope: str
    response_type: ResponseType


class ResolveGrantModel(BaseModel):
    client_id: int
    client_secret: str
    grant_type: GrantType = GrantType.authorization_code

    # Grant type specific.
    code: str | None = None
    redirect_uri: str | None = None
    refresh_token: str | None = None


class AllowClientModel(BaseModel):
    client_id: int
    state: str
    redirect_uri: str
    scope: str
    response_type: ResponseType
