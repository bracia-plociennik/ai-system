"""Private advisory style history. Integrity declarations are not owner authority.

The coordinator verifies exact-target owner consent and semantic privacy before
calling apply. This module never authenticates a chat, actor or approval string.
"""
import argparse
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

SCHEMA = 1
KEYS = {"language", "verbosity", "response-format", "vocabulary", "tone"}
ACTIONS = {"init", "enable", "disable", "correction", "observation", "confirm", "disable-preference"}
SOURCE_KINDS = {"owner-correction", "owner-preference", "marked-observation"}
EVENT_FIELDS = {"revision", "timestamp", "actor", "source", "approval", "action", "key", "value", "previous", "sha256"}
REQUEST_FIELDS = {"action", "actor", "source", "approval", "key", "value"}
HEX = re.compile(r"[0-9a-f]{64}\Z")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class InvalidProfile(ValueError):
    pass


def require(value, message):
    if not value:
        raise InvalidProfile(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON field")
        result[key] = value
    return result


def load_json(text):
    try:
        return json.loads(text, object_pairs_hook=unique)
    except (json.JSONDecodeError, TypeError) as error:
        raise InvalidProfile("invalid JSON") from error


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def reference(value):
    require(isinstance(value, str) and len(value) <= 240, "invalid source reference")
    if re.fullmatch(r"conversation:[a-zA-Z0-9-]{1,100}", value):
        return
    require(re.fullmatch(r"(?:decisions|style-feedback)/[a-z0-9/-]+\.md", value)
            and ".." not in value and "//" not in value, "unsafe source reference")


def evidence(value, kinds):
    require(isinstance(value, dict) and set(value) == {"kind", "reference", "sha256"}, "invalid provenance")
    require(value["kind"] in kinds, "invalid provenance kind")
    reference(value["reference"])
    require(isinstance(value["sha256"], str) and HEX.fullmatch(value["sha256"]), "invalid evidence digest")


def request(value):
    require(isinstance(value, dict) and set(value) == REQUEST_FIELDS, "invalid request fields")
    require(value["action"] in ACTIONS, "unknown action")
    require(value["actor"] in {"owner", "agent"}, "unknown actor")
    evidence(value["source"], SOURCE_KINDS)
    evidence(value["approval"], {"owner-profile-opt-in"})
    if value["action"] == "observation":
        require(value["actor"] == "agent" and value["source"]["kind"] == "marked-observation", "observation must be marked agent provenance")
    else:
        require(value["actor"] == "owner" and value["source"]["kind"] in {"owner-correction", "owner-preference"}, "explicit owner provenance required")
    if value["action"] in {"correction", "observation", "confirm"}:
        require(value["key"] in KEYS, "unsupported style key")
        text = value["value"]
        require(isinstance(text, str) and 0 < len(text) <= 160 and text == text.strip()
                and all(ord(c) >= 32 for c in text), "invalid minimized style value")
        require(not re.search(r"(?i)(?:https?://|@|-----BEGIN|\b(?:password|token|secret|api[_ -]?key|client|customer)\s*[:=]|\bsk-[a-z0-9]{12,})", text), "sensitive style value")
    elif value["action"] == "disable-preference":
        require(value["key"] in KEYS and value["value"] is None, "invalid disable preference")
    else:
        require(value["key"] is None and value["value"] is None, "unexpected style value")


def replay(events):
    enabled = False
    preferences = {}
    for i, event in enumerate(events):
        action, key = event["action"], event["key"]
        require((i == 0) == (action == "init"), "init must be first and unique")
        if action in {"enable", "disable"}:
            enabled = action == "enable"
        elif action in {"correction", "observation", "confirm", "disable-preference"}:
            require(enabled, "profile disabled; feedback recording prohibited")
            if action == "disable-preference":
                require(key in preferences, "unknown preference")
                preferences.pop(key)
            elif action == "observation" and key in preferences and preferences[key]["disposition"] == "confirmed":
                pass  # Event is retained, but does not replace confirmed owner context.
            else:
                if action == "confirm":
                    require(key in preferences and preferences[key]["disposition"] == "tentative"
                            and event["value"] == preferences[key]["value"], "confirmation requires current matching tentative value")
                preferences[key] = {"value": event["value"], "disposition": "tentative" if action == "observation" else "confirmed",
                                    "source": event["source"], "revision": event["revision"]}
    return enabled, preferences


def validate(profile, scope):
    require(isinstance(profile, dict) and set(profile) == {"schema", "scope", "revision", "events"}, "invalid profile fields")
    require(type(profile["schema"]) is int and profile["schema"] == SCHEMA, "unsupported profile schema")
    require(profile["scope"] == scope and isinstance(scope, str) and SLUG.fullmatch(scope), "foreign or invalid scope")
    events = profile["events"]
    require(isinstance(events, list) and events and type(profile["revision"]) is int
            and profile["revision"] == len(events), "invalid profile revision")
    previous = "0" * 64
    for i, event in enumerate(events, 1):
        require(isinstance(event, dict) and set(event) == EVENT_FIELDS, "invalid event fields")
        require(type(event["revision"]) is int and event["revision"] == i and event["previous"] == previous, "invalid history chain")
        require(isinstance(event["timestamp"], str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", event["timestamp"]), "invalid event timestamp")
        try:
            datetime.strptime(event["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as error:
            raise InvalidProfile("invalid event timestamp") from error
        request({key: event[key] for key in REQUEST_FIELDS})
        require(event["sha256"] == digest({key: value for key, value in event.items() if key != "sha256"}), "corrupted history digest")
        previous = event["sha256"]
    replay(events)
    return profile


def projection(profile, scope):
    validate(profile, scope)
    enabled, prefs = replay(profile["events"])
    return {"schema": SCHEMA, "scope": scope, "profile_revision": profile["revision"],
            "profile_sha256": digest(profile), "enabled": enabled, "authority": "advisory-data-only",
            "preferences": {key: value for key, value in prefs.items() if enabled and value["disposition"] == "confirmed"},
            "tentative_keys": sorted(key for key, value in prefs.items() if enabled and value["disposition"] == "tentative")}


def transition(profile, scope, expected_revision, change):
    require(type(expected_revision) is int and expected_revision >= 0, "invalid expected revision")
    request(change)
    if profile is None:
        require(expected_revision == 0 and change["action"] == "init", "missing profile; initialize explicitly")
        result = {"schema": SCHEMA, "scope": scope, "revision": 0, "events": []}
    else:
        validate(profile, scope)
        require(profile["revision"] == expected_revision, "stale expected revision")
        result = copy.deepcopy(profile)
    event = {**copy.deepcopy(change), "revision": result["revision"] + 1,
             "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "previous": result["events"][-1]["sha256"] if result["events"] else "0" * 64}
    event["sha256"] = digest(event)
    result["revision"] += 1
    result["events"].append(event)
    return validate(result, scope)


def safe_path(root, relative):
    root = Path(root)
    require(root.is_absolute() and root.exists() and root.is_dir(), "selected absolute runtime root required")
    require(isinstance(relative, str) and "\\" not in relative and not relative.startswith("/")
            and all(part not in {"", ".", "..", ".systems", ".git", "secrets", "credentials"} for part in relative.split("/")), "unsafe profile path")
    slug = r"[a-z0-9]+(?:-[a-z0-9]+)*"
    owners = (r"project-state/" + slug, r"clients/" + slug, r"clients/" + slug + r"/project-state/" + slug,
              r"owned-assets/" + slug, r"owned-assets/" + slug + r"/project-state/" + slug)
    require(relative == "memory/style-profile-v1.json" or any(
        re.fullmatch(owner + r"/memory/style-profile-v1\.json", relative) for owner in owners), "noncanonical profile path")
    require(not any(p.is_symlink() for p in [root, *root.parents]), "linked runtime root")
    path = root / relative
    require(not any(p.is_symlink() for p in [path, *path.parents]), "linked profile path")
    if path.exists():
        require(path.is_file() and path.stat().st_nlink == 1, "nonregular or multiply-linked profile")
    return path


def read(root, relative, scope):
    path = safe_path(root, relative)
    require(path.exists(), "profile missing")
    return validate(load_json(path.read_text()), scope)


def apply(root, relative, scope, expected_revision, change):
    """Apply a coordinator-approved request; declared evidence is not authority."""
    path = safe_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    require(path.parent.stat().st_mode & 0o077 == 0, "profile directory must be private (0700)")
    lock = path.with_suffix(".lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        require(stat.S_ISREG(os.fstat(descriptor).st_mode) and os.fstat(descriptor).st_nlink == 1, "unsafe profile lock")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        safe_path(root, relative)
        current = read(root, relative, scope) if path.exists() else None
        result = transition(current, scope, expected_revision, change)
        fd, temp = tempfile.mkstemp(prefix=".style-profile-", dir=path.parent)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
        return result
    finally:
        os.close(descriptor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["inspect", "project", "prepare", "apply"])
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--request")
    parser.add_argument("--expected-revision", type=int)
    args = parser.parse_args()
    try:
        if args.action in {"prepare", "apply"}:
            require(args.request is not None and args.expected_revision is not None, "request and expected revision required")
            change = load_json(Path(args.request).read_text())
            if args.action == "apply":
                result = apply(args.workspace, args.path, args.scope, args.expected_revision, change)
            else:
                path = safe_path(args.workspace, args.path)
                current = read(args.workspace, args.path, args.scope) if path.exists() else None
                result = transition(current, args.scope, args.expected_revision, change)
        else:
            result = read(args.workspace, args.path, args.scope)
        if args.action == "project":
            result = projection(result, args.scope)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    except (InvalidProfile, OSError, TypeError) as error:
        parser.exit(1, "Style profile rejected: " + str(error) + "\n")


if __name__ == "__main__":
    main()
