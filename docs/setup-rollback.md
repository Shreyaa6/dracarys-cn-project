# Phase 2 setup and rollback

These are **reconstructed, operator-run instructions**, not proof of additional tests. Run only on the named project hosts. Repository finalization does not execute privileged networking changes. Keep host backups and private keys outside the clone. Use the [device map](architecture.md) and [bundle](../configs/phase2/README.md). Existing root dns/nginx files are Phase 1 only.

## 1. Inventory and preserve current state

On each Mac, record `hostname`, `date`, `ipconfig getifaddr en0`, `ifconfig en0`, `route -n get default`, `networksetup -getdnsservers "Wi-Fi"` and `scutil --dns`. On the Pi record `hostname`, `ip -4 addr`, `ip route` and `ip link`. Verify current IPs against the table before using any rule. Record service/listener state and certificate paths; do not assume the screenshots represent current running state.

Create a distinct backup directory on each host outside Git, for example:

```bash
umask 077
DRACARYS_BACKUP="$HOME/dracarys-private-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DRACARYS_BACKUP"
printf '%s\n' "$DRACARYS_BACKUP"
```

Keep that path and use the same backup throughout the test. Capture original DNS settings and whether services were running. Never overwrite a prior baseline backup after changing rules.

## 2. Backend services

On Meghna, from the repository root:

```bash
python3 backend-a/server.py
```

On Raspberry Pi, from its repository root:

```bash
python3 backend-b/server.py
```

Leave each foreground process in its own terminal. Stop only that process with Ctrl+C for the planned failure. Inspect with `lsof -nP -iTCP:3001 -sTCP:LISTEN` on Meghna and `ss -ltnp 'sport = :3002'` on Pi. Before isolation, direct HTTP probes from primary should return 200 with the matching X-Backend. Do not send HTTPS to these plain HTTP ports.

## 3. DNS on Shreya and Meghna

Install dnsmasq with Homebrew if absent. Use `brew --prefix` to locate the actual installation; Shreya/Meghna screenshots use `/opt/homebrew`, while Pranjal's nginx uses `/usr/local`. On each DNS host, from the clone root:

```bash
DNS_PREFIX="$(brew --prefix)"
DNS_BIN="$DNS_PREFIX/opt/dnsmasq/sbin/dnsmasq"
DNS_CONF="$DNS_PREFIX/etc/dnsmasq.conf"
sudo cp -p "$DNS_CONF" "$DRACARYS_BACKUP/dnsmasq.conf"
# Shreya: use dnsmasq-primary.conf; Meghna: use dnsmasq-backup.conf.
```

Review both the main file and any service-loaded `dnsmasq.d` files for duplicate project records. Merge unrelated pre-existing settings instead of replacing them blindly. Copy the selected template to a private candidate, merge required unrelated settings, and syntax-check it with the same include arguments used by the service. For a standalone candidate:

```bash
"$DNS_BIN" --test -C /absolute/path/to/candidate-dnsmasq.conf
# After review and successful validation on the intended host:
sudo cp /absolute/path/to/candidate-dnsmasq.conf "$DNS_CONF"
sudo brew services restart dnsmasq
```

A dnsmasq SIGHUP is not sufficient for rereading arbitrary main-configuration edits; restart after record changes. Validate both servers:

```bash
dig @10.7.3.26 app.dracarys.test A +noall +answer
dig @10.7.30.248 app.dracarys.test A +noall +answer
dig @10.7.3.26 api.dracarys.test A +noall +answer
dig @10.7.30.248 ttl.dracarys.test A +noall +answer
```

Expected: app/api → 10.7.12.197 TTL 30; ttl → 10.7.12.197 TTL 120. These templates provide local project answers; preserve the host's existing upstream resolver policy for unrelated names and avoid configuring a self-forwarding loop.

On **two identifiable client Macs**, save existing Wi-Fi DNS settings, then:

```bash
networksetup -getdnsservers "Wi-Fi" > "$DRACARYS_BACKUP/wifi-dns.txt"
sudo networksetup -setdnsservers "Wi-Fi" 10.7.3.26 10.7.30.248
hostname
networksetup -getdnsservers "Wi-Fi"
scutil --dns
dscacheutil -q host -a name app.dracarys.test
```

