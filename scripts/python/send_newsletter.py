#!/usr/bin/env python3
"""
Send newsletter via Buttondown API when a new post is published.
Always schedules for the following day at 3pm Europe/Rome timezone.
"""

import json
import os
import re
import sys
import subprocess
import requests
import toml
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dataclasses import dataclass
from typing import Optional


@dataclass
class NewsletterPayload:
    """Payload to be sent to Buttondown API."""
    subject: str
    body: str
    status: str
    publish_date: str

    def to_dict(self) -> dict:
        return {
            "subject": self.subject,
            "body": self.body,
            "status": self.status,
            "publish_date": self.publish_date
        }


def get_schedule_time(now: Optional[datetime] = None) -> str:
    """Get tomorrow at 3pm Europe/Rome timezone, formatted as ISO UTC."""
    europe = ZoneInfo("Europe/Rome")
    if now is None:
        now = datetime.now(europe)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=europe)

    tomorrow_3pm = (now + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
    # Convert to UTC for the API
    return tomorrow_3pm.astimezone(ZoneInfo("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_new_posts() -> list[str]:
    """Get list of new/modified posts from git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f.startswith("content/posts/") and f.endswith(".md")]
    except subprocess.CalledProcessError:
        return []


def parse_post(post_path: str) -> tuple[dict, str]:
    """Parse a Hugo post with TOML frontmatter."""
    content = Path(post_path).read_text()

    # Split frontmatter and body
    match = re.match(r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)$', content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse frontmatter in {post_path}")

    frontmatter_str, body = match.groups()
    frontmatter = toml.loads(frontmatter_str)

    return frontmatter, body.strip()


def build_post_url(frontmatter: dict, site_url: str) -> str:
    """Build the URL for the post based on Hugo permalink structure."""
    date = frontmatter.get("date", "")
    if isinstance(date, str):
        date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    # Format: /posts/:year:month:day (from hugo.toml)
    date_path = date.strftime("%Y%m%d")
    return f"{site_url}/posts/{date_path}"


def build_email_body(body: str, post_url: str) -> str:
    """Build email body with link to full post."""
    return f"""{body}

---

[Read the full post]({post_url})"""


def build_payload(title: str, body: str, post_url: str, now: Optional[datetime] = None) -> NewsletterPayload:
    """Build the newsletter payload."""
    schedule_time = get_schedule_time(now)
    email_body = build_email_body(body, post_url)

    return NewsletterPayload(
        subject=title,
        body=email_body,
        status="scheduled",
        publish_date=schedule_time
    )


def get_sent_emails(api_key: str) -> set[str]:
    """Get list of already sent email subjects from Buttondown."""
    response = requests.get(
        "https://api.buttondown.com/v1/emails",
        headers={"Authorization": f"Token {api_key}"}
    )

    if response.status_code != 200:
        print(f"Warning: Could not fetch existing emails: {response.status_code}")
        return set()

    emails = response.json().get("results", [])
    return {email.get("subject") for email in emails if email.get("subject")}


def send_newsletter(payload: NewsletterPayload, api_key: str, dry_run: bool = False) -> bool:
    """Send newsletter via Buttondown API."""

    print(f"Scheduling for: {payload.publish_date} (tomorrow 3pm Europe/Rome)")

    if dry_run:
        print("\n[DRY RUN] Would send payload:")
        print(json.dumps(payload.to_dict(), indent=2))
        return True

    response = requests.post(
        "https://api.buttondown.com/v1/emails",
        headers={
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        },
        json=payload.to_dict()
    )

    if response.status_code in (200, 201):
        print(f"Newsletter scheduled successfully: {payload.subject}")
        return True
    else:
        print(f"Failed to schedule newsletter: {response.status_code}")
        print(response.text)
        return False


def resolve_path(path: str) -> Path:
    """Resolve a path relative to REPO_ROOT if set, otherwise relative to cwd."""
    repo_root = os.environ.get("REPO_ROOT", "")
    if repo_root:
        return Path(repo_root) / path
    return Path(path)


def main():
    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    site_url = os.environ.get("SITE_URL", "https://nicoloboschi.com")
    dry_run = os.environ.get("DRY_RUN", "").lower() in ("true", "1", "yes")

    if not api_key and not dry_run:
        print("Error: BUTTONDOWN_API_KEY not set (use DRY_RUN=true to test without it)")
        sys.exit(1)

    # Check for manual input
    manual_post = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None

    if manual_post:
        posts = [manual_post]
    else:
        posts = get_new_posts()

    if not posts:
        print("No new posts detected")
        return

    # Get already sent emails to avoid duplicates (skip in dry run without API key)
    if api_key:
        sent_subjects = get_sent_emails(api_key)
        print(f"Found {len(sent_subjects)} existing emails in Buttondown")
    else:
        sent_subjects = set()
        print("[DRY RUN] Skipping duplicate check (no API key)")

    for post_path in posts:
        resolved_path = resolve_path(post_path)
        if not resolved_path.exists():
            print(f"Post not found: {post_path}")
            continue

        try:
            frontmatter, body = parse_post(str(resolved_path))
        except ValueError as e:
            print(f"Error parsing post: {e}")
            continue

        # Skip drafts
        if frontmatter.get("draft", False):
            print(f"Skipping draft: {post_path}")
            continue

        title = frontmatter.get("title", "New Post")

        # Check if already sent
        if title in sent_subjects:
            print(f"Skipping (already sent): {title}")
            continue

        post_url = build_post_url(frontmatter, site_url)
        payload = build_payload(title, body, post_url)

        print(f"Sending newsletter for: {title}")
        print(f"Post URL: {post_url}")

        send_newsletter(payload, api_key or "", dry_run)


if __name__ == "__main__":
    main()
