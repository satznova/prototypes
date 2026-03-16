from pydantic import BaseModel
from datetime import datetime

class LongUrl(BaseModel):
    long_url: str
    alias_code: str | None = None # Validates None as a valid input. If not provided, it defaults to None
    #alias_code: str = None # It may cause issues if you expect None to be a valid input value later
    expiration_date: datetime = None
