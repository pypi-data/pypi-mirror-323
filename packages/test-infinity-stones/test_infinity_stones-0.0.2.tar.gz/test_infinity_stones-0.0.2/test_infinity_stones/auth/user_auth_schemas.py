from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

class VerifiableAddress(BaseModel):
    id: str
    value: str
    verified: bool
    via: str
    status: str
    verified_at: datetime
    created_at: datetime
    updated_at: datetime

class Identity(BaseModel):
    id: str
    schema_id: str
    schema_url: str
    state: str
    state_changed_at: datetime
    traits: dict[str, str]
    verifiable_addresses: list[VerifiableAddress]
    metadata_public: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    organization_id: Optional[str]

class Device(BaseModel):
    id: str
    ip_address: str
    user_agent: str
    location: str

class AuthenticationMethod(BaseModel):
    method: str
    aal: str
    completed_at: datetime

class UserAuthResponse(BaseModel):
    id: str
    active: bool
    expires_at: datetime
    authenticated_at: datetime
    authenticator_assurance_level: str
    authentication_methods: list[AuthenticationMethod]
    issued_at: datetime
    identity: Identity
    devices: list[Device]