# Phase 2 configuration bundle

These are reconstructed deployment templates based on the repository, E004/E005, E008, E015/E016, E029, E031, E045/E047 and E057. They are not original machine exports and are not automatically installed. Use [setup and rollback](../../docs/setup-rollback.md), [TLS steps](../../docs/tls-phase2.md) and [validation limits](../../docs/validation.md).

| File | Host and purpose |
|---|---|
| [dnsmasq-primary.conf](dnsmasq-primary.conf) | Shreya, 10.7.3.26:53 |
| [dnsmasq-backup.conf](dnsmasq-backup.conf) | Meghna, 10.7.30.248:53 |
| [nginx-primary.conf](nginx-primary.conf) | Pranjal, 10.7.12.197:8080/8443 |
| [nginx-standby.conf](nginx-standby.conf) | Meghna, 10.7.30.248:8080/8443, local A at 127.0.0.1:3001 |
| [backend-a.pf.conf](backend-a.pf.conf) | Meghna, IPv4 PF anchor rules protecting :3001 |
| [backend-b-iptables.rules](backend-b-iptables.rules) | Pi, individual command recipe protecting :3002 |
| [standby-ext.cnf](standby-ext.cnf) | CA holder, leaf certificate signing extensions |

Normal app/api mapping is 10.7.12.197, TTL 30. api is a DNS/HTTP alias, not a demonstrated trusted HTTPS name. The separate ttl name uses 120 seconds. Cutover temporarily changes only app to 10.7.30.248 on BOTH resolvers. No automatic synchronization, health-driven DNS updates or active nginx health checker is implemented.

Firewall templates reproduce the primary-only isolation stage, which was rolled back. Before combining isolation with migration, explicitly authorize standby 10.7.30.248 to Backend B; the original transition is not evidenced. Loopback Backend A on the standby does not cross en0. Do not imply the two stages were tested with unchanged firewall policy.

The root [dnsmasq configuration](../../dns/dnsmasq.conf) and [nginx configuration](../../nginx/nginx.conf) remain historical Phase 1 artifacts, not Phase 2 install targets.
