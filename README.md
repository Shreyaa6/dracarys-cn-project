# Private Network Service Platform

**Course**: Computer Networks  
**Project Phase**: Phase 1 Final Submission  
**Team Name**: Dracarys  

---

## 1. Project Description

The **Private Network Service Platform** is an end-to-end, multi-tier private network architecture deployed across a local area network on heterogeneous devices (macOS and Raspberry Pi Linux). The system demonstrates production networking concepts:

1. **Authoritative Private Name Resolution**: Isolated DNS service resolving private domain `app.dracarys.test` via `dnsmasq`.
2. **Edge Reverse Proxy & TLS Termination**: `nginx 1.31.6` terminating TLSv1.2/TLSv1.3 with a custom Public Key Infrastructure (PKI) Local CA, forwarding traffic to backend pools.
3. **Round-Robin Load Balancing**: Equal-weight load distribution across heterogeneous backend servers with automated failover.
4. **Application Backends with HTTP/1.1 Semantics**: Python HTTP servers providing REST endpoints (`/`, `/api/status`), method handling (`GET`, `HEAD`), cache control headers (`Cache-Control: max-age=60`), and conditional revalidation via `ETag` returning `304 Not Modified`.
5. **Observability & Resilience**: Comprehensive Wireshark packet capture analysis and verified resilience against five distinct network failure modes.

---

## 2. Team Members

| Name | Role / Machine Responsibility | Enrollment Number |
| :--- | :--- | :--- |
| **Shreya Narayani** | Authoritative Private DNS Server (dnsmasq on macOS) | 2401020067 |
| **Meghna Nair** | Application Backend A (Python HTTPServer on macOS) | 2401010274 |
| **Pranjal Shukla** | Edge Reverse Proxy, TLS Termination, Load Balancer (nginx on macOS) | 2401010335 |
| **Ritesh Kumar** | — | 2401010384 |

---

## 3. Network Architecture & Machine Inventory

All participating systems operate within a private IPv4 `/19` campus/LAN subnet with a default gateway at `10.7.0.1`.

```text
                               +----------------------------------+
                               |           Client Host            |
                               | (Configured DNS: 10.7.3.26)      |
                               +-----------------+----------------+
                                                 |
                       1. DNS Query (UDP/53)     |  3. HTTPS Request (TCP/8443)
                       "app.dracarys.test"       |     TLSv1.2 / TLSv1.3
                                                 |
                     +---------------------------+---------------------------+
                     |                                                       |
                     v                                                       v
      +-----------------------------+                         +-----------------------------+
      |       Private DNS Host      |                         |      Edge / Load Balancer   |
      |          Shreya Mac         |                         |         Pranjal Mac         |
      |         10.7.3.26           |                         |         10.7.26.65          |
      |        dnsmasq (en0)        |                         |        nginx 1.31.6         |
      +-----------------------------+                         +--------------+--------------+
                     |                                                       |
                     +-- Resolves to 10.7.26.65                              | Round-Robin Upstream
                                                                             | Proxy (HTTP)
                                                     +-----------------------+-----------------------+
                                                     |                                               |
                                                     v                                               v
                                      +-----------------------------+                 +-----------------------------+
                                      |          Backend A          |                 |          Backend B          |
                                      |          Meghna Mac         |                 |         Raspberry Pi        |
                                      |         10.7.22.237         |                 |         10.7.23.235         |
                                      |          Port: 3001         |                 |       Port: 3002 (wlan0)    |
                                      |         X-Backend: A        |                 |         X-Backend: B        |
                                      +-----------------------------+                 +-----------------------------+
```

### Machine & Service Mapping

