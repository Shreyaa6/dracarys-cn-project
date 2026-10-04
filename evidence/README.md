# Packet Capture & Verification Evidence

This directory stores the official Wireshark packet captures, terminal verification logs, and empirical screenshots collected during live testing of the **Private Network Service Platform** (Team Dracarys).

All screenshots represent actual live network executions collected across the participating nodes on the `10.7.0.0/19` private network.

---

## 1. Evidence Directory Organization

| Subdirectory | Target Artifacts | Summary of Evidence Files |
| :--- | :--- | :--- |
| [`evidence/connectivity/`](connectivity/) | Network Layer ICMP ping traces | Pairwise ping matrices verifying full-mesh 0% packet loss. |
| [`evidence/dns/`](dns/) | Private DNS resolution & Wireshark records | Client DNS resolver configuration, successful `dig`, and UDP port 53 packet captures. |
| [`evidence/tcp/`](tcp/) | TCP handshakes & connection management | Three-way handshake (`SYN`, `SYN-ACK`, `ACK`) and full connection lifecycle on port 8443. |
| [`evidence/tls/`](tls/) | TLS 1.2 handshake & encryption records | Handshake parameters, SNI match, trusted curl verification, and encrypted Application Data frames. |
| [`evidence/load-balancing/`](load-balancing/) | Upstream proxy load distribution | 8-request terminal trace demonstrating round-robin alternation between `X-Backend: A` and `B`. |
| [`evidence/caching/`](caching/) | HTTP caching & conditional revalidation | `Cache-Control`, `ETag`, and conditional `304 Not Modified` empty-body response validation. |
| [`evidence/failures/`](failures/) | Fault injection and resilience proofs | Terminal outputs for the 5 injected failure scenarios (DNS timeouts, single backend down, 502, connection refused). |

---

## 2. Comprehensive Evidence Catalog

### 2.1 Connectivity Verification (`evidence/connectivity/`)
Direct Layer 3 ICMP echo verification confirming mutual IP reachability across all physical hosts with 0% packet loss:

- [ping-pranjal-to-machines.jpeg](connectivity/ping-pranjal-to-machines.jpeg):
  - **Terminal / Host**: Pranjal Mac (`10.7.26.65`)
  - **What it Proves**: Successful pairwise ping execution from Pranjal Mac to Shreya Mac (`10.7.3.26`), Meghna Mac (`10.7.22.237`), and Raspberry Pi (`10.7.23.235`), with 3 packets transmitted, 3 received, and 0.0% packet loss to every host.
- [ping-shreya-to-machines.jpeg](connectivity/ping-shreya-to-machines.jpeg):
  - **Terminal / Host**: Shreya Mac (`10.7.3.26`)
  - **What it Proves**: Successful pairwise ping execution from Shreya Mac to Meghna Mac (`10.7.22.237`) and Raspberry Pi (`10.7.23.235`), confirming 3 packets transmitted, 3 received, and 0.0% packet loss.
- [ping-meghna-to-pi.jpeg](connectivity/ping-meghna-to-pi.jpeg):
  - **Terminal / Host**: Meghna Mac (`10.7.22.237`)
  - **What it Proves**: Successful pairwise ping execution from Meghna Mac to Raspberry Pi (`10.7.23.235`), confirming 3 packets transmitted, 3 received, and 0.0% packet loss.

---

### 2.2 DNS Resolution Evidence (`evidence/dns/`)
Validates private name resolution using `dnsmasq` on Shreya Mac (`10.7.3.26`):

- [dns-success.jpeg](dns/dns-success.jpeg):
  - **What it Proves**: Confirms the client Wi-Fi DNS resolver is configured to `10.7.3.26` via `networksetup -getdnsservers Wi-Fi`. Shows `dig app.dracarys.test` returning an `A` record pointing to `10.7.26.65` from `SERVER: 10.7.3.26#53`.
- [dns-wireshark-response.jpeg](dns/dns-wireshark-response.jpeg):
  - **What it Proves**: Wireshark capture of Packet 4 in `dracarys-taskG.pcap` showing the DNS response packet over UDP. Displays Source IP `10.7.3.26` (UDP server port 53) to Destination IP `10.7.26.65` (UDP client ephemeral port 51219).
- [dns-wireshark-answer.jpeg](dns/dns-wireshark-answer.jpeg):
  - **What it Proves**: Detailed Wireshark packet dissection expanding the DNS Answer section: `app.dracarys.test: type A, class IN, addr 10.7.26.65`.

---

### 2.3 TCP Handshake & Connection Evidence (`evidence/tcp/`)
Validates Layer 4 reliable transport on nginx HTTPS port 8443:

- [tcp-three-way-handshake.jpeg](tcp/tcp-three-way-handshake.jpeg):
  - **What it Proves**: Discrete 3-way TCP handshake packets on port 8443:
    1. Client ephemeral port `50041 -> 8443 [SYN] Seq=0`
    2. Edge server port `8443 -> 50041 [SYN, ACK] Seq=0 Ack=1`
    3. Client port `50041 -> 8443 [ACK] Seq=1 Ack=1`
- [tcp-connection-overview.jpeg](tcp/tcp-connection-overview.jpeg):
  - **What it Proves**: Full TCP connection lifecycle filtered by `tcp.port == 8443`, showing transmission of all 44 captured packets including data segments, duplicate ACKs/retransmissions, and graceful two-way connection termination (`FIN, ACK`).

