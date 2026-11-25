# Repository validation - 25 November 2026

These are local repository checks, separate from the 24 November lab observations. No private LAN hosts were probed, no service was started for this task, and no firewall/DNS/trust configuration was installed on the user's machine.

## Evidence and preservation

- Verified all 158 SHA-256 entries in the supplied handoff before copying; the separately attached assignment PDF matches its handoff copy.
- Retained all 57 original screenshot uploads, 57 OCR companions, original filenames and SHA-256 in JSON/CSV manifests. E036/E037 are byte-identical and retained under both IDs.
- Retained the original 8,226-byte PCAP. tshark 4.6.8 dissection confirms 32 frames, DNS transaction, TCP handshake/close and TLS 1.3 ServerHello. Derived frame summary is committed separately.
- Reviewed original screenshot contact sheets and relevant configuration/result pixels against the handoff audit. Rendered assignment pages 9-10 to verify mandatory extensions and the exact 11-step sequence.
- Phase 1 images, topology, backend sources, public CA and root DNS/nginx configurations remain byte-identical to baseline a933e2c. Historical README/architecture are retained as separate files; historical pages receive explicit phase banners. Git history is not rewritten.

## File and configuration checks

Run the repeatable offline check from the repository root:

```bash
python3 scripts/validate_repository.py
```

It checks complete evidence IDs, original names, screenshot hashes/sizes, duplicate mapping, curated SHA256SUMS, relative Markdown image/file links, HTML gallery references, Python AST syntax and private-key file/content boundaries. It does not validate remote links, every Markdown anchor or live service behavior.

| Check | Actual result | Limit |
|---|---|---|
| dnsmasq 2.93 `--test -C` on both Phase 2 templates | Passed | Syntax only; no binding, upstream resolution or host include-directory test |
| nginx 1.31.10 `-t` on both template-derived candidates | Passed | Isolated scratch prefix/logs and disposable validation.invalid certificate/key substituted; no actual deployed leaf/key validation and no listener started |
| macOS `/sbin/pfctl -nf` on Backend A anchor | Passed | Parse-only; no loading, root access or firewall enforcement test |
| `bash -n` on Pi iptables command recipe | Passed | Shell syntax + static rule-order review only; Linux iptables/kernel execution unavailable here |
| Both backend Python files and helper scripts | AST syntax passed | Backend code unchanged, no new runtime/LAN result claimed |
| Public CA inspection with OpenSSL | Parsed CN/issuer Dracarys Local CA and validity | Does not validate unavailable leaf certificates or every client trust store |
| Canonical report export | ReportLab export, rendered and visually reviewed | PDF is a reading export; Markdown remains canonical |
| Relative links and evidence integrity | Passed after completion of referenced files | Local file references only |
| Git diff / intended file review | Whitespace and private-artifact checks passed before commit | No guarantee from ignore rules alone; staged content also inspected |

The disposable nginx validation key/certificate were created only in scratch outside Git and removed after syntax checks. This was not regeneration of the real CA. Host-specific templates must still be reviewed on their intended machines with real private paths before installation.

Public CA fingerprint (SHA-256):

```text
8B:4E:6B:D1:E8:C5:1D:64:F4:5A:91:2D:A3:4D:BE:20:48:44:53:09:59:4E:89:76:12:8D:B3:10:4C:33:7C:B0
```

## Final completeness audit

The report covers changes from Phase 1, methods, results, evidence, recovery, limitations and a learning paragraph for each A-F extension. The bundle includes both DNS/edge roles, both host firewall mechanisms and standby certificate extensions. The demonstration runbook follows all 11 assignment steps and includes reversible faults, layer-by-layer diagnosis and viva prompts. The [submission checklist](submission-checklist.md) maps the entire assignment, with live gaps separated from prepared files.

The final audit found no basis to claim primary-down DNS failover, ownership of E043, the strict simultaneous migration cache comparison, or the faculty challenge/viva already complete. These remain explicit. Full current host inventory, client trust and Pi backup are rehearsal checks. No unsupported pass claims, new application features, private keys, session keylogs, duplicate reference repository, installation logs or handoff ZIP are included.

## Rebuild the PDF

With ReportLab installed in the selected Python environment:

```bash
python3 scripts/export_report.py
python3 scripts/validate_repository.py
```

Render the resulting PDF with a PDF renderer and inspect all pages after content changes. The export links back to the corresponding GitHub Markdown/evidence locations. Repository publication details are reported with the final commit rather than embedding a self-referential commit hash in this file.