| Role | Host Device | IP Address | Subnet / Gateway | Interface | Port(s) | Service | Config / Source Location |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Private DNS** | Shreya Mac | `10.7.3.26` | `/19` (`10.7.0.1`) | `en0` | UDP/53, TCP/53 | `dnsmasq` | `dns/dnsmasq.conf` |
| **Edge / Proxy** | Pranjal Mac | `10.7.26.65` | `/19` (`10.7.0.1`) | `en0` | 8080 (HTTP), 8443 (HTTPS) | `nginx 1.31.6` | `nginx/nginx.conf` |
| **Backend A** | Meghna Mac | `10.7.22.237` | `/19` (`10.7.0.1`) | `en0` | 3001 | Python HTTPServer | `~/CN_Project/backend-a/server.py` |
| **Backend B** | Raspberry Pi | `10.7.23.235` | `/19` (`10.7.0.1`) | `wlan0` | 3002 | Python HTTPServer | `~/CN_Project/backend-b/server.py` |

---

## 4. Repository Structure

```text
dracarys-cn-project/
├── .gitignore                  # Excludes private keys (*.key, *.pem), credentials, and caches
├── README.md                   # Project overview, run guides, and testing manual
├── backend-a/
│   └── server.py               # Backend A Python server (port 3001, X-Backend: A)
├── backend-b/
│   └── server.py               # Backend B Python server (port 3002, X-Backend: B)
├── dns/
│   └── dnsmasq.conf            # dnsmasq configuration (app.dracarys.test -> 10.7.26.65)
├── nginx/
│   └── nginx.conf              # Reverse proxy, SSL termination, and load balancing config
├── tls/
│   └── README.md               # Dracarys Local CA architecture, trust setup, and key policy
├── docs/
│   ├── architecture.md         # Comprehensive system architecture & Wireshark breakdown
│   └── failure-tests.md        # Fault injection scenarios and formal D3 failover demo
└── evidence/
    ├── README.md               # Explanation of packet captures and directory layout
    ├── dns/                    # Packet captures for DNS resolution
    ├── tcp/                    # Packet captures for TCP 3-way handshakes
    ├── tls/                    # Packet captures for TLS 1.2 handshake & encrypted streams
    ├── load-balancing/         # Round-robin request logs
    ├── caching/                # ETag and 304 Not Modified validation logs
    └── failures/               # Resilience testing outputs
```

---

## 5. Prerequisites & Environment

- **Python**: Python 3.8+ (uses standard library modules: `http.server`, `json`)
- **DNS Server**: `dnsmasq` installed on Shreya Mac (`brew install dnsmasq`)
- **Edge Server**: `nginx` 1.31.6+ installed on Pranjal Mac (`brew install nginx`)
- **Diagnostic Tools**: `dig`, `curl`, `wireshark` / `tshark`

---

## 6. How to Run the Services

### 6.1 Running Backend A (Meghna Mac - `10.7.22.237`)
```bash
# From workspace or home directory on Meghna Mac
cd ~/CN_Project/backend-a
python3 server.py
```
*Listens on `0.0.0.0:3001`. Emits `X-Backend: A`.*

### 6.2 Running Backend B (Raspberry Pi - `10.7.23.235`)
```bash
# On Raspberry Pi terminal (over SSH or local shell)
cd ~/CN_Project/backend-b
python3 server.py
```
*Listens on `0.0.0.0:3002` on interface `wlan0`. Emits `X-Backend: B`.*

### 6.3 Configuring & Running DNS (`dnsmasq` on Shreya Mac - `10.7.3.26`)
1. Place `dnsmasq.conf` into `/usr/local/etc/dnsmasq.conf` or run directly with:
   ```bash
   sudo dnsmasq -C ./dns/dnsmasq.conf -d
   ```
2. The server binds to `127.0.0.1` and `10.7.3.26` on interface `en0`.

### 6.4 Configuring & Running nginx (Pranjal Mac - `10.7.26.65`)
1. Ensure the TLS certificate is present at `/usr/local/etc/nginx/certs/app.dracarys.test.crt` and the private key is at `/usr/local/etc/nginx/certs/app.dracarys.test.key`.
2. Validate syntax:
   ```bash
   nginx -t -c $(pwd)/nginx/nginx.conf
   ```
3. Start or reload nginx:
   ```bash
   nginx -c $(pwd)/nginx/nginx.conf
   # Or reload if already running:
   nginx -s reload
   ```

---

## 7. Verification & Testing Guide

Run the following commands from any client machine connected to the same subnet:

