#!/usr/bin/env python3
"""Watch TCF Canada exam centres in Vancouver and send a push alert when
registration looks open (or the sessions page changes).

Run once:        python monitor.py
Run every 30m:   python monitor.py --loop 1800
Test alerts:     python monitor.py --test-notify

Notification channels (set as environment variables / GitHub secrets):
  NTFY_TOPIC                        -> push via https://ntfy.sh/<topic>
  TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID -> Telegram message
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config.yaml"
STATE_PATH = HERE / "state.json"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-CA,en;q=0.9,fr;q=0.8",
}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def load_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def fetch_text(url, selector):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    node = (soup.select_one(selector) if selector else None) or soup.body or soup
    return re.sub(r"\s+", " ", node.get_text(" ")).strip()


def find_keywords(text, keywords):
    low = text.lower()
    return [k for k in keywords if re.search(r"\b" + re.escape(k.lower()) + r"\b", low)]


def check_centre(centre, prev):
    text = fetch_text(centre["url"], centre.get("selector") or "")
    digest = hashlib.sha256(text.encode()).hexdigest()
    open_hits = find_keywords(text, centre.get("open_keywords", []))
    closed_hits = find_keywords(text, centre.get("closed_keywords", []))

    # Open if an "open" phrase is present, or the "closed" phrase vanished
    # (and stay open until a "closed" phrase comes back).
    was_closed_or_open = bool(prev.get("closed_hits")) or prev.get("open", False)
    is_open = bool(open_hits) or (not closed_hits and was_closed_or_open)
    changed = bool(prev.get("hash")) and prev["hash"] != digest

    return {
        "hash": digest,
        "open": is_open,
        "open_hits": open_hits,
        "closed_hits": closed_hits,
        "changed": changed,
        "checked": now(),
        "error": None,
    }


def notify(title, message, url=None):
    sent = False
    topic = os.environ.get("NTFY_TOPIC")
    if topic:
        payload = {"topic": topic, "title": title, "message": message,
                   "priority": 5, "tags": ["rotating_light"]}
        if url:
            payload["click"] = url
        requests.post("https://ntfy.sh/", json=payload, timeout=20).raise_for_status()
        sent = True

    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        text = f"{title}\n\n{message}" + (f"\n{url}" if url else "")
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat, "text": text}, timeout=20).raise_for_status()
        sent = True

    if not sent:
        print("  (no notification channel configured — set NTFY_TOPIC or TELEGRAM_*)")
    print(f"  >> ALERT: {title} | {message}")


def run_once():
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    state = load_json(STATE_PATH, {})

    for centre in config["centres"]:
        name = centre["name"]
        prev = state.get(name, {})
        print(f"[{now()}] {name}")
        try:
            cur = check_centre(centre, prev)
        except Exception as exc:  # network error, 403, timeout...
            print(f"  error: {exc}")
            errors = prev.get("errors", 0) + 1
            state[name] = {**prev, "error": str(exc), "errors": errors, "checked": now()}
            if errors == 3:  # warn once when a site keeps failing
                notify(f"TCF monitor: cannot reach {name}", str(exc)[:300], centre["url"])
            continue

        print(f"  open={cur['open']} open_hits={cur['open_hits']} "
              f"closed_hits={cur['closed_hits']} changed={cur['changed']}")

        if cur["open"] and not prev.get("open"):
            hits = ", ".join(cur["open_hits"]) or "'closed' message disappeared"
            notify(f"🟢 TCF registration may be OPEN: {name}",
                   f"Signal: {hits}. Go book now!", centre["url"])
        elif cur["changed"] and centre.get("alert_on_change"):
            notify(f"🔔 TCF page changed: {name}",
                   "The sessions page changed — check it now.", centre["url"])

        cur["errors"] = 0
        state[name] = cur

    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--loop", type=int, metavar="SECONDS",
                        help="keep running, checking every SECONDS (e.g. 1800)")
    parser.add_argument("--test-notify", action="store_true", help="send a test alert and exit")
    args = parser.parse_args()

    if args.test_notify:
        notify("✅ TCF monitor test", "Notifications are working.")
        return

    while True:
        run_once()
        if not args.loop:
            break
        time.sleep(args.loop)


if __name__ == "__main__":
    sys.exit(main())