If preserving unrelated Wi-Fi DNS is necessary, a scoped `/etc/resolver/dracarys.test` file may contain `nameserver 10.7.3.26` and `nameserver 10.7.30.248` on separate lines. Back up any existing file first. This is an alternative mechanism, not evidence of global Wi-Fi settings; the assignment explicitly asks for client DNS configuration, so show the actual method and confirm acceptance. `dig @server` tests that server directly; on macOS it does not test scoped system-resolver cache behavior. Use dscacheutil and hostname curl for that.

Rollback: restore the saved dnsmasq file and prior include files, test, then restart or stop the service according to its original state. Restore original client DNS addresses. Use `networksetup -setdnsservers "Wi-Fi" Empty` only if the baseline used automatic/DHCP DNS. Restore or remove only the scoped resolver file created for this project. Flush only when the test or restoration calls for it:

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

## 4. Primary and standby nginx

Obtain the existing private deployment certificates using [TLS instructions](tls-phase2.md). On Pranjal use nginx-primary.conf; on Meghna use nginx-standby.conf. Check the absolute certificate paths, existing nginx ownership and invocation before deploying. The standby uses local A at 127.0.0.1; the primary uses A's LAN IP. Both require B listening on 10.7.6.30:3002.

```bash
NGINX_CONF="$(brew --prefix)/etc/nginx/nginx.conf"
cp -p "$NGINX_CONF" "$DRACARYS_BACKUP/nginx.conf"
# Review/merge selected template into a private candidate first.
nginx -t -c /absolute/path/to/candidate-nginx.conf
# Install only after successful test, preserving unrelated server blocks.
cp /absolute/path/to/candidate-nginx.conf "$NGINX_CONF"
nginx -t
# If nginx was running:
nginx -s reload
# If it was stopped, use nginx (do not start a duplicate master).
```

Use the same binary, config path, prefix and service manager for start/stop/reload; if using a custom `-c` or `-p`, repeat those options. The default commands above assume the Homebrew default configuration. Verify `curl -v https://app.dracarys.test:8443/api/status` from a trusted client. For standby preparation only:

```bash
curl -v --resolve app.dracarys.test:8443:10.7.30.248 \
  https://app.dracarys.test:8443/api/status
```

Rollback: restore the saved nginx configuration, run `nginx -t`, then reload an existing instance. If standby was newly started for the test, stop that instance with its matching `nginx -s quit`; do not stop an unrelated nginx. Restore normal DNS before retiring the standby, and allow cached clients an overlap interval.

## 5. Isolation stage: Backend A PF

Use local access to Meghna. Save the current configuration, anchor file if present, rule listing and enable status:

```bash
sudo cp -p /etc/pf.conf "$DRACARYS_BACKUP/pf.conf"
sudo pfctl -s info > "$DRACARYS_BACKUP/pf-info.txt"
sudo pfctl -sr > "$DRACARYS_BACKUP/pf-rules.txt"
# If /etc/pf.anchors/dracarys already exists, preserve it and inspect ownership first.
```

Install the [anchor contents](../configs/phase2/backend-a.pf.conf) at `/etc/pf.anchors/dracarys`. Review `/etc/pf.conf` with all Apple/system anchors preserved. Add the following only once, at a filter-rule position where earlier quick accepts cannot bypass the project policy:

```text
anchor "dracarys"
load anchor "dracarys" from "/etc/pf.anchors/dracarys"
```

Validate the entire candidate with `sudo pfctl -vnf /etc/pf.conf`. Loading the main file can affect dynamically inserted rules: compare the baseline, use the host's existing anchor arrangement where possible, and do not use a blanket flush. On the dedicated demo host, after review:

```bash
sudo pfctl -f /etc/pf.conf
sudo pfctl -E
# Record the returned enable token; it belongs to this invocation.
sudo pfctl -a dracarys -sr
```

