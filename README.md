# NetDiag — Network Troubleshooting & Diagnostics Toolkit

A lightweight Python command-line toolkit for focused connectivity checks against one explicitly supplied host. This is a learning/demo project for basic network troubleshooting.

## Features
- **ICMP ping:** checks host reachability and displays native command output.
- **DNS lookup:** resolves hostnames and lists IPv4/IPv6 addresses.
- **TCP port test:** checks whether a TCP connection can be established to a specified port.
- **Traceroute:** displays the route toward a target with a configurable hop limit.
- **HTTP/HTTPS check:** requests a URL and reports its response status.
- **JSON report:** exports results, timestamps and platform details.
- Uses Python's standard library; no third-party packages are required.

## Requirements
- Python 3.10 or newer.
- Windows includes `ping` and `tracert`. Linux/macOS need `ping` and `traceroute` available for those tests.

## Run on Windows
```bat
python -m venv venv
venv\Scripts\activate
python netdiag.py example.com
```

Run selected tests:
```bat
python netdiag.py example.com --tests dns port http --port 443
python netdiag.py 8.8.8.8 --tests ping trace --max-hops 6
```

Save a JSON report:
```bat
python netdiag.py example.com --json reports\example-com-report.json
```

## Interpret results
- **Ping fails:** ICMP may be blocked by the target or firewall. Check DNS and service connectivity before concluding the host is down.
- **DNS fails:** verify the hostname, configured DNS resolver and local network configuration.
- **TCP port fails:** the service may be stopped, filtered, listening on another port, or unreachable.
- **Traceroute timeouts:** some routers intentionally do not answer trace probes. Asterisks do not automatically mean traffic cannot reach the destination.
- **HTTP check fails:** inspect DNS, TCP reachability, TLS, proxy configuration and HTTP status.

A successful ping does not prove an application is healthy, and a failed ping does not necessarily mean a host is unavailable.

## Example troubleshooting workflow
1. Check DNS resolution.
2. Check reachability with ping.
3. Test the application's TCP port (for example, 443 for HTTPS).
4. Use traceroute when route information may help.
5. Check an application-level HTTP/HTTPS response.
6. Export a JSON report for documentation.

## Safety
Run diagnostics only against systems and networks you own or are explicitly authorized to test. This tool accepts one target at a time; it does not scan IP ranges or enumerate devices.

## Limitations
- Diagnostic helper, not a continuous monitoring platform.
- ICMP and traceroute depend on OS utilities and network/firewall policies.
- TCP test establishes a connection only; it does not validate application behavior.
- HTTP check performs a basic GET request and no authenticated testing.
- It does not capture or decode packets. For packet-level inspection, see [WIRESHARK_LAB.md](WIRESHARK_LAB.md).

## Interview summary
"I built a Python network diagnostics toolkit that helps troubleshoot connectivity in layers. It checks DNS resolution, ICMP reachability, TCP port connectivity, route tracing and HTTP/HTTPS response status. It can export a timestamped JSON report. It tests one explicitly supplied target rather than scanning networks, and its results must be interpreted carefully because firewalls can block ICMP or traceroute probes."
