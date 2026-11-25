# Submission checklist and final completeness audit

Compared against the supplied Computer Networks assignment (Sections 3, 6-9), original screenshots, PCAP and Phase 1 source. Updated 25 November 2026. **Evidenced** means supported by supplied historical artifacts; **historical** means retained Phase 1 record; **prepared** means repository material exists; **pending** requires live work. No claim of faculty acceptance or marks is made.

## Phase 1 foundation and whole-project constraints

| Requirement | Status and location | Qualification / action |
|---|---|---|
| Simple local platform, .test domain, fixed ports | Evidenced; source and architecture | Three Macs + Pi, not four Macs. Confirm faculty acceptance of Pi substitution if not previously agreed. No cloud/VLAN/NAT extension added. |
| Topology, machine roles, full inventory | Prepared Phase 2 architecture; historical Phase 1 inventory | Refresh all current IP/prefix/interface/MAC/gateway values before evaluation; Pi /19 is visible in E023. |
| Pairwise LAN reachability | Historical Phase 1 images; Phase 2 E001/E002 | Re-run all peer pairs for current deployment; no full refreshed Phase 2 matrix claimed. |
| app/api DNS records | Historical configs; Phase 2 templates and app evidence | app final target/TTL proven by E057; capture current api answer during rehearsal. api HTTPS SAN is not covered. |
| At least two other Macs use team DNS | Partial, E012 and E043 | Pranjal identified; E043 owner absent and scope-specific. Capture hostname + DNS settings on two identifiable client Macs. |
| Backend GET / and /api/status, X-Backend, LAN binding | Source preserved; historical/Phase 2 HTTP responses | Direct responses HTTP/1.0, edge HTTP/1.1. Unknown paths return bare 404. |
| Round-robin proxy and HTTPS | Evidenced, E016/E036/E044/E057 | No negotiated HTTP/2 claim; no -k in demonstration. |
| CA trust on every demo client | Historical setup; verified curl on shown clients | Check current certificates and trust on each live demo client; no supplied leaf certificate files. |
| Caching headers and 304 | Historical 304 image; Phase 2 headers | Shared fixed ETag is a simplified demonstration, not correct validation of distinct A/B bodies. |
| DNS/TCP/TLS protocol evidence | Phase 1 screenshots + Phase 2 PCAP | 32 frames dissected; TLS 1.3 certificate and HTTP content remain encrypted. |
| Five Phase 1 failure scenarios | Historical failure-tests and images | Preserve old addresses and B-down context; Phase 2 uses A-down. |
| Phase 1 checkpoint/viva | User reports Phase 1 completed | Repository does not independently establish grades or faculty sign-off. |

## Mandatory Phase 2 extensions

| Requirement | Status | Evidence / genuine remaining work |
|---|---|---|
| A: second resolver and matching records | Evidenced | E012/E020/E057; PCAP 1-2 |
| A: client continues with primary explicitly stopped | **Pending narrow evidence sequence** | Backup use is proven; paired primary stop-state + fresh client backup query is missing. Run 9A in demo runbook. |
| B: visible TTL, record change, old/new client answers | Evidenced with timing qualification | E045-E049; do not claim exact 120-second expiry. |
| B: immediate manual-flush change | Evidenced | E050; earlier E014 alone is insufficient. |
| C: edge-only backend access during demo | Evidenced | PF E004/E005 + probes E020-E022; Pi E027-E029 |
| C: backup and restore firewall state | Evidenced rollback, partial backup artifact | PF backup commands E004; E010/E052 rollback; full Pi pre-change backup file absent. Save one before the next test. |
| C: final policy | Rolled back | E054/E056 direct success; do not claim permanent isolation. |
| D: A stopped, B-only service, A/B recovery | Evidenced | E001/E002/E015-E019; passive handling, no general zero-downtime guarantee. |
| D: identify edge single point of failure | Prepared explanation | Architecture and report; shared host/LAN risks documented. |
| E: standby, trusted TLS, hostname cutover | Evidenced | E007/E008/E031-E038; --resolve preparation distinguished from hostname cutover. |
| E: simultaneous old-cache/new-client edge comparison | **Pending focused live proof** | General TTL test exists, but migration-specific concurrent comparison not isolated. Run 9D. |
| E: rollback to primary | Evidenced | E039-E042/E057; E040 is resolver disagreement. |
| E/C: combined isolation + migration | Not claimed | Intermediate allowlist adjustment absent. Reconstructed instructions stage separately or require new explicit standby allow rule and new evidence. |
| F: faculty-injected diagnosis | **Pending live evaluation** | Worksheet prepared; E053/E055/E054 is a separate real troubleshooting incident. |
| Individual viva / all-member participation | **Pending live evaluation** | Eleven-step runbook and viva prompts prepared; no fabricated results. |

## Repository deliverables

| Assignment deliverable | Repository location | State |
|---|---|---|
| Updated architecture | [architecture.md](architecture.md) | Prepared with phase distinction and current evidence |
| Configuration bundle | [Phase 2 configs](../configs/phase2/README.md) | Reconstructed templates, historical Phase 1 configs retained |
| TLS and launches | [TLS](tls-phase2.md), [setup/rollback](setup-rollback.md) | Prepared; private host material deliberately excluded |
| Backend source | [A](../backend-a/server.py), [B](../backend-b/server.py) | Preserved, syntax checked; limitations disclosed |
| Evidence folder | [Index](../evidence/phase2/README.md), gallery, manifests, hashes | 57 original uploads + original PCAP; Phase 1 originals retained |
| Phase 2 final report | [Markdown](phase2-report.md), [PDF](phase2-report.pdf) | Prepared; observations/interpretations/gaps separated |
| Final presentation | [Live demo runbook](demo-runbook.md) | All 11 assignment steps; no separate slide deck required by supplied sequence |
| Validation and audit | [validation.md](validation.md) | Actual local checks with limits |

## Final evaluation

The repository work can be completed and pushed while live evidence gaps remain. Priority before the evaluation slot: (1) paired primary-DNS-down/fresh-backup resolution, (2) two clearly identified client DNS configurations, (3) simultaneous migration cache comparison. During the same rehearsal, refresh inventory, confirm api DNS/current client trust and save the Pi firewall baseline. Confirm Pi substitution if approval is not already held. Then perform the faculty challenge and individual viva during evaluation.

The fixed ETag is an acknowledged implementation limitation; no production cache-correctness claim is made. If faculty requires strict representation validators, repair that separately with new validation and deployment evidence rather than rewriting old screenshots. No unsupported requirement is marked complete.
