# Packet Capture & Verification Evidence

This directory stores the official Wireshark packet captures (`.pcap` / `.pcapng`), terminal logs, and verification artifacts collected during live testing of the **Private Network Service Platform** (Team Dracarys).

> [!NOTE]
> In accordance with academic integrity and evaluation rules, this repository does not include placeholder or fabricated capture files. Each designated subdirectory contains a `.gitkeep` placeholder for storing the actual raw captures collected during live network runs.

---

## 1. Directory Organization

| Subdirectory | Target Artifacts |
| :--- | :--- |
| [`evidence/dns/`](file:///Users/shreyanarayani/dracarys-cn-project/evidence/dns) | Wireshark captures of UDP port 53 query/response transactions (`app.dracarys.test`). |
| [`evidence/tcp/`](file:///Users/shreyanarayani/dracarys-cn-project/evidence/tcp) | Three-way TCP handshake (`SYN`, `SYN-ACK`, `ACK`) and connection teardown. |
| [`evidence/tls/`](file:///Users/shreyanarayani/dracarys-cn-project/evidence/tls) | TLS handshake records, certificate exchange, and encrypted Application Data frames. |
| [`evidence/load-balancing/`](file:///Users/shreyanarayani/dracarys-cn-project/evidence/load-balancing) | Terminal session logs showing round-robin alternation between `X-Backend: A` and `X-Backend: B`. |
| [`evidence/caching/`](file:///Users/shreyanarayani/dracarys-cn-project/evidence/caching) | Terminal session logs showing `Cache-Control`, `ETag`, and conditional `304 Not Modified`. |
| [`evidence/failures/`](file:///Users/shreyanarayani/dracarys-cn-project/evidence/failures) | Terminal outputs and captures for the 5 injected failure scenarios (e.g. backend failover). |

---

## 2. Documented Observations from Actual Captures

### 2.1 DNS Resolution Capture (`evidence/dns/`)
Captured across client interface querying authoritative DNS server:
- **Transaction Flow**:
  - Source: `10.7.26.65` (Client)
  - Destination: `10.7.3.26:53` (Shreya Mac / `dnsmasq`)
  - Protocol: `DNS (UDP)`
- **Query Record**:
  - Standard Query `A app.dracarys.test`
- **Response Record**:
  - Standard Query Response `app.dracarys.test: type A, class IN, addr 10.7.26.65`
  - Configured TTL: `0`

### 2.2 TCP Handshake Capture (`evidence/tcp/`)
Because testing was executed directly from the edge host Mac, both endpoint IP addresses are captured as `10.7.26.65`:
- **Client Ephemeral Port**: `50041`
- **Edge Listening Port**: `8443`
- **Three-Way Handshake**:
  1. `10.7.26.65:50041 -> 10.7.26.65:8443 [SYN] Seq=0 Win=65535`
  2. `10.7.26.65:8443 -> 10.7.26.65:50041 [SYN, ACK] Seq=0 Ack=1 Win=65535`
  3. `10.7.26.65:50041 -> 10.7.26.65:8443 [ACK] Seq=1 Ack=1`

### 2.3 TLS 1.2 Handshake & Encryption Verification (`evidence/tls/`)
To inspect all discrete cryptographic stages in Wireshark, testing was conducted with TLSv1.2:
1. **ClientHello**:
   - SNI (Server Name Indication): `app.dracarys.test`
   - Client Random, supported cipher suites
2. **ServerHello**:
   - Agreed Cipher Suite (e.g., `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384`)
3. **Certificate**:
   - Server certificate chain issued by `Dracarys Local CA`
4. **Server Key Exchange / Server Hello Done**:
   - Elliptic Curve Diffie-Hellman parameters signed by server private key
5. **Client Key Exchange**:
   - Client ECDH public parameter
6. **ChangeCipherSpec**:
   - Signals transition to symmetric AEAD cipher
7. **Encrypted Handshake Message**:
   - Handshake authentication
8. **TLS Application Data**:
   - **Critical Observation**: Once `ChangeCipherSpec` is exchanged, all application protocol data (HTTP request line, headers such as `X-Backend`, `If-None-Match`, and JSON response payloads) are fully encrypted within TLS Application Data records.
   - Wireshark is unable to parse plaintext HTTP streams, proving that private traffic over `8443` is secure against passive eavesdropping.

---

## 3. Placement Instructions for Team Evidence

When saving capture files and terminal transcripts into this repository:
1. Export Wireshark sessions as standard `.pcap` or `.pcapng` into the appropriate subfolder (e.g., `evidence/dns/dns_query_response.pcapng`).
2. Save raw terminal execution outputs as `.txt` or `.log` into their corresponding folders.
3. Verify that **NO private keys or credentials** are included in any packet payload or log file before committing.
