# Standby TLS and client trust

Reconstructed procedure from E007/E008 and E030-E032. The existing public [Dracarys CA certificate](../tls/dracarys-ca.crt) is supplied. Neither leaf certificate nor any private key is supplied as a file. Do not manufacture missing historical certificates or regenerate the real CA. E031 shows a standby certificate valid 24 November 2026 to 22 February 2027, SAN app.dracarys.test; check actual files before reuse.

## Standby host: key and CSR

Only if provisioning a new standby certificate, create a **new private directory outside the repository**, or use an existing key/CSR after verifying provenance. Never overwrite a deployed key:

```bash
umask 077
mkdir -p "$HOME/dracarys-private"
cd "$HOME/dracarys-private"
test ! -e standby.key && test ! -e standby.csr || exit 1
openssl genrsa -out standby.key 2048
openssl req -new -key standby.key -subj '/CN=app.dracarys.test' -out standby.csr
openssl req -in standby.csr -noout -verify -subject
chmod 600 standby.key
```

Transfer only the CSR to the existing CA holder using an approved private channel. The key remains on standby. The subject alone is insufficient; signing must include a DNS SAN.

## CA holder: sign with existing CA

Use the existing CA key and serial file on its authorized host. Verify the request and intended hostname. Copy [standby-ext.cnf](../configs/phase2/standby-ext.cnf) to the working directory, then use the existing paths (adapt only after checking actual deployment):

```bash
openssl req -in standby.csr -noout -verify -subject
sudo openssl x509 -req -in standby.csr \
  -CA /usr/local/etc/nginx/certs/dracarys-ca.crt \
  -CAkey /usr/local/etc/nginx/certs/dracarys-ca.key \
  -CAserial /usr/local/etc/nginx/certs/dracarys-ca.srl \
  -out standby.crt -days 90 -sha256 -extfile standby-ext.cnf
openssl verify -CAfile /usr/local/etc/nginx/certs/dracarys-ca.crt standby.crt
openssl x509 -in standby.crt -noout -subject -issuer -dates -ext subjectAltName
```

The existing CA custodian must manage serial uniqueness. Do not recreate/reset a missing serial file ad hoc. Return only the signed public certificate and public CA certificate to standby. Do not copy the CA key to standby. Restrict CA/leaf key permissions to their required owner; nginx's master must still be able to read its leaf key.

## Match key, configure and verify

On standby, compare these public modulus digests; matching values support that the certificate corresponds to the RSA key without displaying key contents:

```bash
openssl x509 -in standby.crt -noout -modulus | openssl dgst -sha256
openssl rsa -in standby.key -noout -modulus | openssl dgst -sha256
openssl verify -CAfile /path/to/dracarys-ca.crt standby.crt
```

Place files at the paths referenced by the reviewed standby nginx template; test `nginx -t` before starting/reloading. The CA identity should be verified with the team by fingerprint before adding trust:

```bash
openssl x509 -in tls/dracarys-ca.crt -noout -fingerprint -sha256
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain tls/dracarys-ca.crt
curl -v --resolve app.dracarys.test:8443:10.7.30.248 \
  https://app.dracarys.test:8443/api/status
```

Run the trust commands from the clone root on each participating Mac. Some curl/OpenSSL builds use their own CA bundle instead of the macOS trust store; `curl --cacert tls/dracarys-ca.crt ...` validates explicitly without bypassing trust, but verify browser/system trust separately for the final demo. After cutover, repeat hostname curl **without --resolve**, checking certificate verification, X-Edge and remote IP. Never use `-k` for the demonstration.

api.dracarys.test is not a demonstrated certificate SAN. Its DNS record does not make its HTTPS certificate valid. In TLS 1.3 the PCAP cannot display the encrypted Certificate message without session secrets; use curl or local certificate inspection for validation evidence.

## Rollback

Record prior trust state before import. If the CA was newly added solely for the lab, remove only that exact certificate/trust entry from the selected keychain using Keychain Access and its verified fingerprint; do not remove a pre-existing shared trust entry. Restore previous nginx configuration and service state as described in [setup/rollback](setup-rollback.md). Retain private keys in their protected host directory, never Git. A replaced CA would require deliberate reissuance and trust redistribution; that is not part of this repository finalization.
