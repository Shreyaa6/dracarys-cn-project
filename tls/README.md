# TLS & Certificate Architecture

This directory documents the Transport Layer Security (TLS) configuration and Public Key Infrastructure (PKI) established for Team Dracarys's **Private Network Service Platform**.

---

## 1. Overview & Local CA Architecture

For our private domain `app.dracarys.test`, public Certificate Authorities (such as Let's Encrypt, DigiCert, or Sectigo) cannot issue valid certificates because `.test` is a reserved private top-level domain ([RFC 2606](https://datatracker.ietf.org/doc/html/rfc2606)) that is not routable or registrable on the public Internet.

To provide genuine, cryptographically secure TLS termination at the edge proxy without relying on insecure client flags (such as `curl -k` or `--insecure`):
- We established a dedicated internal Certificate Authority: **Dracarys Local CA**.
- The public root CA certificate is tracked in this repository at [`tls/dracarys-ca.crt`](dracarys-ca.crt). Client machines import and trust this public root certificate into their local system trust stores.
- Using this Local CA, we signed a leaf server certificate issued specifically for `app.dracarys.test`.

### Verified Local CA Properties
- **Public Certificate File**: [`tls/dracarys-ca.crt`](dracarys-ca.crt)
- **Subject**: `CN=Dracarys Local CA`
- **Issuer**: `CN=Dracarys Local CA` (Self-signed Root CA)
- **Public Key**: RSA 2048-bit (`Exponent: 65537 (0x10001)`)
- **Signature Algorithm**: `sha256WithRSAEncryption`
- **Validity Window**: `Oct 4 13:17:37 2026 GMT` to `Oct 4 13:17:37 2027 GMT`
- **Basic Constraints**: `critical, CA:TRUE`
- **Private Key**: The CA private key is **NOT** committed to Git and must remain strictly private to the issuing host.

---

## 2. Server Certificate Details

The reverse proxy presents a leaf certificate signed directly by **Dracarys Local CA**:

- **Hostname / Common Name (CN)**: `app.dracarys.test`
- **Subject**: `CN=app.dracarys.test`
- **Issuer**: `CN=Dracarys Local CA`
- **Subject Alternative Name (SAN)**: `DNS:app.dracarys.test`
- **Extended Key Usage (EKU)**: `TLS Web Server Authentication` (`extendedKeyUsage = serverAuth`)
- **Public Key**: RSA 2048-bit
- **Signature Algorithm**: `sha256WithRSAEncryption`
- **Validity Window**: `Oct 4 13:20:26 2026 GMT` to `Oct 4 13:20:26 2027 GMT`
- **Certificate Scope**: The server certificate intentionally covers **only** `app.dracarys.test`. It does not cover `api.dracarys.test` or wildcard subdomains.
- **Private Key**: The server private key (`app.dracarys.test.key`) is **NOT** committed to Git.

---

## 3. Deployed Paths on the Nginx Edge Host (`10.7.26.65`)

The reverse proxy host (`10.7.26.65`) runs nginx 1.31.6 on macOS. The certificates and private key are stored locally on that host at standard nginx PKI paths:

| File Role | Absolute Path on Edge Host (`10.7.26.65`) | In Repository? |
| :--- | :--- | :--- |
| **Local CA Certificate** | `/usr/local/etc/nginx/certs/dracarys-ca.crt` | Yes ([`tls/dracarys-ca.crt`](dracarys-ca.crt)) |
| **Server Leaf Certificate** | `/usr/local/etc/nginx/certs/app.dracarys.test.crt` | No (Host deployment only) |
| **Server Private Key** | `/usr/local/etc/nginx/certs/app.dracarys.test.key` | **Never** (Secret host key) |

---

## 4. Nginx TLS Configuration

Nginx terminates TLS on port 8443 and proxies validated HTTP requests to the upstream Python backends. The TLS parameters in `nginx/nginx.conf` specify:

```nginx
server {
    listen 8443 ssl;
    server_name app.dracarys.test;

    ssl_certificate     /usr/local/etc/nginx/certs/app.dracarys.test.crt;
    ssl_certificate_key /usr/local/etc/nginx/certs/app.dracarys.test.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ...
}
```

- **Port**: Listens for HTTPS on port `8443`.
- **Certificates**: `ssl_certificate` references `app.dracarys.test.crt` and `ssl_certificate_key` references `app.dracarys.test.key`.
- **Protocols**: Supports modern secure transport protocols `TLSv1.2` and `TLSv1.3`.

---

## 5. Client Trust Architecture & Verification

### Private Trust Model
Because `.test` is a private TLD and `Dracarys Local CA` is a private internal Certificate Authority, this setup does **not** rely on public commercial root programs (such as Apple Root Store or Mozilla NSS).

Instead, the public root CA certificate ([`tls/dracarys-ca.crt`](dracarys-ca.crt)) was imported into and trusted within the local system trust store (macOS Keychain) on participating client machines. As a result:
- Standard command-line clients (`curl`, OpenSSL) and web browsers build a complete, verified chain of trust up to `Dracarys Local CA`.
- Client verification succeeds cleanly **without** the `-k` (`--insecure`) flag.

### Verified Client Test Command

A participating client verified the deployment using the following command:

```bash
curl -v https://app.dracarys.test:8443/api/status
```

The verbose output confirmed the following verified milestones:
1. **DNS Resolution**: `app.dracarys.test` resolved to edge IP `10.7.26.65`.
2. **TCP Handshake**: Connection to `10.7.26.65` on port `8443` succeeded.
3. **SAN Matching**: Subject Alternative Name (`SAN`) matched `app.dracarys.test`.
4. **Issuer Validation**: Issuer confirmed as `CN=Dracarys Local CA`.
5. **Certificate Trust**: Verified cleanly with `SSL certificate verify ok` (no trust warnings or insecure flags).
6. **Application Response**: Negotiated cipher suite and returned an authenticated `HTTP/1.1 200 OK` response with application payload.

---

## 6. Reproducing the TLS Setup

> [!NOTE]
> The commands below represent a **technically correct, reproducible OpenSSL procedure consistent with the deployed certificate properties**, rather than an exact historical command transcript.

### Step 1: Create the Local Root CA (RSA 2048)

Generate the private key and self-signed certificate for the local CA:

```bash
# 1. Generate CA private key (RSA 2048) - KEEP PRIVATE
openssl genrsa -out dracarys-ca.key 2048

# 2. Generate self-signed CA root certificate (valid 365 days)
openssl req -x509 -new -nodes \
    -key dracarys-ca.key \
    -sha256 \
    -days 365 \
    -subj "/CN=Dracarys Local CA" \
    -out dracarys-ca.crt
```

### Step 2: Create Server Private Key and CSR

Generate the server private key and Certificate Signing Request (CSR) for `app.dracarys.test`:

```bash
# 1. Generate server private key (RSA 2048) - KEEP PRIVATE
openssl genrsa -out app.dracarys.test.key 2048

# 2. Generate Certificate Signing Request (CSR)
openssl req -new \
    -key app.dracarys.test.key \
    -subj "/CN=app.dracarys.test" \
    -out app.dracarys.test.csr
```

### Step 3: Sign the Server Certificate with SAN and Extended Key Usage

Create an OpenSSL extension config file to attach the Subject Alternative Name and Server Authentication usage:

```bash
cat << 'EOF' > server-ext.cnf
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = app.dracarys.test
EOF
```

Sign the CSR using the local CA:

```bash
openssl x509 -req \
    -in app.dracarys.test.csr \
    -CA dracarys-ca.crt \
    -CAkey dracarys-ca.key \
    -CAcreateserial \
    -out app.dracarys.test.crt \
    -days 365 \
    -sha256 \
    -extfile server-ext.cnf
```

### Step 4: Configure Nginx on the Edge Host

Copy the generated certificate and private key to the nginx certificate directory:

```bash
sudo mkdir -p /usr/local/etc/nginx/certs
sudo cp dracarys-ca.crt /usr/local/etc/nginx/certs/dracarys-ca.crt
sudo cp app.dracarys.test.crt /usr/local/etc/nginx/certs/app.dracarys.test.crt
sudo cp app.dracarys.test.key /usr/local/etc/nginx/certs/app.dracarys.test.key
sudo chmod 600 /usr/local/etc/nginx/certs/app.dracarys.test.key
```

Verify nginx configuration and reload:

```bash
sudo nginx -t
sudo nginx -s reload
```

### Step 5: Trust the Local CA on Participating macOS Clients

To enable client trust without `-k`:

- **GUI Method (Keychain Access)**:
  1. Transfer the public certificate `dracarys-ca.crt` to the client Mac.
  2. Double-click `dracarys-ca.crt` or open **Keychain Access.app** and drag it into the **System** or **login** keychain.
  3. Double-click **Dracarys Local CA** in Keychain Access.
  4. Expand the **Trust** section and set **When using this certificate** to **Always Trust**.
  5. Close the window and authenticate with macOS administrator credentials.

- **Command-Line Method (Terminal)**:
  ```bash
  # Adds the certificate as a trusted root in the macOS System keychain (requires administrator privileges)
  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain dracarys-ca.crt
  ```

---

## 7. Verification & Inspection Commands

Run these inspection commands to verify certificates and active TLS connections:

```bash
# Verify the Local CA certificate subject, issuer, and validity dates
openssl x509 -in tls/dracarys-ca.crt -noout -subject -issuer -dates

# Inspect full certificate details, extensions, and public key properties
openssl x509 -in tls/dracarys-ca.crt -noout -text

# Inspect deployed server certificate details on the nginx edge host
openssl x509 -in /usr/local/etc/nginx/certs/app.dracarys.test.crt -noout -subject -issuer -dates -ext subjectAltName

# Test end-to-end verified HTTPS connection from client (must return HTTP 200 without -k)
curl -v https://app.dracarys.test:8443/api/status
```

---

## 8. Security Policy & Best Practices

> [!CAUTION]
> **Strict Private Key Policy**:
> - **Never commit `*.key` files**: Private keys (`dracarys-ca.key`, `app.dracarys.test.key`) contain secret cryptographic material that allows impersonation or decryption. They must remain exclusively on the host where they were generated.
> - **Never commit the CA private key**: Compromise of the CA private key invalidates the entire trust domain.
> - **Public CA Distribution**: The root certificate [`tls/dracarys-ca.crt`](dracarys-ca.crt) is a **public certificate** and is safe to distribute publicly to clients for trust store installation.
> - **Repository Protection**: The repository `.gitignore` explicitly excludes `*.key`, `*.pem`, `*.p12`, and `*.pfx` files to prevent accidental leakage.
