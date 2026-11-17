#!/usr/bin/env python3
"""Focused network diagnostics for one explicitly supplied target."""
from __future__ import annotations
import argparse
import json
import platform
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def ping(host: str, count: int = 4, timeout_ms: int = 1200) -> dict[str, Any]:
    command = (["ping", "-n", str(count), "-w", str(timeout_ms), host]
               if platform.system().lower() == "windows"
               else ["ping", "-c", str(count), "-W", str(max(1, (timeout_ms + 999)//1000)), host])
    start = time.perf_counter()
    try:
        p = subprocess.run(command, capture_output=True, text=True, errors="replace",
                           timeout=max(10, count * (timeout_ms / 1000 + 2)), check=False)
        return {"test": "ping", "target": host, "success": p.returncode == 0,
                "return_code": p.returncode,
                "duration_ms": round((time.perf_counter()-start)*1000, 2),
                "details": (p.stdout + "\n" + p.stderr).strip()[-4000:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"test": "ping", "target": host, "success": False, "error": str(exc)}


def dns_lookup(host: str) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        records = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        addresses = sorted({r[4][0] for r in records})
        return {"test": "dns_lookup", "target": host, "success": bool(addresses),
                "addresses": addresses, "duration_ms": round((time.perf_counter()-start)*1000, 2)}
    except socket.gaierror as exc:
        return {"test": "dns_lookup", "target": host, "success": False,
                "error": str(exc), "duration_ms": round((time.perf_counter()-start)*1000, 2)}


def tcp_port(host: str, port: int, timeout: float = 3.0) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"test": "tcp_port", "target": host, "port": port, "success": True,
                    "message": "TCP connection established",
                    "duration_ms": round((time.perf_counter()-start)*1000, 2)}
    except (OSError, TimeoutError) as exc:
        return {"test": "tcp_port", "target": host, "port": port, "success": False,
                "error": str(exc), "duration_ms": round((time.perf_counter()-start)*1000, 2)}


def traceroute(host: str, max_hops: int = 8, timeout_ms: int = 700) -> dict[str, Any]:
    if platform.system().lower() == "windows":
        command = ["tracert", "-d", "-h", str(max_hops), "-w", str(timeout_ms), host]
    else:
        command = ["traceroute", "-n", "-m", str(max_hops), "-w",
                   str(max(1, timeout_ms // 1000)), host]
    start = time.perf_counter()
    try:
        p = subprocess.run(command, capture_output=True, text=True, errors="replace",
                           timeout=max(15, max_hops * (timeout_ms/1000) * 3 + 5), check=False)
        return {"test": "traceroute", "target": host, "success": p.returncode == 0,
                "return_code": p.returncode,
                "duration_ms": round((time.perf_counter()-start)*1000, 2),
                "details": (p.stdout + "\n" + p.stderr).strip()[-6000:],
                "note": "Some routers do not answer trace probes; timeouts alone do not prove an outage."}
    except FileNotFoundError:
        return {"test": "traceroute", "target": host, "success": False,
                "error": "Traceroute utility not found. Windows uses tracert; Linux/macOS commonly use traceroute."}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"test": "traceroute", "target": host, "success": False, "error": str(exc)}


def http_check(url: str, timeout: float = 5.0) -> dict[str, Any]:
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    request = urllib.request.Request(url, headers={"User-Agent": "NetDiagToolkit/1.0"})
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {"test": "http_check", "target": url,
                    "success": 200 <= response.status < 400, "status_code": response.status,
                    "duration_ms": round((time.perf_counter()-start)*1000, 2)}
    except urllib.error.HTTPError as exc:
        return {"test": "http_check", "target": url, "success": False,
                "status_code": exc.code, "error": str(exc),
                "duration_ms": round((time.perf_counter()-start)*1000, 2)}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"test": "http_check", "target": url, "success": False, "error": str(exc),
                "duration_ms": round((time.perf_counter()-start)*1000, 2)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run focused diagnostics against one authorized host.")
    parser.add_argument("target", help="Hostname or IP address")
    parser.add_argument("--tests", nargs="+",
                        choices=["ping", "dns", "port", "trace", "http", "all"], default=["all"])
    parser.add_argument("--port", type=int, default=443)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--max-hops", type=int, default=8)
    parser.add_argument("--json", dest="json_path", help="Optional JSON report path")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    if not 1 <= args.count <= 10:
        parser.error("--count must be between 1 and 10")
    if not 1 <= args.max_hops <= 20:
        parser.error("--max-hops must be between 1 and 20")

    selected = {"ping", "dns", "port", "trace", "http"} if "all" in args.tests else set(args.tests)
    results = []
    if "ping" in selected: results.append(ping(args.target, args.count))
    if "dns" in selected: results.append(dns_lookup(args.target))
    if "port" in selected: results.append(tcp_port(args.target, args.port))
    if "trace" in selected: results.append(traceroute(args.target, args.max_hops))
    if "http" in selected: results.append(http_check(args.target))

    report = {"tool": "NetDiag Toolkit", "generated_at": datetime.now(timezone.utc).isoformat(),
              "target": args.target, "platform": platform.platform(), "results": results}
    print(f"\nNetDiag Toolkit | Target: {args.target}\n" + "-"*58)
    for item in results:
        label = "PASS" if item.get("success") else "CHECK"
        print(f"[{label}] {item['test']} | {item.get('duration_ms', 'N/A')} ms")
        if item.get("addresses"): print("       Addresses:", ", ".join(item["addresses"]))
        if item.get("port"): print("       TCP port:", item["port"])
        if item.get("status_code"): print("       HTTP status:", item["status_code"])
        if item.get("error"): print("       Error:", item["error"])
        if item.get("details"):
            for line in item["details"].splitlines()[-10:]: print("       ", line)
    if args.json_path:
        path = Path(args.json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nJSON report saved to: {path.resolve()}")
    print("\nA failed probe is a diagnostic clue, not by itself proof of a network fault.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
