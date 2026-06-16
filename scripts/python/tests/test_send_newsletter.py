"""Tests for send_newsletter module."""

import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from send_newsletter import (
    get_schedule_time,
    build_email_body,
    build_payload,
    parse_post,
    build_post_url,
    NewsletterPayload,
)
import tempfile
from pathlib import Path


class TestGetScheduleTime:
    """Tests for get_schedule_time function."""

    def test_schedules_for_today_3pm_if_before(self):
        """Should schedule for today at 3pm if current time is before 3pm."""
        rome = ZoneInfo("Europe/Rome")
        now = datetime(2024, 6, 15, 10, 30, 0, tzinfo=rome)  # 10:30 AM Rome

        result = get_schedule_time(now)

        # Today 3pm Rome = June 15, 2024 at 15:00 Rome
        # In summer (CEST), Rome is UTC+2, so 15:00 Rome = 13:00 UTC
        assert result == "2024-06-15T13:00:00Z"

    def test_schedules_for_tomorrow_if_past_3pm(self):
        """Should schedule for tomorrow if current time is past 3pm."""
        rome = ZoneInfo("Europe/Rome")
        now = datetime(2024, 6, 15, 18, 0, 0, tzinfo=rome)  # 6pm Rome

        result = get_schedule_time(now)

        # Tomorrow (June 16) since it's past 3pm
        assert result == "2024-06-16T13:00:00Z"

    def test_handles_winter_time_before_3pm(self):
        """Should handle winter time (CET, UTC+1) and schedule today."""
        rome = ZoneInfo("Europe/Rome")
        now = datetime(2024, 1, 15, 10, 0, 0, tzinfo=rome)  # January, winter time

        result = get_schedule_time(now)

        # Today 3pm Rome (CET), Rome is UTC+1, so 15:00 Rome = 14:00 UTC
        assert result == "2024-01-15T14:00:00Z"


class TestBuildEmailBody:
    """Tests for build_email_body function."""

    def test_includes_post_link(self):
        """Should include link to full post."""
        body = "Short content"
        post_url = "https://example.com/posts/123"

        result = build_email_body(body, post_url)

        assert "[Read the full post](https://example.com/posts/123)" in result

    def test_truncates_long_content(self):
        """Should truncate content longer than max_length."""
        body = "x" * 2000
        post_url = "https://example.com/posts/123"

        result = build_email_body(body, post_url, max_length=100)

        assert result.startswith("x" * 100 + "...")
        assert len(result.split("---")[0].strip()) == 103  # 100 chars + "..."

    def test_no_truncation_for_short_content(self):
        """Should not add ellipsis for short content."""
        body = "Short content"
        post_url = "https://example.com/posts/123"

        result = build_email_body(body, post_url)

        assert "..." not in result.split("---")[0]


class TestBuildPayload:
    """Tests for build_payload function."""

    def test_creates_scheduled_payload(self):
        """Should create a payload with scheduled status."""
        rome = ZoneInfo("Europe/Rome")
        now = datetime(2024, 6, 15, 10, 0, 0, tzinfo=rome)

        payload = build_payload(
            title="Test Post",
            body="Test content",
            post_url="https://example.com/posts/123",
            now=now
        )

        assert payload.subject == "Test Post"
        assert payload.status == "scheduled"
        # Before 3pm → today at 3pm Rome (CEST = UTC+2) = 13:00 UTC
        assert payload.publish_date == "2024-06-15T13:00:00Z"
        assert "Test content" in payload.body
        assert "[Read the full post]" in payload.body

    def test_publish_date_is_today_3pm_rome_summer_if_before(self):
        """Verify publish_date is today 3pm Rome in summer when before 3pm."""
        rome = ZoneInfo("Europe/Rome")
        now = datetime(2024, 6, 15, 10, 0, 0, tzinfo=rome)

        payload = build_payload("Test", "Body", "https://example.com", now=now)

        assert payload.publish_date == "2024-06-15T13:00:00Z"

    def test_publish_date_is_tomorrow_3pm_rome_summer_if_after(self):
        """Verify publish_date is tomorrow 3pm Rome in summer when after 3pm."""
        rome = ZoneInfo("Europe/Rome")
        now = datetime(2024, 6, 15, 18, 0, 0, tzinfo=rome)

        payload = build_payload("Test", "Body", "https://example.com", now=now)

        assert payload.publish_date == "2024-06-16T13:00:00Z"

    def test_publish_date_is_today_3pm_rome_winter_if_before(self):
        """Verify publish_date is today 3pm Rome in winter when before 3pm."""
        rome = ZoneInfo("Europe/Rome")
        now = datetime(2026, 1, 23, 10, 0, 0, tzinfo=rome)

        payload = build_payload("Test", "Body", "https://example.com", now=now)

        assert payload.publish_date == "2026-01-23T14:00:00Z"

    def test_to_dict(self):
        """Should convert payload to dict for API."""
        payload = NewsletterPayload(
            subject="Test",
            body="Body",
            status="scheduled",
            publish_date="2024-06-16T13:00:00Z"
        )

        result = payload.to_dict()

        assert result == {
            "subject": "Test",
            "body": "Body",
            "status": "scheduled",
            "publish_date": "2024-06-16T13:00:00Z"
        }


class TestParsePost:
    """Tests for parse_post function."""

    def test_parses_toml_frontmatter(self):
        """Should parse TOML frontmatter correctly."""
        content = """+++
date = '2024-06-15T10:00:00+02:00'
draft = false
title = 'Test Post Title'
tags = ["test", "example"]
+++

This is the body content.

With multiple paragraphs."""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()

            frontmatter, body = parse_post(f.name)

            assert frontmatter["title"] == "Test Post Title"
            assert frontmatter["draft"] is False
            assert frontmatter["tags"] == ["test", "example"]
            assert "This is the body content." in body
            assert "With multiple paragraphs." in body

            Path(f.name).unlink()

    def test_raises_on_invalid_frontmatter(self):
        """Should raise ValueError for invalid frontmatter."""
        content = "No frontmatter here, just content."

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()

            with pytest.raises(ValueError, match="Could not parse frontmatter"):
                parse_post(f.name)

            Path(f.name).unlink()


class TestBuildPostUrl:
    """Tests for build_post_url function."""

    def test_builds_url_from_date(self):
        """Should build URL using date from frontmatter."""
        frontmatter = {"date": "2024-06-15T10:00:00+02:00"}
        site_url = "https://nicoloboschi.com"

        result = build_post_url(frontmatter, site_url)

        assert result == "https://nicoloboschi.com/posts/20240615"

    def test_handles_datetime_object(self):
        """Should handle datetime object in frontmatter."""
        frontmatter = {"date": datetime(2024, 6, 15, 10, 0, 0)}
        site_url = "https://example.com"

        result = build_post_url(frontmatter, site_url)

        assert result == "https://example.com/posts/20240615"
