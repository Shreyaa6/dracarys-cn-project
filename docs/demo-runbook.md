# Final demonstration - 11-step runbook

Follow assignment Section 8 in order. **Expected** outcomes below are targets for a new live run, not newly recorded results. Historical observations are identified separately by E IDs in the [index](../evidence/phase2/README.md). Faculty challenge and viva are **pending live evaluation**. Keep [setup/rollback](setup-rollback.md) open and save timestamped outputs from the actual run.

## Preparation

Use the Phase 2 IP map; confirm current addresses first. Start both backends, primary/backup DNS and primary nginx. Prepare standby TLS and service before step 9. Verify CA trust on each client without -k. Save DNS, nginx, client settings and full firewall backups outside Git. Keep a local terminal on each firewall host. Agree which teammate operates each device; every member must participate and understand all roles.

Define this convenience function on each test client (bash or zsh):

```bash
probe() {
  date '+%Y-%m-%d %H:%M:%S %Z'
  curl -sS --connect-timeout 5 --max-time 15 -D - -o /dev/null \
    -w 'Connected IP: %{remote_ip}\nHTTP result: %{http_code}\n' \
    https://app.dracarys.test:8443/api/status
}
```

Retain full output and curl exit status. Do not hide errors behind header-only filtering. Set aside a second named client for cached-versus-fresh comparison.

## 1. Show topology and IP/service inventory

Display [architecture](architecture.md) and the [configuration bundle](../configs/phase2/README.md). Name each physical host, owner, IP, interface and port. Explain Meghna's three roles and that DNS is queried separately from HTTPS.

**Expected:** evaluator can trace DNS → primary/standby edge → A/B. **Historical:** E001/E005/E020/E023 establish key roles; refreshed full inventory is still needed.

## 2. Confirm the private LAN

Each Mac runs:

```bash
hostname
date
ipconfig getifaddr en0
ifconfig en0
route -n get default
for ip in 10.7.3.26 10.7.12.197 10.7.30.248 10.7.6.30; do ping -c 3 "$ip"; done
```

Pi runs `hostname; ip -4 addr; ip route; ip link` and the same ping loop. Self-ping is not peer reachability evidence; record each peer pair. **Expected:** correct LAN inventory and peer reachability. **Historical:** E001/E002 show Meghna-to-peers; Phase 1 has earlier connectivity screenshots. Do not reuse old MAC/gateway values as current measurements.

## 3. Resolve the private domain from clients

On two named client Macs:

```bash
hostname
networksetup -getdnsservers "Wi-Fi"
scutil --dns
dig app.dracarys.test A
dig @10.7.3.26 app.dracarys.test A +noall +answer
dig @10.7.30.248 app.dracarys.test A +noall +answer
dscacheutil -q host -a name app.dracarys.test
```

**Expected:** normal app address 10.7.12.197; direct replies TTL 30. Explain direct dig versus scoped system lookup. **Historical:** E012 shows Pranjal's two DNS addresses; E043 is an unlabeled scoped resolver, so capture the missing owner/configuration context now.

## 4. Open HTTPS by hostname

```bash
curl -v --connect-timeout 5 --max-time 15 https://app.dracarys.test:8443/api/status
```

**Expected:** valid certificate chain/SAN, no -k, HTTP/1.1 200 and primary edge. Open the same hostname URL in a trusted browser if requested. **Historical:** E044. Client offering h2 does not establish negotiated h2; read the accepted ALPN protocol.

## 5. Show A/B load balancing

```bash
for i in {1..6}; do echo "Request $i"; probe; sleep 1; done
```

**Expected:** both X-Backend values and X-Edge primary; do not demand a particular first backend. **Historical:** E016 and final E057. Explain round-robin and why clients need only the edge address.

## 6. Show DNS, TCP and TLS packet evidence

Open [client-dns-https.pcap](../evidence/phase2/pcap/client-dns-https.pcap) in Wireshark. Decode TCP 8443 as TLS if necessary. Use [frame analysis](packet-capture-analysis.md) to point to DNS frames 1-2, TCP 3-5, ClientHello 6, ServerHello 8 and close 28/30-32. Identify both socket pairs, relative sequence/ACK numbers and receive windows. Explain retransmission classifications without inventing a cause.

TLS 1.3 encrypts most handshake messages after ServerHello. Use historical [Phase 1 TLS screenshot](../evidence/tls/tls-handshake.jpeg) to discuss a visible TLS 1.2 certificate exchange, clearly naming the different session. Use curl for HTTP headers and trust; the PCAP is not decrypted.

## 7. Show HTTP headers and conditional caching

```bash
curl -I https://app.dracarys.test:8443/api/status
curl -i -H 'If-None-Match: "dracarys-v1"' \
  https://app.dracarys.test:8443/api/status
```

**Expected for unchanged code:** max-age=60, ETag and bodyless 304 for the matching conditional GET. **Historical:** [Phase 1 304 screenshot](../evidence/caching/etag-304-not-modified.jpeg); Phase 2 responses still show the same headers. Explain fresh cache reuse versus conditional revalidation versus full 200. Disclose that the shared fixed ETag across different A/B bodies is simplified and not representation-correct. curl does not automatically cache between commands; DNS TTL is a different cache.

## 8. Stop A and demonstrate service through B

On Meghna, Ctrl+C only the foreground Backend A process. Record `date` and `lsof -nP -iTCP:3001 -sTCP:LISTEN`. On a client run ten probes. **Expected:** HTTP 200 from B only, after passive failure handling. **Historical:** E001/E017.

Recover on Meghna with `python3 backend-a/server.py` from the clone root. Repeat probes after the 10s failure timeout. **Expected:** A/B return. **Historical:** E002/E018/E019. Explain that a failed edge still interrupts service until manual migration.

