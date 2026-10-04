# TLS & Certificate Architecture

This directory documents the Transport Layer Security (TLS) configuration and Public Key Infrastructure (PKI) established for Team Dracarys's **Private Network Service Platform**.

---

## 1. Overview & Local CA Architecture

For our private domain `app.dracarys.test`, public Certificate Authorities (such as Let's Encrypt or DigiCert) cannot issue certificates because `.test` is a reserved private top-level domain (RFC 2606) not routable on the public Internet.

To provide genuine, cryptographically secure TLS termination without insecure browser or client flags:
- We created a dedicated internal Certificate Authority: **Dracarys Local CA**.
- The public root CA certificate is available in this repository at [`tls/dracarys-ca.crt`](dracarys-ca.crt). Client machines import and trust this public certificate in their trusted system certificate stores (macOS Keychain).
- Using this Local CA, we signed a server leaf certificate covering only `app.dracarys.test`.

---

## 2. Server Certificate Details

- **Common Name (CN)**: `app.dracarys.test`
- **Subject Alternative Name (SAN)**: `DNS:app.dracarys.test` (covers only `app.dracarys.test`)
- **Issuer**: `Dracarys Local CA`
- **Signature Algorithm**: SHA-256 with RSA encryption
- **Protocols Supported**: TLSv1.2, TLSv1.3

---

## 3. Host and Deployment Paths (Pranjal Mac)

The reverse proxy host (`10.7.26.65`) runs nginx 1.31.6. The certificate and private key are stored locally on that host at standard configuration paths:

| File Role | Path on Edge Host (`10.7.26.65`) |
| :--- | :--- |
| **Server Certificate** | `/usr/local/etc/nginx/certs/app.dracarys.test.crt` |
| **Server Private Key** | `/usr/local/etc/nginx/certs/app.dracarys.test.key` |

---

## 4. Client Trust Verification (No `-k` Flag)

Because the root certificate of **Dracarys Local CA** is imported and marked as trusted in the client's Keychain / system trust store:
- Standard clients (`curl`, browsers, OpenSSL s_client) establish the cryptographic chain of trust to the local root CA.
- Verification succeeds without passing the `-k` (`--insecure`) flag.
- Validated command:
  ```bash
  curl -v https://app.dracarys.test:8443
  ```
  The verbose output explicitly confirms:
  - Subject Name match: `CN=app.dracarys.test`
  - Server certificate verification: `SSL certificate verify ok`
  - Negotiation of TLSv1.2 or TLSv1.3 session

---

## 5. Security & Repository Policy

> [!CAUTION]
> **Zero Private Key Policy**:
> Private keys (`*.key`, `*.pem`, `*.p12`, etc.) contain secret cryptographic material that must never leave the host machine.
> - Under **NO** circumstances should `app.dracarys.test.key` or CA private keys be committed to this repository. CA and server private keys are deliberately NOT stored in Git.
> - Only the public CA root certificate ([`tls/dracarys-ca.crt`](dracarys-ca.crt)) is tracked in the repository for client trust store installation.
> - The repository's `.gitignore` explicitly blocks all key extensions.
> - The actual server certificate and key files remain exclusively on `/usr/local/etc/nginx/certs/` on Pranjal's Mac.
