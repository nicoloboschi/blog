#!/usr/bin/env python3
"""
Publish a blog post: send Buttondown newsletter + publish to Hashnode.

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
from publish_hashnode import (
    publish_to_hashnode,
    get_published_posts,
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

    parser = argparse.ArgumentParser(description="Publish a blog post (newsletter + Hashnode)")
    parser.add_argument("post_path", help="Path to post file (e.g., content/posts/my-post.md)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without publishing")
    args = parser.parse_args()

    buttondown_key = os.environ.get("BUTTONDOWN_API_KEY", "")
    hashnode_token = os.environ.get("HASHNODE_API_TOKEN", "")
    hashnode_pub_id = os.environ.get("HASHNODE_PUBLICATION_ID", "")
    site_url = os.environ.get("SITE_URL", "https://nicoloboschi.com")

    if not args.dry_run:
        missing = []
        if not buttondown_key:
            missing.append("BUTTONDOWN_API_KEY")
        if not hashnode_token:
            missing.append("HASHNODE_API_TOKEN")
        if not hashnode_pub_id:
            missing.append("HASHNODE_PUBLICATION_ID")
        if missing:
            print(f"Error: missing env vars: {', '.join(missing)}")
            print("Set them in .env or use --dry-run")
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
    tags = frontmatter.get("tags", [])
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

    # --- Hashnode ---
    print("=== Hashnode ===")
    if hashnode_token and hashnode_pub_id:
        published_posts = get_published_posts(hashnode_token, hashnode_pub_id)
        existing_post_id = published_posts.get(title)
        if existing_post_id:
            print(f"Post exists on Hashnode, updating...")
        result = publish_to_hashnode(
            title=title,
            body=body,
            tags=tags,
            api_token=hashnode_token,
            publication_id=hashnode_pub_id,
            original_url=post_url,
            site_url=site_url,
            existing_post_id=existing_post_id,
            dry_run=args.dry_run,
        )
        if not result.success:
            print(f"Hashnode failed: {result.error}")
            sys.exit(1)
    elif args.dry_run:
        print("[DRY RUN] Would publish to Hashnode (no token)")
    else:
        print("Skipped (no API token)")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
