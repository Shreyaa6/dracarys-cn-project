# Failure & Resilience Demonstrations

This document details the failure testing and resilience validations conducted on the **Private Network Service Platform** (Team Dracarys).

All tests were performed on live network interfaces across the participating nodes and restored to normal operation upon completion.

---

## 1. Summary of Completed Failure Demonstrations

| # | Test Scenario | Fault Injected | Observed Network Behavior | Recovery / Restoration |
|---|---|---|---|---|
| **1** | **Wrong DNS Server** | Client DNS temporarily changed to `192.0.2.53` | `dig +time=2 +tries=1 app.dracarys.test` timed out / no servers could be reached. `ping -c 3 10.7.26.65` still succeeded with 0% packet loss, confirming layer isolation between DNS resolution and IP routing. | DNS restored to `10.7.3.26`; `dig` again successfully resolved `app.dracarys.test` to `10.7.26.65`. |
| **2** | **Wrong DNS Record** | DNS record temporarily modified: `app.dracarys.test -> 192.0.2.123` (RFC 5737 TEST-NET-1 non-routable address) | DNS lookup succeeded rapidly (`A 192.0.2.123`), but subsequent HTTPS connection attempt to port 8443 timed out at the TCP SYN phase. | Reverted `dnsmasq.conf` mapping to `10.7.26.65` and reloaded `dnsmasq`. |
| **3** | **One Backend Down (Formal D3 Scenario)** | Stopped Backend B (`10.7.23.235:3002`) on Raspberry Pi | nginx detected upstream TCP connection failure to Backend B, automatically routed all incoming requests to Backend A (`10.7.22.237:3001`). Client experienced uninterrupted HTTPS service with `X-Backend: A`. | Restarted Backend B server. Demonstrated requests resumed alternating between Backend A and Backend B. |
| **4** | **Both Backends Down** | Stopped both Backend A (`3001`) and Backend B (`3002`) | nginx received TCP connection refused from both upstream pool members. nginx returned `HTTP/1.1 502 Bad Gateway` to the client. TLS termination at the edge was unaffected. | Restarted Backend A and Backend B. Service recovered to 200 OK. |
| **5** | **Wrong Destination Port** | Client attempted HTTPS connection to `app.dracarys.test:8444` (unbound port) | TCP SYN packet to port 8444 was immediately answered with a TCP RST from the edge host OS (`10.7.26.65`), resulting in `curl: (7) Failed to connect to app.dracarys.test port 8444: Connection refused`. | Directed requests back to configured port 8443 (or 8080). |

---

## 2. Formal D3 Demonstration: Single Backend Failure & Automatic Recovery

The primary resilience scenario selected for demonstration is **Scenario 3: One Backend Down**.

### 2.1 Baseline State (Normal Operation)
Both Backend A (`10.7.22.237:3001`) and Backend B (`10.7.23.235:3002`) are active.
Requests to `https://app.dracarys.test:8443/api/status` alternate between backends due to nginx round-robin load balancing.

```bash
for i in {1..6}; do
  echo "---- Request $i ----"
  curl -s -D - https://app.dracarys.test:8443/api/status -o /dev/null | grep -E 'HTTP/|X-Backend'
done
```

**Observed Output:**
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

### 2.2 Fault Injection: Stop Backend B
On Raspberry Pi (`10.7.23.235`):
```bash
# Terminate the running backend-b process
kill <pid>   # or Ctrl+C
```

### 2.3 Degraded State (Failover Active)
The client repeats the request loop. Because Backend B is offline, nginx marks Backend B as temporarily failed and dispatches all requests to the healthy node Backend A:

```bash
for i in {1..4}; do
  echo "---- Request $i ----"
  curl -s -D - https://app.dracarys.test:8443/api/status -o /dev/null | grep -E 'HTTP/|X-Backend'
done
```

**Observed Output:**
```text
---- Request 1 ----
HTTP/1.1 200 OK
X-Backend: A
---- Request 2 ----
HTTP/1.1 200 OK
X-Backend: A
---- Request 3 ----
HTTP/1.1 200 OK
X-Backend: A
---- Request 4 ----
HTTP/1.1 200 OK
X-Backend: A
```
**Key Evaluation Point**: Demonstrated requests continued returning HTTP 200 OK, with X-Backend confirming responses from Backend A while Backend B was unavailable.

### 2.4 Recovery & Restoration
On Raspberry Pi (`10.7.23.235`):
```bash
python3 ~/CN_Project/backend-b/server.py
```
Upon Backend B resuming operation on port 3002:
- nginx routes subsequent demonstrated requests across both backends once Backend B is restored.
- Traffic automatically redistributes in alternating round-robin pattern (`A -> B -> A -> B`).
- Normal baseline state is restored.
