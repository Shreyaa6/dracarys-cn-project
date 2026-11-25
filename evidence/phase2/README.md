# Phase 2 evidence index

Original observations: 24 November 2026. IDs are inventory IDs, not chronological order. All 57 original uploads are retained byte-for-byte, including identical E036/E037. Original names, size and full SHA-256 are in [manifest.json](manifest.json) and [manifest.csv](manifest.csv). OCR is searchable assistance, not authoritative evidence.

[Offline gallery](gallery.html) · [Packet capture](pcap/client-dns-https.pcap) · [Packet analysis](../../docs/packet-capture-analysis.md) · [Final report](../../docs/phase2-report.md)

| ID | Topic | Observation and limits | Original filename |
|---|---|---|---|
| [E001](screenshots/baseline/E001.png) | baseline | Meghna IP, ping checks, Backend A logs and stop; no listener after stop | Screenshot 2026-11-24 at 3.40.58 PM.png |
| [E002](screenshots/backend-ha/E002.png) | backend-ha | Backend A restarted after stopped-listener check | Screenshot 2026-11-24 at 3.42.59 PM.png |
| [E003](screenshots/isolation/E003.png) | isolation | PF initial disabled state and original rules | Screenshot 2026-11-24 at 3.49.59 PM.png |
| [E004](screenshots/isolation/E004.png) | isolation | PF backup, edge allow/client block rules, syntax validation | Screenshot 2026-11-24 at 6.14.22 PM.png |
| [E005](screenshots/isolation/E005.png) | isolation | PF enabled and dracarys anchor rules displayed | Screenshot 2026-11-24 at 6.18.34 PM.png |
| [E006](screenshots/edge-migration/E006.png) | edge-migration | Pre-install nginx/listener check on Meghna Mac | Screenshot 2026-11-24 at 6.46.58 PM.png |
| [E007](screenshots/edge-migration/E007.png) | edge-migration | Standby nginx installation, CSR and matching certificate/key modulus hashes | Screenshot 2026-11-24 at 6.58.47 PM.png |
| [E008](screenshots/edge-migration/E008.png) | edge-migration | Standby nginx full configuration and successful syntax/start | Screenshot 2026-11-24 at 7.00.31 PM.png |
| [E009](screenshots/ttl/E009.png) | TTL | Backup TTL 120 change; temporary differing resolver answers | Screenshot 2026-11-24 at 7.39.04 PM.png |
| [E010](screenshots/rollback/E010.png) | rollback | PF configuration restored, anchor cleared and PF disabled | Screenshot 2026-11-24 at 8.09.06 PM.png |
| [E011](screenshots/ttl/E011.jpeg) | TTL | Early TTL 30 system-resolver loop returning old IP | WhatsApp Image 2026-11-24 at 15.30.25.jpeg |
| [E012](screenshots/backup-dns/E012.jpeg) | backup-dns | Backup DNS response and both Wi-Fi DNS servers configured | WhatsApp Image 2026-11-24 at 15.31.17.jpeg |
| [E013](screenshots/ttl/E013.jpeg) | TTL | Early TTL 30 new answers from both resolvers and system lookup | WhatsApp Image 2026-11-24 at 15.33.25.jpeg |
| [E014](screenshots/ttl/E014.jpeg) | TTL | Early manual flush after answer already changed; weaker than E050 | WhatsApp Image 2026-11-24 at 15.35.06.jpeg |
| [E015](screenshots/backend-ha/E015.jpeg) | backend-ha | Primary nginx passive-failure/retry configuration and syntax validation | WhatsApp Image 2026-11-24 at 15.38.12.jpeg |
| [E016](screenshots/backend-ha/E016.jpeg) | backend-ha | Baseline six A/B HTTP 200 responses via primary | WhatsApp Image 2026-11-24 at 15.39.40.jpeg |
| [E017](screenshots/backend-ha/E017.jpeg) | backend-ha | Ten B-only HTTP 200 responses during A outage | WhatsApp Image 2026-11-24 at 15.42.07.jpeg |
| [E018](screenshots/backend-ha/E018.jpeg) | backend-ha | Recovery loop transitions from B-only to A/B | WhatsApp Image 2026-11-24 at 15.44.31.jpeg |
| [E019](screenshots/backend-ha/E019.jpeg) | backend-ha | Continuation of restored A/B load balancing | WhatsApp Image 2026-11-24 at 15.44.48.jpeg |
| [E020](screenshots/backup-dns/E020.jpeg) | backup-dns | DNS traffic to backup, primary-edge IP, allowed direct Backend A request | WhatsApp Image 2026-11-24 at 18.19.20.jpeg |
| [E021](screenshots/isolation/E021.jpeg) | isolation | Client direct Backend A request times out | WhatsApp Image 2026-11-24 at 18.27.44.jpeg |
| [E022](screenshots/isolation/E022.jpeg) | isolation | Direct A blocked while HTTPS via primary succeeds | WhatsApp Image 2026-11-24 at 18.28.07.jpeg |
| [E023](screenshots/isolation/E023.jpeg) | isolation | Pi IP/prefix and initial UFW/iptables/nft state | WhatsApp Image 2026-11-24 at 18.32.04.jpeg |
| [E024](screenshots/isolation/E024.jpeg) | isolation | Pi existing nft rules, background Docker/Tailscale state | WhatsApp Image 2026-11-24 at 18.32.36.jpeg |
| [E025](screenshots/isolation/E025.jpeg) | isolation | Continuation of existing Pi firewall state | WhatsApp Image 2026-11-24 at 18.32.37 (1).jpeg |
| [E026](screenshots/isolation/E026.jpeg) | isolation | Continuation of existing Pi NAT/IPv6 state | WhatsApp Image 2026-11-24 at 18.32.37.jpeg |
| [E027](screenshots/isolation/E027.jpeg) | isolation | Primary edge direct Backend B request succeeds | WhatsApp Image 2026-11-24 at 18.37.30.jpeg |
| [E028](screenshots/isolation/E028.jpeg) | isolation | Client direct B times out while HTTPS succeeds | WhatsApp Image 2026-11-24 at 18.39.51.jpeg |
| [E029](screenshots/isolation/E029.jpeg) | isolation | Pi DRACARYS_BACKEND rules and accept/drop counters | WhatsApp Image 2026-11-24 at 18.40.25.jpeg |
| [E030](screenshots/tls/E030.jpeg) | TLS | Certificate directory file listing; no key contents | WhatsApp Image 2026-11-24 at 18.43.49.jpeg |
| [E031](screenshots/tls/E031.jpeg) | TLS | Key permissions tightened; standby CSR signed, chain and SAN verified | WhatsApp Image 2026-11-24 at 18.56.17.jpeg |
| [E032](screenshots/edge-migration/E032.jpeg) | edge-migration | Standby TLS verified with --resolve; preparatory connectivity only | WhatsApp Image 2026-11-24 at 19.05.00.jpeg |
| [E033](screenshots/edge-migration/E033.jpeg) | edge-migration | Standby A/B distribution using --resolve | WhatsApp Image 2026-11-24 at 19.09.11.jpeg |
| [E034](screenshots/edge-migration/E034.jpeg) | edge-migration | Before cutover both DNS answers point to primary; primary request succeeds | WhatsApp Image 2026-11-24 at 19.11.18.jpeg |
| [E035](screenshots/edge-migration/E035.jpeg) | edge-migration | Both DNS answers changed to standby with TTL 30 | WhatsApp Image 2026-11-24 at 19.17.24.jpeg |
| [E036](screenshots/edge-migration/E036.jpeg) | edge-migration | Hostname-based standby TLS and HTTP 200 without --resolve | WhatsApp Image 2026-11-24 at 19.18.40(1).jpeg |
| [E037](screenshots/edge-migration/E037.jpeg) | edge-migration | Duplicate upload of E036, same original bytes | WhatsApp Image 2026-11-24 at 19.18.40.jpeg |
| [E038](screenshots/edge-migration/E038.jpeg) | edge-migration | Primary nginx stopped; hostname requests continue via standby A/B | WhatsApp Image 2026-11-24 at 19.21.27.jpeg |
| [E039](screenshots/edge-migration/E039.jpeg) | edge-migration | Primary nginx restarted; direct --resolve TLS check | WhatsApp Image 2026-11-24 at 19.22.48.jpeg |
| [E040](screenshots/edge-migration/E040.jpeg) | edge-migration | Rollback temporarily has inconsistent DNS answers; not cache proof alone | WhatsApp Image 2026-11-24 at 19.26.12.jpeg |
| [E041](screenshots/edge-migration/E041.jpeg) | edge-migration | Standby requests then both DNS servers converged to primary | WhatsApp Image 2026-11-24 at 19.27.39.jpeg |
| [E042](screenshots/edge-migration/E042.jpeg) | edge-migration | Hostname requests restored to primary, both backends | WhatsApp Image 2026-11-24 at 19.31.01.jpeg |
| [E043](screenshots/backup-dns/E043.jpeg) | backup-dns | Domain-specific resolver has both project DNS servers; host owner not visible | WhatsApp Image 2026-11-24 at 19.32.47.jpeg |
| [E044](screenshots/baseline/E044.jpeg) | baseline | Hostname HTTPS to primary with certificate verification and HTTP 200 | WhatsApp Image 2026-11-24 at 19.33.17.jpeg |
| [E045](screenshots/ttl/E045.jpeg) | TTL | Both resolvers initially return primary with TTL 120 | WhatsApp Image 2026-11-24 at 19.36.29.jpeg |
| [E046](screenshots/ttl/E046.jpeg) | TTL | System cache flushed before timed loop, old IP initially returned | WhatsApp Image 2026-11-24 at 19.38.42.jpeg |
| [E047](screenshots/ttl/E047.jpeg) | TTL | Primary record changed; both DNS servers now give new IP | WhatsApp Image 2026-11-24 at 19.39.51.jpeg |
| [E048](screenshots/ttl/E048.jpeg) | TTL | Client old answer through 19:40:52, new answer at 19:40:57 | WhatsApp Image 2026-11-24 at 19.42.00 (1).jpeg |
| [E049](screenshots/ttl/E049.jpeg) | TTL | Earlier portion of same timed client lookup loop | WhatsApp Image 2026-11-24 at 19.42.00.jpeg |
| [E050](screenshots/ttl/E050.jpeg) | TTL | Manual flush changes stale cached IP immediately to current server answer | WhatsApp Image 2026-11-24 at 19.45.18.jpeg |
| [E051](screenshots/ttl/E051.jpeg) | TTL | TTL record restored; packet capture command and completion | WhatsApp Image 2026-11-24 at 19.48.29.jpeg |
| [E052](screenshots/rollback/E052.jpeg) | rollback | Pi project firewall chain removed, existing ts-input preserved | WhatsApp Image 2026-11-24 at 20.05.52.jpeg |
| [E053](screenshots/troubleshooting/E053.jpeg) | troubleshooting | Post-rollback Backend B connection fails; see E055 and E054 | WhatsApp Image 2026-11-24 at 20.06.10.jpeg |
| [E054](screenshots/rollback/E054.jpeg) | rollback | Backend B direct HTTP 200 after restart | WhatsApp Image 2026-11-24 at 20.07.55 (1).jpeg |
| [E055](screenshots/troubleshooting/E055.jpeg) | troubleshooting | No Backend B listener, then server.py restarted | WhatsApp Image 2026-11-24 at 20.07.55.jpeg |
| [E056](screenshots/rollback/E056.jpeg) | rollback | Backend A direct HTTP 200 after PF rollback | WhatsApp Image 2026-11-24 at 20.09.45.jpeg |
| [E057](screenshots/final-check/E057.jpeg) | final-check | Both DNS servers target primary TTL 30; six primary A/B successes | WhatsApp Image 2026-11-24 at 20.11.29.jpeg |
