#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Log Query Script
Features:
  1. Initialize MCP session, get mcp-session-id
  2. Call query_cls_log to query logs by requestId
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


def step2_query_backend_log(session_id, request_id, env="production", topic="application"):
    """
    Step 2: Call query_cls_log to query logs by requestId
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "query_cls_log",
            "arguments": {
                "requestId": request_id,
                "env": env,
                "topic": topic
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


def step3_parse_and_format(raw_response, request_id):
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
    formatted_file = os.path.join(LOG_DIR, f"{request_id}_formatted.log")
    with open(formatted_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return formatted_file


def main():
    """Main function: chain all steps together"""
    if len(sys.argv) < 2:
        print("Usage: python query_backend_log.py <requestId> [env] [topic] [output_dir]")
        print("  requestId: The request ID to query (required)")
        print("  env:       production | staging (optional, default: production)")
        print("  topic:     Log topic (optional, default: application)")
        print("             Options: application | gateway | pdf")
        print("  output_dir: Root directory for saving logs (optional, default: script directory)")
        print("              Logs will be saved to <output_dir>/logs/")
        print()
        print("Examples:")
        print("  python query_backend_log.py c872a4bd-d874-4042-bf92-fa980f11d05b")
        print("  python query_backend_log.py c872a4bd-d874-4042-bf92-fa980f11d05b staging")
        print("  python query_backend_log.py c872a4bd-d874-4042-bf92-fa980f11d05b production pdf")
        print("  python query_backend_log.py c872a4bd-d874-4042-bf92-fa980f11d05b production application /path/to/workspace")
        sys.exit(1)

    request_id = sys.argv[1]
    env = sys.argv[2] if len(sys.argv) > 2 else "production"
    topic = sys.argv[3] if len(sys.argv) > 3 else "application"
    output_dir = sys.argv[4] if len(sys.argv) > 4 else None

    if output_dir:
        global LOG_DIR
        LOG_DIR = os.path.join(output_dir, "logs")

    # Step 1: Initialize session (prefer local cache)
    session_id = step1_initialize_session()

    # Step 2: Query logs
    raw_response = step2_query_backend_log(session_id, request_id, env, topic)

    # If None, session expired, refresh and retry
    if raw_response is None:
        session_id = step1_initialize_session(force_refresh=True)
        raw_response = step2_query_backend_log(session_id, request_id, env, topic)
        if raw_response is None:
            print("[Error] Still failed after refreshing session, please check network or service status", file=sys.stderr)
            sys.exit(1)

    # Step 3: Parse and format
    formatted_file = step3_parse_and_format(raw_response, request_id)

    print(f"  Formatted logs saved to: {formatted_file}")


if __name__ == "__main__":
    main()
