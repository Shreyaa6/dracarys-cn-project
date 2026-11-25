# Dracarys - Phase 2 Final Report

**Computer Networks: Private Network Service Platform**
Evidence collected: 24 November 2026 · Report finalized: 25 November 2026
Team: Shreya Narayani, Meghna Nair, Pranjal Shukla and Ritesh Kumar

## 1. Scope and completion boundary

Phase 2 extends the existing local DNS, TLS reverse proxy and two Python backends. This report covers extensions A-F, observed resilience tests, recovery, troubleshooting and learning. It is based on original screenshots E001-E057, the supplied 32-frame packet capture and the existing Phase 1 repository. No lab outcomes were generated during repository finalization. Local file/configuration checks are documented separately in [validation](validation.md).

The evidence demonstrates backup DNS availability/use, TTL cache persistence and manual flushing, backend isolation and rollback, A-down/B-only service with recovery, and manual edge migration. It does not conclusively pair primary-DNS shutdown with a subsequent backup answer, identify the second client in E043, or isolate simultaneous old-cache versus fresh-client edge traffic during migration. Extension F and individual viva remain pending live evaluation. These limits do not invalidate the supported observations, but prevent marking all mandatory evaluation requirements complete.

The [complete evidence index](../evidence/phase2/README.md) links every ID to its original. The [offline gallery](../evidence/phase2/gallery.html) provides full-resolution access. E036/E037 are duplicate uploads, not two independent trials. Timestamps are those visible on hosts; clocks are not assumed synchronized.

## 2. Changes from Phase 1

Phase 1 established a private .test domain, nginx TLS termination and round-robin A/B responses, HTTP conditional requests, packet screenshots and five controlled failures. Its original README, architecture, configuration files and 18 evidence images remain available in the repository and Git history at baseline a933e2c. The old edge/backend addresses are historical: 10.7.26.65, 10.7.22.237 and 10.7.23.235.

Phase 2 uses Shreya Mac 10.7.3.26 for primary DNS; Pranjal Mac 10.7.12.197 for primary nginx and testing; Meghna Mac 10.7.30.248 for Backend A :3001, backup DNS :53 and temporary standby nginx :8443; and Raspberry Pi 10.7.6.30 for Backend B :3002. E020 explicitly prints the primary edge IP, E001/E005 identify Meghna, and E023 identifies the Pi and /19 prefix. Current Mac MAC addresses/default gateways were not independently re-established by the supplied Phase 2 evidence.

The normal app record returns 10.7.12.197 with TTL 30 from both resolvers (E057). Cutover temporarily uses 10.7.30.248. A separate ttl.dracarys.test record uses TTL 120 in the stronger repeat. nginx adds X-Edge labels and passive retry settings. Python responses are HTTP/1.0; edge responses are HTTP/1.1, with TLS 1.3 visible in later curl sessions. Offering h2 is not evidence of HTTP/2 negotiation.

## 3. Method and evidence discipline

Tests use direct DNS queries to compare server configuration, system-resolver lookups to observe client caching, hostname-based curl to verify application paths, X-Backend/X-Edge headers to identify serving components, and host listener/firewall inspection to establish fault state. A successful direct dig does not prove system-resolver failover. A --resolve request preserves TLS hostname checking while bypassing normal DNS; it is useful preparation but not DNS cutover proof. A timeout alone does not identify a firewall as the cause.

The configuration bundle is reconstructed from visible configuration commands and historical source, not exported verbatim from every host. Test-specific commands and expected outputs in the runbook are reproduction instructions, not new historical observations. The report cites screenshot IDs; the machine-readable manifest supplies original filenames, hashes and paths. Original pixels take precedence over OCR transcription errors.

## 4. Extension A - Backup DNS resolver

**Method.** Configure dnsmasq on Meghna's Mac with matching app/api records, then configure client DNS lists with primary 10.7.3.26 and backup 10.7.30.248. Query the backup explicitly, inspect client settings and capture actual project DNS traffic. The assignment additionally requires stopping primary dnsmasq and proving continued resolution.

