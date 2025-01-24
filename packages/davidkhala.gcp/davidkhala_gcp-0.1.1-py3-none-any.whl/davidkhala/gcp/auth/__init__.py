from dataclasses import dataclass
from typing import TypedDict, NotRequired, Optional


@dataclass
class ServiceAccountInfo(TypedDict):
    client_email: str
    private_key: str
    token_uri: NotRequired[str]
    project_id: NotRequired[str]


class CredentialsInterface:
    token: Optional[str]
    """
    The bearer token that can be used in HTTP headers to make authenticated requests.
    """


class OptionsInterface:
    credentials: CredentialsInterface
    """
    raw secret not cached in credentials object. You need cache it by yourself.
    """
    projectId: str
