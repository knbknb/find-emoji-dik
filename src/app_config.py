from typing import Optional, cast
from pydantic import BaseModel, HttpUrl, model_validator

class AppConfig(BaseModel):
    # Files and user
    file_path: str = "./data/moby-dick-lowercase.txt"
    toot_storage_file: str = "data/toot_storage.json"
    user: str = "@mobydick@mastodon.art"

    # Mastodon
    mastodon_instance_url: HttpUrl = cast(HttpUrl, "https://social.vivaldi.net")
    mastodon_client_id: Optional[str] = None
    mastodon_client_secret: Optional[str] = None
    mastodon_access_token: Optional[str] = None

    # OpenAI
    openai_access_token: Optional[str] = None
    openai_model: str = "gpt-4o"
    translate_service_url: HttpUrl = cast(HttpUrl, "https://api.openai.com/v1/chat/completions")

    # Behavior
    n_words: int = 4
    toot: Optional[str] = None
    data_file: Optional[str] = None
    signature: Optional[str] = None
    dry_run: bool = False

    @model_validator(mode='before')
    @classmethod
    def require_mastodon_credentials_for_posting(cls, values):
        dry_run = values.get("dry_run", False)
        if not dry_run:
            missing = [
                name for name in ("mastodon_client_id", "mastodon_client_secret", "mastodon_access_token")
                if not values.get(name)
            ]
            if missing:
                raise ValueError(f"Mastodon credentials missing while dry_run is False: {', '.join(missing)}")
        return values
