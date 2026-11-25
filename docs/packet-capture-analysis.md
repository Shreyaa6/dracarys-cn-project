# Original packet capture — verified frame notes

File: [original PCAP](../evidence/phase2/pcap/client-dns-https.pcap). Original bytes retained. Classic little-endian PCAP, Ethernet link type 1, 32 frames, 8,226 bytes. Frame numbering below comes from reading the packet bytes; use Wireshark/tshark for richer protocol dissection.

| Frames | Observation |
|---|---|
| 1 | UDP DNS query, client 10.7.3.26:53658 → backup resolver 10.7.30.248:53, transaction 0x9b4f, A question app.dracarys.test |
| 2 | Matching DNS response, A=10.7.12.197, TTL=30 seconds |
| 3 | TCP SYN, 10.7.3.26:63203 → 10.7.12.197:8443 |
| 4 | SYN+ACK from edge :8443 to client :63203 |
| 5 | Client ACK completes the three-way handshake |
| 6 | TLS record with ClientHello handshake message |
| 8 | TLS record with ServerHello; additional records follow in the same TCP payload |
| 10 | ChangeCipherSpec record (compatibility record; by itself does not establish negotiated TLS version) |
| 11–12, 18–19, 25, 27 | TLS outer content type 23 records. In TLS 1.3 these may contain encrypted handshake, application or alert data; do not label all as HTTP payload solely from the outer type. |
| 13, 15 | Same TCP sequence and payload length as frame 8; repeated server data, suitable for discussing possible retransmission/duplicate capture. tshark 4.6.8 classifies both as TCP Spurious Retransmission. This classification does not establish the underlying cause. |
| 28 | Client FIN+ACK |
| 30–32 | Server acknowledgement, server FIN+ACK, final client ACK |

Client SYN sequence is 1664199416. Server SYN sequence is 694731260. Frame 4 acknowledges client sequence +1; frame 5 acknowledges server sequence +1. Wireshark typically displays relative sequence numbers 0 and 1 instead.

This capture establishes an actual cross-host DNS → TCP → TLS flow, unlike the old Phase 1 loopback capture described in the snapshot. It does not by itself establish that the primary DNS was stopped, that the HTTP status was 200, which backend served the response, or that certificate validation succeeded. Use relevant curl screenshots for the latter claims. The DNS client here happens to be the primary-DNS host; that is not proof its DNS daemon was running or stopped.

Useful display filters:

```text
dns.qry.name == "app.dracarys.test"
tcp.port == 8443
tcp.flags.syn == 1
tls.handshake
tcp.analysis.retransmission
tcp.flags.fin == 1
```

If Wireshark does not decode TLS on 8443 automatically, use Decode As → TLS. No TLS keylog was supplied; do not promise decrypted HTTP from this capture.

## Independent dissection during repository finalization

On 25 November 2026 the original bytes were read using tshark 4.6.8:

```bash
tshark -r evidence/phase2/pcap/client-dns-https.pcap -d tcp.port==8443,tls
```

The [complete 32-frame summary](../evidence/phase2/pcap/tshark-summary.txt) is a derived analysis artifact, not a new capture. Frame 8 selects TLS 1.3 via supported_versions (0x0304); legacy version labels in ClientHello/record headers do not override that selection. Frame 8 also includes compatibility ChangeCipherSpec and encrypted outer type-23 records. Frames 20-23 are classified as duplicate ACKs. Relative duration is approximately 1.522542 seconds; this is one captured exchange, not a general service-latency benchmark.

SYNs consume one sequence number. Client initial sequence 1664199416 and server initial sequence 694731260 are acknowledged as +1 in the handshake. Advertised receive windows and window scaling relate to receiver flow control; retransmission/ACK analysis relates to reliable delivery, not proof of a particular congestion mechanism. In the close, frame 29 acknowledges earlier client bytes (Ack=533), frame 30 acknowledges the client FIN (Ack=534), frame 31 sends server FIN, and frame 32 acknowledges it (Ack=2230).

Neither HTTP 200, backend identity, certificate validation nor primary-DNS shutdown can be inferred from this encrypted capture alone. E036/E044 show curl trust and status; E057 shows final DNS and both backends. No decrypted payload or session secret is included. Original byte integrity is covered by the Phase 2 SHA256SUMS file.
