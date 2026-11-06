#!/usr/bin/env bash
# Generate 1 MiB of random data from Linux /dev/urandom and from OpenSSL.
# Run from the repo root:  bash utils/generate_random_linux.sh
set -e

OUT="${1:-datasets}"
mkdir -p "$OUT"

# 1) Linux kernel generator (1 MiB = 1048576 bytes)
head -c 1048576 /dev/urandom > "$OUT/urandom.bin"

# 2) OpenSSL's rand utility
openssl rand -out "$OUT/openssl.bin" 1048576

echo "OpenSSL version: $(openssl version)"
echo "Kernel:          $(uname -r)"
echo
ls -l "$OUT/urandom.bin" "$OUT/openssl.bin"
echo
sha256sum "$OUT/urandom.bin" "$OUT/openssl.bin"
