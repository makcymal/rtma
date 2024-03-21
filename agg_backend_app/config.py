from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "agg_backend_app" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "agg_backend_app" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_min: int = 15



class Settings(BaseModel):

    auth_jwt: AuthJWT = AuthJWT()


settings = Settings()