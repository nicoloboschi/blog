#!/usr/bin/env python3
"""
Publish a blog post: send the Buttondown newsletter.

Usage:
    uv run publish-post content/posts/my-post.md [--dry-run]
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from send_newsletter import (
    parse_post,
    build_post_url,
    build_payload,
    get_sent_emails,
    send_newsletter,
)


def resolve_path(path: str) -> Path:
    """Resolve path relative to the repo root (two levels up from this script)."""
    repo_root = Path(__file__).parent.parent.parent
    candidate = repo_root / path
    if candidate.exists():
        return candidate
    return Path(path)


def main():
    load_dotenv(Path(__file__).parent.parent.parent / ".env")

    parser = argparse.ArgumentParser(description="Publish a blog post (newsletter)")
    parser.add_argument("post_path", help="Path to post file (e.g., content/posts/my-post.md)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without publishing")
    args = parser.parse_args()

    buttondown_key = os.environ.get("BUTTONDOWN_API_KEY", "")
    site_url = os.environ.get("SITE_URL", "https://nicoloboschi.com")

    if not args.dry_run and not buttondown_key:
        print("Error: missing env var: BUTTONDOWN_API_KEY")
        print("Set it in .env or use --dry-run")
        sys.exit(1)

    resolved = resolve_path(args.post_path)
    if not resolved.exists():
        print(f"Post not found: {args.post_path}")
        sys.exit(1)

    try:
        frontmatter, body = parse_post(str(resolved))
    except ValueError as e:
        print(f"Error parsing post: {e}")
        sys.exit(1)

    if frontmatter.get("draft", False):
        print(f"Skipping draft: {args.post_path}")
        sys.exit(0)

    title = frontmatter.get("title", "New Post")
    post_url = build_post_url(frontmatter, site_url)

    print(f"Publishing: {title}")
    print(f"Post URL:   {post_url}")
    print()

    # --- Buttondown newsletter ---
    print("=== Buttondown Newsletter ===")
    if buttondown_key:
        sent_subjects = get_sent_emails(buttondown_key)
        if title in sent_subjects:
            print(f"Already sent, skipping newsletter: {title}")
        else:
            payload = build_payload(title, body, post_url)
            send_newsletter(payload, buttondown_key, dry_run=args.dry_run)
    elif args.dry_run:
        payload = build_payload(title, body, post_url)
        send_newsletter(payload, "", dry_run=True)
    else:
        print("Skipped (no API key)")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
