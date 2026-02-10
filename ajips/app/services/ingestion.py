from __future__ import annotations

from typing import Optional

import ipaddress
import urllib.parse
import requests
from bs4 import BeautifulSoup


# Allowed schemes and top-level domains for simple allowlist
ALLOWED_SCHEMES = {"http", "https"}
# Example: restrict to common job sites; expand as needed
ALLOWED_NETLOCS = {
    "linkedin.com",
    "indeed.com",
    "glassdoor.com",
    "monster.com",
    "ziprecruiter.com",
    "careerbuilder.com",
    "jobs.eu.lever.co",
    "boards.greenhouse.io",
    "jobs.github.com",
    "wellfound.com",
}


def _is_safe_url(url: str) -> bool:
    """Validate URL scheme, hostname, and prevent SSRF to private networks."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    # Disallow private and loopback IPs
    try:
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_link_local:
            return False
    except ValueError:
        pass  # Not an IP address; continue
    # Optional hostname allowlist
    if ALLOWED_NETLOCS and not any(
        hostname.endswith(netloc) for netloc in ALLOWED_NETLOCS
    ):
        # If allowlist is empty, allow any non-private hostname
        pass
    return True


def fetch_job_posting(url: str, timeout_s: int = 10) -> Optional[str]:
    """Fetch and extract plain text from a job posting URL with SSRF protection."""
    if not _is_safe_url(url):
        raise ValueError("URL is not allowed or is potentially unsafe")
    response = requests.get(url, timeout=timeout_s)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings)
    return text or None
