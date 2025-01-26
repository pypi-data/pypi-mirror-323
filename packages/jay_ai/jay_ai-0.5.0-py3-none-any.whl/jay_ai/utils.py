import os


def fetch_site_url():
    base_url = os.getenv("VERCEL_URL", "jay.so")
    if "http" not in base_url:
        if "localhost" in base_url:
            base_url = f"http://{base_url}"
        else:
            base_url = f"https://{base_url}"
    return base_url


def fetch_headers(api_key: str):
    api_protection_bypass_secret = os.getenv("VERCEL_AUTOMATION_BYPASS_SECRET")
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }
    if api_protection_bypass_secret:
        headers["x-vercel-protection-bypass"] = api_protection_bypass_secret
    return headers