**Observed result and evidence.** E012 shows Pranjal's Wi-Fi DNS list containing both servers and a successful backup reply. E020 shows DNS traffic reaching the backup and identifies Pranjal's IP. The original PCAP frames 1-2 show Shreya 10.7.3.26:53658 asking backup 10.7.30.248:53 for app.dracarys.test and receiving 10.7.12.197, TTL 30. E043 shows a domain-specific resolver with both servers, but its owner is not visible. This establishes backup configuration, availability and actual use.

**Recovery and qualification.** E057 confirms both resolvers finally agree on the primary edge. No explicit primary-stop record paired with the subsequent backup response is present. A DNS query from the primary-DNS host does not establish its daemon state. A focused live stop → listener check → uncached client lookup/capture → restart sequence remains required. Confirm two identifiable client Macs have the intended DNS settings; scoped resolution should not be described as global Wi-Fi configuration.

**Learning.** Redundant DNS and resilient applications solve different failures. A working backup can return an address even when the application is down, and an already cached address can permit HTTPS while DNS is unavailable. Resolver selection is client behavior, not guaranteed sequential use of a list. A valid failover demonstration must show the stopped service and a fresh query reaching backup, rather than relying only on a cached lookup.

## 5. Extension B - TTL and controlled record change

**Method.** Use ttl.dracarys.test so the experiment does not confuse normal app routing. Configure TTL 120 on both resolvers, flush the initial client cache, start timestamped system lookups, change the record on both servers, and compare fresh server replies with cached client answers. Repeat with a manual flush after restoring the server record.

**Observed sequence.** E045 shows both servers returning 10.7.12.197 with TTL 120 at 19:36:11. E046/E049 show the client loop initially returning that old address from 19:38:20. E009 shows temporary resolver disagreement at 19:39:02; this is configuration skew. E047 shows both resolvers giving 10.7.30.248 by 19:39:38. E048 shows the client retaining 10.7.12.197 through 19:40:52 and returning 10.7.30.248 at 19:40:57.

E050 is the strongest flush evidence: both servers have reverted to 10.7.12.197 while the client still returns 10.7.30.248; after the flush, a lookup at 19:45:10 immediately returns 10.7.12.197. Earlier E011-E014 use TTL 30, but E014 already has matching before/after answers, so it cannot alone demonstrate a flush-caused transition.

**Recovery and qualification.** Restore the separate ttl record to 10.7.12.197 on both servers and verify agreement; E050/E051 document restoration-related commands. Leave normal app at TTL 30 (E057). The observations support cache persistence and eventual refresh, not an exactly measured 120-second countdown. Polling, resolver refresh behavior and non-synchronized host timestamps constrain precision.

**Learning.** DNS changes take effect at the server before every client uses them. TTL bounds reuse of a cached answer, but the observed time depends on when that client last acquired it. Manual flushing can shorten the wait for a controlled test. Comparing two unequal server answers diagnoses record synchronization first; only after server agreement can an old system-resolver answer be interpreted as cache persistence with confidence.

## 6. Extension C - Backend service isolation

**Method.** Preserve current firewall state. On Meghna, invoke a PF anchor that allows primary edge 10.7.12.197 to TCP 3001 and drops other IPv4 LAN clients. On the Pi, place a TCP 3002 INPUT jump into DRACARYS_BACKEND, returning loopback traffic, accepting primary edge on wlan0 and dropping others. Compare direct requests from the edge and a separate client with verified HTTPS through nginx.

**Observed result and evidence.** E003 shows PF's initial disabled state; E004 shows backup and syntax validation; E005 shows enablement and loaded rules. E020 records an edge-to-A HTTP 200, while E021/E022 show client direct-A timeout and HTTPS success. E023-E026 document pre-existing Pi rules. E027 shows edge-to-B HTTP 200, E028 shows direct-B timeout with HTTPS success, and E029 shows six accepted and six dropped packets in the project chain. The combined rules, counters and paired probes support isolation more strongly than a timeout alone.

