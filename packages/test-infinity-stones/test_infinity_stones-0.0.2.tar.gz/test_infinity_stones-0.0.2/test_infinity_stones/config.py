from pydantic import BaseModel


class Settings(BaseModel):
    AUTH_SERVICE_BASE_URL: str
    AUTHENTICATE_USER_ENDPOINT_PATH: str

    class ConfigDict:
        case_sensitive = True
