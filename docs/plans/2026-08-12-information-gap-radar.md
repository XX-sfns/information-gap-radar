# 每日信息差雷达 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a GitHub-hosted daily intelligence dashboard that commits fresh data and sends a concise notification.

**Architecture:** A Python collector writes a versioned `data/latest.json`; a dependency-free dashboard renders it on GitHub Pages. GitHub Actions runs the collector on a schedule, commits the result only when it changes, and calls configured notification channels.

**Tech Stack:** Python 3.11, requests, feedparser, pytest, GitHub Actions, static HTML/CSS/JavaScript.

---

### Task 1: Define portable configuration and data contracts

**Files:**
- Create: `config.example.yaml`
- Create: `src/radar/models.py`
- Test: `tests/test_models.py`

**Step 1:** Define normalized insight, pain-point, stock, and report models.

**Step 2:** Validate JSON serialization with pytest.

### Task 2: Implement collectors and pain-point classification

**Files:**
- Create: `src/radar/collectors.py`
- Create: `src/radar/classifier.py`
- Test: `tests/test_classifier.py`

**Step 1:** Fetch RSS, public Reddit JSON, Hacker News discussion and GitHub repositories with timeouts and source attribution.

**Step 2:** Classify user language into pain-point categories, urgency, audience and evidence signals; retain original links.

### Task 3: Generate reports and notifications

**Files:**
- Create: `src/radar/report.py`
- Create: `src/radar/notify.py`
- Create: `src/radar/cli.py`
- Test: `tests/test_report.py`

**Step 1:** Build `latest.json` and dated historical reports, resilient to individual source failures.

**Step 2:** Send a compact markdown report to Feishu, Telegram or a generic webhook, driven only by GitHub Secrets.

### Task 4: Build the Pages dashboard and automation

**Files:**
- Create: `index.html`, `assets/app.js`, `assets/style.css`
- Create: `.github/workflows/daily-radar.yml`
- Create: `README.md`

**Step 1:** Render four dashboards: AI/news, GitHub, stocks, and information gap.

**Step 2:** Schedule the workflow, publish Pages, commit result changes, and document secrets/setup.

### Task 5: Verify

**Files:**
- Test: `tests/`

**Step 1:** Run `python -m pytest -q`.

**Step 2:** Run the collector in offline-safe mode and validate generated JSON.
