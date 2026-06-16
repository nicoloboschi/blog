#!/usr/bin/env python3
"""Publish blog posts to Hashnode via GraphQL API."""

import re

import requests
from dataclasses import dataclass


HASHNODE_API_URL = "https://gql.hashnode.com"

PUBLISH_POST_MUTATION = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      url
      title
    }
  }
}
"""

UPDATE_POST_MUTATION = """
mutation UpdatePost($input: UpdatePostInput!) {
  updatePost(input: $input) {
    post {
      id
      url
      title
    }
  }
}
"""

GET_POSTS_QUERY = """
query GetPosts($publicationId: ObjectId!, $first: Int!) {
  publication(id: $publicationId) {
    posts(first: $first) {
      edges {
        node {
          id
          title
        }
      }
    }
  }
}
"""


@dataclass
class HashnodeResult:
    success: bool
    url: str = ""
    error: str = ""


def get_published_posts(api_token: str, publication_id: str) -> dict[str, str]:
    """Get map of title→id for already published posts."""
    response = requests.post(
        HASHNODE_API_URL,
        headers={
            "Authorization": api_token,
            "Content-Type": "application/json",
        },
        json={
            "query": GET_POSTS_QUERY,
            "variables": {
                "publicationId": publication_id,
                "first": 50,
            },
        },
    )

    if response.status_code != 200:
        print(f"Warning: Could not fetch Hashnode posts: {response.status_code}")
        return {}

    data = response.json()
    if "errors" in data:
        print(f"Warning: Hashnode API error: {data['errors']}")
        return {}

    posts = data.get("data", {}).get("publication", {}).get("posts", {}).get("edges", [])
    return {edge["node"]["title"]: edge["node"]["id"] for edge in posts}


def resolve_image_urls(body: str, site_url: str) -> str:
    """Rewrite relative image paths to absolute URLs so external platforms can load them."""
    return re.sub(
        r'(!\[[^\]]*\])\((/[^)]+)\)',
        lambda m: f'{m.group(1)}({site_url}{m.group(2)})',
        body,
    )


def publish_to_hashnode(
    title: str,
    body: str,
    tags: list[str],
    api_token: str,
    publication_id: str,
    original_url: str,
    site_url: str = "https://nicoloboschi.com",
    existing_post_id: str | None = None,
    dry_run: bool = False,
) -> HashnodeResult:
    """Publish or update a post on Hashnode."""

    # Rewrite relative image paths to absolute URLs
    body = resolve_image_urls(body, site_url)

    # Add canonical URL pointing back to the original blog
    body_with_canonical = f"> Originally published at [{original_url}]({original_url})\n\n{body}"

    is_update = existing_post_id is not None
    tag_objects = [{"slug": tag.lower().replace(" ", "-"), "name": tag} for tag in tags]

    if is_update:
        mutation = UPDATE_POST_MUTATION
        variables = {
            "input": {
                "id": existing_post_id,
                "title": title,
                "contentMarkdown": body_with_canonical,
                "originalArticleURL": original_url,
                "tags": tag_objects,
            }
        }
        operation = "updatePost"
    else:
        mutation = PUBLISH_POST_MUTATION
        variables = {
            "input": {
                "title": title,
                "contentMarkdown": body_with_canonical,
                "publicationId": publication_id,
                "originalArticleURL": original_url,
                "tags": tag_objects,
            }
        }
        operation = "publishPost"

    action = "update" if is_update else "publish"

    if dry_run:
        print(f"\n[DRY RUN] Would {action} on Hashnode:")
        print(f"  Title: {title}")
        print(f"  Tags: {tags}")
        print(f"  Canonical URL: {original_url}")
        print(f"  Body length: {len(body_with_canonical)} chars")
        if is_update:
            print(f"  Post ID: {existing_post_id}")
        return HashnodeResult(success=True, url="(dry run)")

    response = requests.post(
        HASHNODE_API_URL,
        headers={
            "Authorization": api_token,
            "Content-Type": "application/json",
        },
        json={"query": mutation, "variables": variables},
    )

    if response.status_code != 200:
        return HashnodeResult(success=False, error=f"HTTP {response.status_code}: {response.text}")

    data = response.json()

    if "errors" in data:
        return HashnodeResult(success=False, error=str(data["errors"]))

    post = data.get("data", {}).get(operation, {}).get("post", {})
    url = post.get("url", "")
    print(f"{'Updated' if is_update else 'Published'} on Hashnode: {url}")
    return HashnodeResult(success=True, url=url)