**Recovery and qualification.** E010 restores the PF configuration, clears the project anchor and disables PF after releasing its enable reference. E052 removes only the Pi project chain, preserving ts-input. E054/E056 subsequently show direct backend HTTP 200. Thus isolation was a reversible demonstration, not the final running policy. A full Pi pre-change backup file is not supplied, despite pre-change rule screenshots. Future runs must save one before editing. The original primary-only Pi allowlist would block standby-to-B; the intermediate adjustment is not recorded, so migration is a separate stage.

**Learning.** A reverse proxy hides backend addresses in normal use but does not itself enforce access control. Firewall rules must specify the trusted source and service port, be ordered before competing accepts, and be verified from both allowed and denied sources. Rollback matters because broad flushes can break unrelated host networking. IPv4 service isolation should not be claimed as universal protection for hypothetical IPv6 listeners.

## 7. Extension D - Backend high availability

**Method.** Configure passive failure handling with max_fails=1, fail_timeout=10s, connect timeout 2s, read/send timeouts 5s and two permitted upstream tries. Establish A/B responses, stop A, verify the listener is absent, repeat requests through the primary edge, then restart A and observe recovery.

**Observed result and evidence.** E015/E016 show configuration validation and a six-request A/B baseline. E001 shows A stopped and no listener; E017 shows ten B-only HTTP 200 responses. E002 shows A restarted. E018/E019 show B-only requests transitioning back to A/B distribution. This is the assignment's A-down test, distinct from the historical Phase 1 B-down demonstration.

**Recovery and qualification.** Restart A with the existing server.py and wait for passive retry eligibility; verify both headers reappear. The samples demonstrate successful requests during the observed outage, not a statistical availability guarantee or measured zero downtime. nginx detects failure on requests; there is no active health checker. The primary edge itself remains a single point of failure until manual migration.

**Learning.** Backend redundancy preserves service only when the proxy recognizes failures and has a healthy alternative. Retry limits and timeouts trade detection speed against unnecessary failures under slow networking. A recovered backend can rejoin without a DNS change because the edge address remains stable. Redundant backends do not eliminate failure of the edge, shared LAN or a host carrying several roles.

## 8. Extension E - Controlled edge migration

**Method.** Install standby nginx on Meghna, using local 127.0.0.1:3001 for A and Pi 10.7.6.30:3002 for B. Generate a standby key/CSR privately and have the existing CA holder sign a certificate for app.dracarys.test. Verify chain, SAN and matching key. Test selected standby connectivity before editing both DNS servers. Then use normal hostname requests and stop primary nginx.

**Observed result and evidence.** E007/E008 show standby setup, matching modulus hashes and successful nginx syntax/start. E030/E031 show key permissions and certificate signing/verification; they contain filenames, not private-key contents. E032/E033 prove preparatory standby TLS and A/B service using --resolve. E034 shows the primary target before cutover. E035 changes both app answers to 10.7.30.248, TTL 30. E036/E037 show hostname-based TLS verification and HTTP 200 without --resolve. E038 shows primary nginx stopped, no edge listeners in the displayed check, and six hostname requests still served via standby A/B.

**Recovery and qualification.** E039 restarts and checks primary using --resolve. E040 shows temporary resolver disagreement during rollback; E041 shows convergence to 10.7.12.197 and E042 shows hostname requests reaching primary again. E057 is the final app/DNS check. A strict simultaneous cached-old-client versus fresh-new-client comparison was not isolated. The standalone TTL test supports the general cache mechanism but does not replace that migration-specific observation. The firewall policy transition allowing standby-to-Pi is also not shown.

