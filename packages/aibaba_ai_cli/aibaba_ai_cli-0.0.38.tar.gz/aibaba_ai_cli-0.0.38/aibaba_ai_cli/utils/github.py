import http.client
import json
from typing import Optional


def list_packages(*, contains: Optional[str] = None):
    conn = http.client.HTTPSConnection("api.github.com")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "aibaba-ai-cli",
    }

    conn.request(
        "GET", "/repos/aibaba-ai/aibaba-ai/contents/templates", headers=headers
    )
    res = conn.getresponse()

    res_str = res.read()

    data = json.loads(res_str)
    package_names = [
        p["name"] for p in data if p["type"] == "dir" and p["name"] != "docs"
    ]
    package_names_filtered = (
        [p for p in package_names if contains in p] if contains else package_names
    )
    return package_names_filtered
