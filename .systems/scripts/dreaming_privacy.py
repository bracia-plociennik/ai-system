"""Conservative lexical screening, never a substitute for human identity review."""
import json
import ipaddress
import re
import unicodedata
from urllib.parse import unquote, urlsplit
from dreaming_provider_v1 import require

SECRET = re.compile(r"(?i)(?:-----BEGIN .*PRIVATE KEY|\b(?:api[_-]?key|password|secret|access[_-]?token)\s*[:=]|\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{12,}))")
LOCAL = re.compile(r"(?i)(?:file\s*:|(?:^|[\s\"'=(])/(?:[A-Za-z0-9_.~-]+/)+[A-Za-z0-9_.~-]*|(?:^|[\s\"'=(])/(?:home|srv|Users|private|tmp|etc|var|opt|mnt|root|Volumes)(?:/|\b)|\b[A-Z]:[\\/]|\\\\[^\s]+|%[25]?[0-9a-f]{2})")
IDENTIFIER = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")

def normalized(value):
    text = unicodedata.normalize("NFKC", value)
    for _ in range(4):
        newer = unquote(text).replace("\\/", "/")
        newer = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m[1],16)), newer)
        if newer == text: break
        text = newer
    return text

def clean_text(value, *, identifiers=False):
    require(isinstance(value,str), "invalid-shareable-text")
    text=normalized(value)
    # Public HTTP URLs may contain slashes, but no credentials, localhost or local file URL.
    def url(match):
        parsed=urlsplit(match[0])
        host=(parsed.hostname or '').lower().rstrip('.')
        require(host and not parsed.username and not parsed.password and host not in {"localhost","localhost.localdomain"}
                and not host.endswith(('.local','.localhost','.internal')), "private-url")
        try:address=ipaddress.ip_address(host)
        except ValueError:pass
        else:require(address.is_global,"private-url")
        require(not re.search(r"(?i)/(?:home|srv|Users|private|tmp|etc|var|opt|mnt|root|Volumes)(?:/|\b)|\b[A-Z]:[\\/]|file:",match[0]),"private-url-path")
        return "public-url"
    screened=re.sub(r"https?://[^\s<>\"']+",url,text)
    require(not re.search(r"(?i)/(?:home|srv|Users|private|tmp|etc|var|opt|mnt|root|Volumes)(?:/|\b)|[A-Za-z]:[\\/]|(?<![A-Za-z0-9])/(?:[A-Za-z0-9_.~-]+/)+[A-Za-z0-9_.~-]*",screened),"private-path")
    require(not SECRET.search(text), "suspected-secret")
    require(not LOCAL.search(screened), "private-path")
    require(not identifiers or not IDENTIFIER.search(text), "identity-review-required")
    return value

def clean_projection(value):
    """Screen all keys and values, including pending/nested translation metadata."""
    if isinstance(value,str): clean_text(value,identifiers=True)
    elif isinstance(value,dict):
        for key,item in value.items(): clean_text(key,identifiers=True); clean_projection(item)
    elif isinstance(value,list):
        for item in value: clean_projection(item)
    else: require(value is None or type(value) in {int,bool}, "invalid-projection-value")
    return value
