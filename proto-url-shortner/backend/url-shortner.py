from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
import validators

from schemas import LongUrl

app = FastAPI(
    title="URL-Shortner",
    description="URL-Shortner",
    version="1.0.0",
    openapi_url=None # To disable the Docs (diables docs, redoc, openapi.json)
)

@app.post("/create_short_code")
def create_short_code(long_url: LongUrl):
    # 1. Check if URL is Valid
    if not validators.url(long_url.long_url):
        return{"status": "FAILED",
               "description": "{} is an INVALID_URL".format(long_url.long_url) ,
               "short_code": None}
    # 2. Check is Long URL already shortened. (Skipping this)
    # 3. Generate Short Code
    # 4. Insert into DataBase
    # 5. Return the Shortened URL to Client. (Note: The Shortened URL exists in a domain we own)
    return {"status": "SUCCESS",
            "description": "Short Code Generated" ,
            "short_code": "abc"}


@app.get("/{short_code}")
def get_long_url(short_code: str):
    # 1. Check is Short Code exists in DB
    # 2. Check if Short code not expired
    # 3 a. For Expired URL. HTTP 410 Gone : The requested resource No longer available
    # 3 b. For Valid URL. HTTP 302 (Redirect Found)
    return RedirectResponse(url="https://wired.com/", status_code=status.HTTP_302_FOUND)
    #return {"short_code": short_code}