Open fresh curl connections for allowed and blocked tests; pre-existing PF states can survive rule changes. Do not flush unrelated connection states. Test primary-to-A direct HTTP, separate-client-to-A timeout, and client HTTPS success. This policy concerns IPv4 en0 traffic to A; standby's loopback A path is separate.

Rollback removes only this test's rules and restores its saved configuration. If no unrelated changes occurred since backup:

```bash
sudo pfctl -a dracarys -F rules
sudo cp -p "$DRACARYS_BACKUP/pf.conf" /etc/pf.conf
sudo pfctl -nf /etc/pf.conf
sudo pfctl -f /etc/pf.conf
sudo pfctl -X YOUR_RECORDED_ENABLE_TOKEN
sudo pfctl -s info
```

Replace the token with this run's actual value. Restore any pre-existing dracarys anchor, or remove the newly created file after unlinking it. Do not blindly use `pfctl -d`: other services may now depend on PF. E010's historical global disable is appropriate only in its recorded initial-disabled context; the safer reconstruction releases this run's own reference.

## 6. Isolation stage: Backend B iptables

On Pi, save pre-change rules outside the clone:

```bash
sudo iptables-save > "$DRACARYS_BACKUP/iptables-before.rules"
sudo ip6tables-save > "$DRACARYS_BACKUP/ip6tables-before.rules"
sudo iptables -S
sudo iptables -S DRACARYS_BACKEND
```

If the project chain already exists, inspect it rather than duplicating a jump or overwriting someone else's rules. Otherwise execute the [individual commands](../configs/phase2/backend-b-iptables.rules), filling the chain before inserting its INPUT jump. They touch only TCP 3002 and preserve Docker/Tailscale chains. Check `sudo iptables -L DRACARYS_BACKEND -n -v --line-numbers` alongside allowed/blocked curl results.

Rollback in order:

```bash
sudo iptables -D INPUT -p tcp --dport 3002 -j DRACARYS_BACKEND
sudo iptables -F DRACARYS_BACKEND
sudo iptables -X DRACARYS_BACKEND
sudo iptables -S INPUT
```

Do not run `iptables -F` without a chain or replace the whole ruleset casually. The complete backup is emergency recovery after comparing intervening changes; a blanket restore can overwrite unrelated current work. No persistence service is added by this recipe. Verify B's listener and direct HTTP after rollback, as E053/E055 show why firewall removal alone may not restore a stopped backend.

## 7. TTL and migration changes

For TTL testing, edit only `host-record=ttl.dracarys.test,10.7.12.197,120` to use 10.7.30.248 on **both** resolvers. Validate and restart each DNS service; direct dig must agree before interpreting client cache behavior. Start the client lookup loop before editing. Do not flush during the natural-expiry part. Restore both records to the original value, demonstrate a stale client answer followed by manual flush, then verify agreement again.

For edge migration, first restore isolation-stage firewall changes, matching the separate-stage evidence. If choosing a combined isolation/migration demonstration instead, explicitly add a Pi allow rule for standby 10.7.30.248 before DROP, document that new policy, and collect new evidence; do not describe it as observed in the original screenshots.

Start/verify standby and its certificate, keep primary running, then change only `address=/app.dracarys.test/10.7.12.197` to 10.7.30.248 on both DNS hosts. Test normal hostname curl with `-w 'Connected IP: %{remote_ip}\n'`, without --resolve. Preserve one warmed client cache and flush a second client to capture the assignment's simultaneous comparison. Stop primary only after recording overlap and standby health. Roll back by starting/validating primary, restoring both app answers to 10.7.12.197, checking direct DNS agreement and hostname HTTPS, then retiring standby when safe. E040 resolver disagreement is a condition to correct, not a TTL result.

## 8. End-of-demo restoration checklist

Restore primary DNS service, both app records at TTL 30, ttl record baseline, Backend A/B listeners, primary nginx and trusted hostname HTTPS. Remove only project firewall changes; check direct backend access. Restore prior client resolver/trust settings if the lab session is ending. Restore temporary nginx configuration/service state. Preserve real screenshots and logs with timestamps outside private-key directories; do not replace old evidence. Compare the final state with the saved baseline, including unrelated firewall/services.