---

### 2.4 TLS Architecture & Verification Evidence (`evidence/tls/`)
Validates TLS termination and cryptographic security at the edge proxy:

- [tls-handshake.jpeg](tls/tls-handshake.jpeg):
  - **What it Proves**: Wireshark filter `tls.handshake || tls.record.content_type == 20` exposing all discrete stages of the TLS 1.2 handshake: `ClientHello` (with SNI `app.dracarys.test`), `ServerHello`, `Certificate`, `ServerKeyExchange` (ECDHE), `ServerHelloDone`, `ClientKeyExchange`, and `ChangeCipherSpec`.
- [tls-encrypted-application-data.jpeg](tls/tls-encrypted-application-data.jpeg):
  - **What it Proves**: Wireshark filter `tls.app_data` confirming that following cipher negotiation, HTTP requests and responses travel strictly inside encrypted `Application Data` records (e.g. 172-byte request and 325-byte response). HTTP paths, headers, and payloads cannot be inspected or intercepted in plaintext.
- [tls-curl-verified.jpeg](tls/tls-curl-verified.jpeg):
  - **What it Proves**: Terminal trace of `curl --tls-max 1.2 -v https://app.dracarys.test:8443/api/status` executing without the insecure `-k` flag. Explicitly demonstrates:
    - Subject: `CN=app.dracarys.test`
    - SubjectAltName: host `app.dracarys.test` matched cert's `app.dracarys.test`
    - Issuer: `CN=Dracarys Local CA`
    - Verification status: `SSL certificate verify ok`
    - Cipher negotiated: `TLSv1.2 / ECDHE-RSA-CHACHA20-POLY1305`
    - Successful HTTP/1.1 200 OK response with `X-Backend: B`.

> [!NOTE]
> **Capture Context for Wireshark TLS Trace**:
> The Wireshark TLS capture was recorded locally on the nginx edge Mac (`10.7.26.65`), capturing traffic between the local test client and the local nginx listener. Therefore, the capture displays `10.7.26.65` as both source and destination IP address on the loopback/internal bridge interface. This reflects edge host internal socket traffic, not cross-machine LAN traffic.

---

### 2.5 Round-Robin Load Balancing Evidence (`evidence/load-balancing/`)
Validates reverse proxy upstream load distribution:

- [load-balancing-ab.jpeg](load-balancing/load-balancing-ab.jpeg):
  - **What it Proves**: Terminal loop executing 8 consecutive requests to `https://app.dracarys.test:8443/api/status`. Shows nginx distributing traffic in strict alternating round-robin order across both backend nodes (`B -> A -> B -> A -> B -> A -> B -> A`), with all requests returning `HTTP/1.1 200 OK`.

---

### 2.6 Caching & Conditional Revalidation Evidence (`evidence/caching/`)
Validates RFC 7234 and RFC 7232 HTTP/1.1 caching headers:

- [etag-304-not-modified.jpeg](caching/etag-304-not-modified.jpeg):
  - **What it Proves**: Terminal loop executing 4 consecutive conditional requests with `If-None-Match: "dracarys-v1"`. Demonstrates that requests return `HTTP/1.1 304 Not Modified` with `ETag: "dracarys-v1"` and `Cache-Control: max-age=60`, alternating between `X-Backend: A` and `B`, with no response body.

---

### 2.7 Failure & Resilience Demonstrations (`evidence/failures/`)
Empirical validation of system behavior under 5 injected failure scenarios:

- [failure-1-wrong-dns-server.jpeg](failures/failure-1-wrong-dns-server.jpeg):
  - **Scenario**: Wrong DNS Server IP configured (`192.0.2.53`).
  - **What it Proves**: DNS query `dig +time=2 +tries=1 app.dracarys.test` times out with `connection timed out; no servers could be reached`. Meanwhile, Layer 3 direct IP ping (`ping -c 3 10.7.26.65`) immediately succeeds with 0.0% packet loss, proving architectural decoupling between DNS resolution and IP routing.
- [failure-2-wrong-dns-record.jpeg](failures/failure-2-wrong-dns-record.jpeg):
  - **Scenario**: DNS record pointed to non-routable address (`192.0.2.123`).
  - **What it Proves**: DNS query succeeds rapidly (`A 192.0.2.123`), but subsequent HTTPS connection attempt (`curl --connect-timeout 3 -v https://app.dracarys.test:8443/api/status`) times out with `curl: (28) Timeout was reached`.
- [failure-3-one-backend-down.jpeg](failures/failure-3-one-backend-down.jpeg):
  - **Scenario**: Backend B stopped on Raspberry Pi.
  - **What it Proves**: With Backend B unavailable, the demonstrated requests continued returning HTTP 200 from Backend A.
- [failure-4-both-backends-down-502.jpeg](failures/failure-4-both-backends-down-502.jpeg):
  - **Scenario**: Both Backend A and Backend B stopped.
  - **What it Proves**: An HTTPS request to `https://app.dracarys.test:8443/api/status` returns `HTTP/1.1 502 Bad Gateway` from nginx.
- [failure-5-wrong-port.jpeg](failures/failure-5-wrong-port.jpeg):
  - **Scenario**: HTTPS connection targeted to unbound port `8444`.
  - **What it Proves**: An HTTPS request to port 8444 failed with connection refused and curl error 7.