**Learning.** DNS cutover can move service without changing the URL, provided the new edge is ready and trusted for the same hostname. Cached clients may continue using the old edge, so controlled migration should keep both edges available during overlap. Updating both resolver records and observing normal hostname connections is essential. This deployment demonstrates manual recovery, not automatic edge HA; Meghna's combined standby/DNS/backend roles introduce correlated risk.

## 9. Extension F - Faculty troubleshooting challenge

**Status: pending live evaluation.** No supplied image establishes a faculty-injected fault. The [runbook](demo-runbook.md) includes a worksheet for timestamp, symptom, hypothesis, DNS/TCP/TLS/application probes, diagnosis, fix and recovery. During evaluation, explain reasoning aloud and record genuine outputs, including incomplete diagnosis if applicable.

**Authentic separate incident.** E053 shows a direct Backend B connection failure after firewall rollback. E055 shows no listener on :3002 and a server.py restart. E054 then returns HTTP/1.0 200 from B. The evidence supports application-listener diagnosis rather than blaming a firewall that had already been removed. E001/E002 also show binary-looking requests rejected with HTTP 400 by the plain HTTP backend; TLS sent to an HTTP port is a plausible inference, not a proven matching client command.

**Recovery and qualification.** The observed B incident recovered by restarting the backend, followed by a direct HTTP probe. It must not be relabeled as the faculty challenge. The final challenge outcome and individual viva cannot be completed through repository editing.

**Learning.** Diagnose one layer at a time: confirm names and resolver agreement, then reachability/listeners, then certificate trust and TLS, then HTTP/upstream state. A successful lower-layer check narrows the search without proving higher layers work. Keep competing hypotheses until evidence eliminates them; a refusal, timeout and 502 can point to different paths even when users describe all three as “the site is down.”

## 10. Packet evidence and protocol interpretation

The original capture contains 32 Ethernet frames (8,226 bytes), independently dissected with tshark 4.6.8. Frames 1-2 show DNS via backup, 3-5 the TCP handshake, 6 ClientHello and 8 ServerHello selecting TLS 1.3. Frame 10 is a compatibility ChangeCipherSpec. Encrypted outer type-23 records follow. Frames 28 and 30-32 show graceful FIN/ACK closure. tshark labels frames 13 and 15 as spurious retransmissions; that classification does not establish the underlying loss or capture cause.

The DNS socket pair is 10.7.3.26:53658 ↔ 10.7.30.248:53. The HTTPS pair is 10.7.3.26:63203 ↔ 10.7.12.197:8443. TCP sequence/acknowledgement numbers and advertised windows support explaining ordered delivery, retransmission and flow control. TLS 1.3 encrypts certificate/most handshake data after ServerHello; no session keylog was supplied. HTTP status, X-Backend and successful certificate validation are established by curl screenshots such as E036/E044, not read from encrypted PCAP payloads. See [frame notes](packet-capture-analysis.md).

## 11. Final state, limitations and next evidence

At the final recorded check, both app records point to primary 10.7.12.197 at TTL 30, and six primary-edge requests show both backends (E057). Direct backend access succeeds after firewall rollback (E054/E056). Standby service shutdown is not established; restoration of primary routing should not be confused with proof that every temporary service was stopped.

The existing shared fixed ETag is a simplified 304 demonstration: A/B response bodies differ while their strong validator is identical. Backend source is preserved to match the historical deployment. This limitation is documented instead of retroactively claiming standards-complete caching. No HTTP/2, automatic edge takeover, permanent isolation, full current host inventory or unrecorded faculty result is claimed.

Before evaluation, collect the narrow primary-DNS-stop failover sequence, identify/configure two client Macs, capture the simultaneous migration cache comparison, refresh current host inventory and perform the full live demonstration. Retain a real Pi firewall backup for that run. Confirm the Pi hardware substitution if faculty approval is not already recorded. Extension F and the viva are evaluation-time work. The [submission checklist](submission-checklist.md) maps these qualifications to the assignment.
