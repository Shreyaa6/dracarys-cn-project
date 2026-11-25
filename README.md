# Dracarys - Private Network Service Platform

Computer Networks course project · Phase 1 foundation + Phase 2 hardening and recovery
Deployment evidence: **24 November 2026** · Repository finalization: **25 November 2026**

A local DNS → TCP → TLS → nginx → Python service on three Macs and a Raspberry Pi. Phase 2 adds backup DNS, TTL experiments, backend isolation, passive upstream failover and manual DNS-based edge migration. The application remains deliberately small.

**Submission status:** documentation and supplied evidence are organized. The evidence supports most Phase 2 demonstrations, with explicit qualifications. Primary-DNS-stop proof, a strict simultaneous cached-client/new-client migration comparison, and second-client ownership/configuration confirmation remain open. The faculty challenge and individual viva are pending live evaluation. See the [submission checklist](docs/submission-checklist.md).

## Start here

| Deliverable | Location |
|---|---|
| Phase 2 final report | [Canonical Markdown](docs/phase2-report.md) · [PDF](docs/phase2-report.pdf) |
| Current architecture and protocol flow | [Architecture](docs/architecture.md) |
| All 57 original screenshots | [Evidence index](evidence/phase2/README.md) · [Offline gallery](evidence/phase2/gallery.html) |
| Original 32-frame capture | [PCAP](evidence/phase2/pcap/client-dns-https.pcap) · [Frame analysis](docs/packet-capture-analysis.md) |
| Reconstructed deployment configurations | [Phase 2 bundle](configs/phase2/README.md) |
| Installation, staged tests and recovery | [Setup / rollback](docs/setup-rollback.md) · [Standby TLS](docs/tls-phase2.md) |
| Final demonstration and viva | [11-step runbook](docs/demo-runbook.md) |
| Completion and verification | [Checklist](docs/submission-checklist.md) · [Validation](docs/validation.md) |
| Phase 1 history | [Original README](README-phase1.md) · [Architecture](docs/architecture-phase1.md) · [Failure tests](docs/failure-tests.md) · [Evidence](evidence/README.md) |

GitHub displays the Markdown index directly. To use the gallery, clone/download the repository and open `evidence/phase2/gallery.html` locally.

## Phase 2 device map

| Device | IPv4 | Services |
|---|---|---|
| Shreya Mac | 10.7.3.26 | Primary DNS UDP/TCP 53; client |
| Pranjal Mac | 10.7.12.197 | Primary nginx 1.31.6, HTTP 8080 / HTTPS 8443; client |
| Meghna Mac | 10.7.30.248 | Backend A TCP 3001; backup DNS 53; temporary standby nginx 1.31.10, 8080/8443 |
| Raspberry Pi (`isro@isro-desktop`) | 10.7.6.30 | Backend B TCP 3002 on wlan0 |

Normal `app.dracarys.test` answer: **10.7.12.197, TTL 30 on both DNS servers** (E057). Migration temporarily used 10.7.30.248. The separate `ttl.dracarys.test` experiment used TTL 120. Do not reuse old Phase 1 edge/backend IPs `.26.65`, `.22.237`, `.23.235` for Phase 2.

```text
                    +--> Shreya primary DNS .3.26:53
Client -- DNS ------|
                    +--> Meghna backup DNS .30.248:53
Client -- HTTPS ---> Pranjal primary edge .12.197:8443
                      |-- HTTP --> Meghna A .30.248:3001
                      +-- HTTP --> Pi B .6.30:3002

Manual DNS cutover: client --> Meghna standby .30.248:8443
                               |-- HTTP --> local A 127.0.0.1:3001
                               +-- HTTP --> Pi B .6.30:3002
```

## Run and verify

Use the [full host-specific setup](docs/setup-rollback.md) before deploying. On Meghna, from the clone root, run `python3 backend-a/server.py`; on the Pi run `python3 backend-b/server.py`. Each listens on IPv4 `0.0.0.0` at its fixed port. Install the appropriate **Phase 2** DNS/nginx template, use the existing private certificates on the intended hosts, and configure client trust and DNS.

From a configured client on the project LAN:

```bash
dig @10.7.3.26 app.dracarys.test A +noall +answer
dig @10.7.30.248 app.dracarys.test A +noall +answer
curl -v --connect-timeout 5 --max-time 15 https://app.dracarys.test:8443/api/status
for i in {1..6}; do
  curl -sS -D - -o /dev/null --max-time 15 https://app.dracarys.test:8443/api/status
 done
```

Expected normal behavior: trusted TLS without `-k`, HTTP/1.1 200, `X-Edge: primary`, responses from both A and B. These are reproduction expectations; the historical evidence is linked in the report. Direct Python responses are HTTP/1.0. Offering h2 does not mean HTTP/2 was negotiated.

Firewall isolation was **rolled back** after testing. Final observed state permits direct backend access. The edge migration is manual, backend failover is passive, and shared host roles remain correlated failure risks. The unchanged backend's shared fixed ETag is a simplified conditional-request demonstration, not representation-correct caching across different A/B bodies.

## Team

| Member | Enrollment | Recorded responsibility |
|---|---|---|
| Shreya Narayani | 2401020067 | Primary DNS / client; Pi SSH access in evidence |
| Meghna Nair | 2401010274 | Backend A, backup DNS and temporary standby edge host |
| Pranjal Shukla | 2401010335 | Primary edge, TLS and client testing |
| Ritesh Kumar | 2401010384 | Team member; individual implementation attribution not supplied |

Device roles are evidence-based; they are not a complete individual contribution ledger. Each member must understand the whole system for viva.

Public CA certificate: [tls/dracarys-ca.crt](tls/dracarys-ca.crt). Private keys and session keylogs must never be committed. Historical Phase 1 configuration files remain unchanged; all Phase 2 templates are under `configs/phase2/`.
