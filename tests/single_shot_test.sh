#!/bin/bash

echo "[*] Initializing Single-Shot Ephemeral Attacker..."
echo "[*] Target: 172.17.0.1 (Docker Gateway) | Port: 2222"
echo "[*] Payload: admin_RCE_EXPLOIT_CVE-2026-33827"
echo "-"

# Deploy a temporary Alpine container to send exactly one SSH request.
# The '-q' flag quiets the apk installation output.
# The SSH command will intentionally fail, generating the necessary log.
docker run --rm alpine sh -c "\
  apk add --no-cache openssh-client -q && \
  ssh -o StrictHostKeyChecking=no -p 2222 'admin_RCE_EXPLOIT_CVE-2026-33827'@172.17.0.1"

echo "-"
echo "[*] Payload delivered."
echo "[*] Attacker container destroyed."
echo "[*] Monitor Uvicorn terminal for execution trace."