## 9. Demonstrate Phase 2 DNS and resilience

### 9A. Backup DNS with primary explicitly stopped

On Shreya, record `date`, then stop the actual primary dnsmasq service (Homebrew-managed deployment: `sudo brew services stop dnsmasq`). Record service status and `sudo lsof -nP -iUDP:53 -iTCP:53`. Verify there is no replacement DNS process on the same address.

On a separate named client with both DNS addresses configured, start a filtered capture in another terminal:

```bash
sudo tcpdump -ni en0 -w /path/outside/repo/dns-failover.pcap \
  'port 53 and (host 10.7.3.26 or host 10.7.30.248)'
```

Flush the client's DNS cache, record `hostname`/`date`, run system lookup and hostname curl. Also record `dig @10.7.3.26 +time=2 +tries=1 app.dracarys.test` and `dig @10.7.30.248 app.dracarys.test`. **Expected:** primary query fails, actual fresh client DNS reaches backup and resolution/HTTPS continues. Explicit backup dig alone is insufficient. Stop the capture with Ctrl+C. This exact paired sequence is **not yet evidenced** by the supplied material.

Recover immediately on Shreya with `sudo brew services start dnsmasq`, verify both answers and hostname service. Retain stop-state and client-query timestamps together.

### 9B. TTL and flush

On Pranjal, after initial flush and with both ttl records at the old IP/TTL 120:

```bash
for i in {1..50}; do
  date '+%H:%M:%S'
  dscacheutil -q host -a name ttl.dracarys.test
  sleep 5
 done
```

During the loop, DNS operators change only the ttl record to 10.7.30.248, validate and restart each dnsmasq. Record both direct dig replies before attributing an old client answer to cache. Do not flush during the natural transition. **Historical:** E045-E049; approximately observed transition, not exact expiry timing.

Restore both ttl records to 10.7.12.197, show the client still has the old cached value if present, then flush and query immediately. **Historical:** E050 demonstrates this. If the cache has already changed, state that and repeat the controlled sequence rather than claiming the flush caused it.

### 9C. Isolation and rollback

Use the staged firewall procedures in [setup/rollback](setup-rollback.md). From Pranjal, direct HTTP to A and B should work. From Shreya, direct connections should time out while hostname HTTPS works. Show PF rules and Pi counters. **Historical:** E004/E005/E020-E029. Roll back and confirm direct access before migration. Save a full Pi firewall backup for this live run; that historical backup artifact is missing.

### 9D. Edge migration and simultaneous cache comparison

Verify standby TLS using --resolve only as preparation. Keep primary available. Warm app DNS on one identified client, then edit app to standby on both DNS servers, validate/restart and confirm agreement. Flush only the second identified client. Run normal hostname curl with remote IP and X-Edge on both clients before TTL expiry; record the old-edge/fresh-standby comparison concurrently. Do not use --resolve for this proof. If both clients already refresh, repeat the warm/cache/cutover sequence rather than fabricate a split.

**Historical:** E035-E038 prove hostname cutover and standby service after primary stop, but do not isolate this strict simultaneous comparison. After capturing overlap, stop primary (`nginx -s quit` using its actual instance configuration), verify its listener state and show continued standby A/B responses. Restore primary, test its TLS, restore both app records to primary, verify convergence, and retire standby only after cache overlap. **Historical recovery:** E039-E042/E057.

## 10. Faculty-injected challenge - pending live evaluation

Do not pre-fill this worksheet with the earlier Backend B incident.

| Field | Record during evaluation |
|---|---|
| Time, machine, evaluator's symptom | Pending live evaluation |
| Initial hypothesis and alternatives | Pending live evaluation |
| DNS: both dig replies + system lookup | Pending live evaluation |
| TCP/IP: reachability, port/listener checks | Pending live evaluation |
| TLS: hostname, chain, dates, curl error | Pending live evaluation |
| HTTP/upstream: status, edge/backend headers, logs | Pending live evaluation |
| Isolated layer and supporting evidence | Pending live evaluation |
| Minimal correction and rollback | Pending live evaluation |
| Retest and residual limitations | Pending live evaluation |

Useful probes: `dig @server`, `dscacheutil`, `ping`, `nc -vz host port`, `lsof`/`ss`, `curl -v` and nginx error logs. A timeout can be filtering or reachability; refusal often suggests no listener; 502 points toward upstream handling after edge TLS succeeds. Check evidence before selecting the fix. Explain reasoning aloud. Preserve partial diagnosis honestly if unresolved.

## 11. Individual viva

Each member should answer independently:

- What is the DNS answer versus the TCP socket pair? Why can DNS succeed while HTTPS fails?
- What do SYN/ACK numbers, retransmissions and advertised windows mean? How does flow control differ from congestion control?
- What does TLS authenticate? Why is backend HTTP still plaintext? What is hidden in TLS 1.3 captures?
- What is SNI, SAN, issuer trust and ALPN? Why does api DNS not guarantee valid api HTTPS?
- How do round-robin, passive failure handling and manual edge migration differ?
- How do DNS TTL, HTTP max-age and ETag revalidation differ? What is this demo's ETag limitation?
- Why does a proxy need firewall rules for isolation? Why preserve unrelated chains?
- Which shared hosts and services remain single points of failure?
- What would HTTP/2 multiplexing and HTTP/3 over QUIC change? What roles do SMTP, IMAP and POP3 play (explanation only)?
- How do these local roles compare with managed DNS, cloud load balancers and CDNs, without claiming cloud deployment?

End by restoring the saved baseline and recording final DNS, listeners, firewall and HTTPS checks. Do not mark the challenge/viva passed until actually evaluated.