### 7.1 DNS Name Resolution Testing
Test resolution directly against the authoritative private DNS server:
```bash
# Query the private DNS server directly
dig @10.7.3.26 app.dracarys.test
```
**Expected Output**:
`app.dracarys.test` resolves with an `A` record pointing to `10.7.26.65`.

If the client's network interface DNS server is set to `10.7.3.26`:
```bash
dig app.dracarys.test
```

### 7.2 HTTPS & TLS Connectivity Testing
Test secure TLS connectivity. Because **Dracarys Local CA** is trusted in the client trust store, **no `-k` flag is needed**:
```bash
curl -v https://app.dracarys.test:8443
```
**Expected Output**:
- Verification: `SSL certificate verify ok`
- HTTP status: `HTTP/1.1 200 OK`
- JSON payload: `{"message": "Private Network Service", "backend": "A"}` (or `"B"`)

Inspect headers on `/api/status`:
```bash
curl -sI https://app.dracarys.test:8443/api/status
```
**Expected Output**:
```http
HTTP/1.1 200 OK
Server: nginx/1.31.6
Content-Type: application/json
X-Backend: A
ETag: "dracarys-v1"
Cache-Control: max-age=60
```

### 7.3 Round-Robin Load Balancing Testing
Verify that nginx alternates requests between Backend A (`10.7.22.237:3001`) and Backend B (`10.7.23.235:3002`):
```bash
for i in {1..6}; do
  echo "---- Request $i ----"
  curl -s -D - https://app.dracarys.test:8443/api/status -o /dev/null | grep -E 'HTTP/|X-Backend'
done
```
**Expected Output**:
```text
---- Request 1 ----
HTTP/1.1 200 OK
X-Backend: A
---- Request 2 ----
HTTP/1.1 200 OK
X-Backend: B
---- Request 3 ----
HTTP/1.1 200 OK
X-Backend: A
---- Request 4 ----
HTTP/1.1 200 OK
X-Backend: B
---- Request 5 ----
HTTP/1.1 200 OK
X-Backend: A
---- Request 6 ----
HTTP/1.1 200 OK
X-Backend: B
```

### 7.4 Caching & Conditional Revalidation (`ETag` / `304 Not Modified`)
Demonstrate HTTP conditional request validation using `If-None-Match`:
```bash
curl -i -H 'If-None-Match: "dracarys-v1"' https://app.dracarys.test:8443/api/status
```
**Expected Output**:
```http
HTTP/1.1 304 Not Modified
Server: nginx/1.31.6
ETag: "dracarys-v1"
Cache-Control: max-age=60
X-Backend: A
```
*(Notice: No JSON response body is returned, confirming bandwidth-saving revalidation).*

---

## 8. Failure Demonstrations Summary

A comprehensive failure matrix was executed across all tiers (documented in detail in [docs/failure-tests.md](file:///Users/shreyanarayani/dracarys-cn-project/docs/failure-tests.md)):
1. **Wrong DNS Server**: Lookup failed/timed out while IP layer ping remained functional.
2. **Wrong DNS Record**: Domain pointed to non-routable `192.0.2.123`; DNS succeeded, but TCP handshake timed out.
3. **One Backend Down (Formal D3 Demo)**: Backend B stopped; nginx seamlessly routed 100% of traffic to Backend A without client-visible downtime. Traffic re-balanced upon restarting Backend B.
4. **Both Backends Down**: nginx returned `HTTP/1.1 502 Bad Gateway`.
5. **Wrong Destination Port**: Requests to port `8444` were rejected with TCP RST (`Connection refused`).

---

## 9. Security & Key Management Policy

> [!IMPORTANT]
> **Zero Private Key Policy**:
> In compliance with strict security practices:
> - **No private keys** (`*.key`, `*.pem`, `*.p12`) are ever committed or tracked in this repository.
> - The repository's `.gitignore` file enforces exclusion of all cryptographic secret patterns.
> - Server private keys remain secured at `/usr/local/etc/nginx/certs/app.dracarys.test.key` on the proxy host.
> - All certificates are issued under our internal **Dracarys Local CA** and trusted via the operating system's local keychain.
