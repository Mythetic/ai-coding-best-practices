#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Frontend Log Query Script
Features:
  1. Initialize MCP session, get mcp-session-id
  2. Call query_frontend_log to query frontend logs by aid + time range
  3. Parse JSON-RPC response, format into readable log lines
  4. Save formatted logs to local file
"""

import json
import os
import sys
import requests


# ========== Configuration ==========
MCP_URL = os.environ.get("MCP_ENDPOINT", "https://your-mcp-endpoint.example.com/")
_auth_token = os.environ.get("MCP_AUTH_TOKEN", "")
if not _auth_token:
    print("[Error] MCP_AUTH_TOKEN environment variable is not set", file=sys.stderr)
    sys.exit(1)
AUTH_TOKEN = f"Bearer {_auth_token}"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
SESSION_FILE = os.path.join(BASE_DIR, "sessionid")
# ===================================


def get_common_headers(session_id=None):
    """Build common request headers"""
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json, text/event-stream",
        "Authorization": AUTH_TOKEN,
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    return headers


def _load_cached_session():
    """Load cached session id from local file, return None if not exists"""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            sid = f.read().strip()
            if sid:
                return sid
    return None


def _save_cached_session(session_id):
    """Cache session id to local file"""
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        f.write(session_id)


def _request_new_session():
    """Request a new mcp-session-id from the remote server"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {
                "name": "python-client",
                "version": "1.0.0"
            }
        }
    }

    headers = get_common_headers()
    resp = requests.post(MCP_URL, json=payload, headers=headers, timeout=30)

    session_id = resp.headers.get("mcp-session-id") or resp.headers.get("Mcp-Session-Id")

    if not session_id:
        print(f"[Error] Failed to get mcp-session-id, HTTP status: {resp.status_code}", file=sys.stderr)
        sys.exit(1)

    return session_id


def step1_initialize_session(force_refresh=False):
    """
    Step 1: Initialize MCP session, get mcp-session-id
    Prefer reading from local cache; request remote if not exists or force_refresh=True
    """
    if not force_refresh:
        cached_sid = _load_cached_session()
        if cached_sid:
            return cached_sid

    session_id = _request_new_session()
    _save_cached_session(session_id)
    return session_id


def _to_utc(time_str):
    """
    Convert time string to UTC format.
    - If 'YYYY-MM-DD HH:MM:SS' (no timezone), treat as local time (UTC+8), subtract 8 hours
    - If timezone info present (e.g., '+08:00'), convert accordingly
    Returns UTC time string in format: 'YYYY-MM-DD HH:MM:SS'
    """
    from datetime import datetime, timedelta, timezone
    time_str = time_str.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S%z"):
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    # No timezone, treat as local time (UTC+8)
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return (dt - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")


def step2_query_frontend_log(session_id, aid, start_time, end_time, env="production"):
    """
    Step 2: Call query_frontend_log to query frontend logs by aid + time range
    Note: MCP API uses UTC time, input time (local) is auto-converted to UTC
    """
    utc_start = _to_utc(start_time)
    utc_end = _to_utc(end_time)
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "query_frontend_log",
            "arguments": {
                "aid": aid,
                "start_time": utc_start,
                "end_time": utc_end,
                "env": env
            }
        }
    }

    headers = get_common_headers(session_id)
    resp = requests.post(MCP_URL, json=payload, headers=headers, timeout=60)

    if "Invalid session ID" in resp.text:
        return None

    if resp.status_code != 200:
        print(f"[Error] Request failed (HTTP {resp.status_code}): {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.text


def step3_parse_and_format(raw_response, aid):
    """
    Step 3: Parse JSON-RPC response, format into log lines
    """
    data = json.loads(raw_response)

    result = data.get("result", {})
    if result.get("isError"):
        contents = result.get("content", [])
        error_msg = ""
        for item in contents:
            if item.get("type") == "text":
                error_msg = item["text"]
        print(f"[Error] API returned error: {error_msg}", file=sys.stderr)
        sys.exit(1)

    contents = result.get("content", [])
    lines = []
    for item in contents:
        if item.get("type") == "text":
            text = item["text"]
            for line in text.split("\n"):
                lines.append(line)

    os.makedirs(LOG_DIR, exist_ok=True)
    formatted_file = os.path.join(LOG_DIR, f"{aid}_frontend_formatted.log")
    with open(formatted_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return formatted_file


def main():
    """Main function: chain all steps together"""
    if len(sys.argv) < 4:
        print("Usage: python query_frontend_log.py <aid> <start_time> <end_time> [env] [output_dir]")
        print("  aid:        Frontend client ID, UUID format (required)")
        print("  start_time: Start time, format: YYYY-MM-DD HH:MM:SS (required)")
        print("  end_time:   End time, format: YYYY-MM-DD HH:MM:SS (required)")
        print("  env:        production | staging (optional, default: production)")
        print("  output_dir: Root directory for saving logs (optional, default: script directory)")
        print("              Logs will be saved to <output_dir>/logs/")
        print()
        print("Examples:")
        print('  python query_frontend_log.py 58316f1b-023e-44f2-a297-2287db9ae71f "2026-04-03 10:00:00" "2026-04-03 12:00:00"')
        print('  python query_frontend_log.py 58316f1b-023e-44f2-a297-2287db9ae71f "2026-04-03 10:00:00" "2026-04-03 12:00:00" staging')
        print('  python query_frontend_log.py 58316f1b-023e-44f2-a297-2287db9ae71f "2026-04-03 10:00:00" "2026-04-03 12:00:00" production /path/to/workspace')
        sys.exit(1)

    aid = sys.argv[1]
    start_time = sys.argv[2]
    end_time = sys.argv[3]
    env = sys.argv[4] if len(sys.argv) > 4 else "production"
    output_dir = sys.argv[5] if len(sys.argv) > 5 else None

    if output_dir:
        global LOG_DIR
        LOG_DIR = os.path.join(output_dir, "logs")

    # Step 1: Initialize session (prefer local cache)
    session_id = step1_initialize_session()

    # Step 2: Query frontend logs
    raw_response = step2_query_frontend_log(session_id, aid, start_time, end_time, env)

    # If None, session expired, refresh and retry
    if raw_response is None:
        session_id = step1_initialize_session(force_refresh=True)
        raw_response = step2_query_frontend_log(session_id, aid, start_time, end_time, env)
        if raw_response is None:
            print("[Error] Still failed after refreshing session, please check network or service status", file=sys.stderr)
            sys.exit(1)

    # Step 3: Parse and format
    formatted_file = step3_parse_and_format(raw_response, aid)

    print(f"  Formatted logs saved to: {formatted_file}")


if __name__ == "__main__":
    main()
