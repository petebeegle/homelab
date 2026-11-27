#!/usr/bin/env python3
"""Create the Terraform state bucket on the NAS S3 gateway and turn versioning on.

One-time bootstrap (scripts/SYNOLOGY.md), safe to re-run. The bucket cannot be Terraform-managed:
it holds Terraform's own state. Credentials come from AWS_ACCESS_KEY_ID and
AWS_SECRET_ACCESS_KEY, as for the S3 backend; they are never printed.

    python3 tools/terraform/state_bucket.py [--endpoint https://s3.petebeegle.com] [--bucket terraform-state]
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import hmac
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

REGION = "us-east-1"
VERSIONING_ON = (
    b'<VersioningConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    b"<Status>Enabled</Status></VersioningConfiguration>"
)


class BucketError(RuntimeError):
    pass


def _signed(endpoint: str, method: str, path: str, query: str, body: bytes, access_key: str, secret_key: str) -> urllib.request.Request:
    """An AWS Signature Version 4 request, path-style, as the gateway expects."""
    now = datetime.datetime.now(datetime.timezone.utc)
    amz_date, day = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
    host = urllib.parse.urlsplit(endpoint).netloc
    payload = hashlib.sha256(body).hexdigest()
    headers = f"host:{host}\nx-amz-content-sha256:{payload}\nx-amz-date:{amz_date}\n"
    signed = "host;x-amz-content-sha256;x-amz-date"
    canonical = "\n".join([method, path, query, headers, signed, payload])
    scope = f"{day}/{REGION}/s3/aws4_request"
    to_sign = "\n".join(["AWS4-HMAC-SHA256", amz_date, scope, hashlib.sha256(canonical.encode()).hexdigest()])
    key = ("AWS4" + secret_key).encode()
    for part in (day, REGION, "s3", "aws4_request"):
        key = hmac.new(key, part.encode(), hashlib.sha256).digest()
    signature = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()
    url = endpoint.rstrip("/") + path + ("?" + query if query else "")
    return urllib.request.Request(
        url,
        data=body or None,
        method=method,
        headers={
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload,
            "Authorization": f"AWS4-HMAC-SHA256 Credential={access_key}/{scope}, SignedHeaders={signed}, Signature={signature}",
        },
    )


def _call(endpoint: str, method: str, path: str, query: str, body: bytes, access_key: str, secret_key: str) -> tuple[int, bytes]:
    request = _signed(endpoint, method, path, query, body, access_key, secret_key)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def ensure(endpoint: str, bucket: str, access_key: str, secret_key: str) -> None:
    path = "/" + bucket
    status, body = _call(endpoint, "PUT", path, "", b"", access_key, secret_key)
    if status == 200:
        print(f"created bucket {bucket}")
    elif status == 409 and b"BucketAlreadyOwnedByYou" in body:
        print(f"bucket {bucket} already exists")
    else:
        raise BucketError(f"creating bucket {bucket}: HTTP {status}")

    status, _ = _call(endpoint, "PUT", path, "versioning=", VERSIONING_ON, access_key, secret_key)
    if status != 200:
        raise BucketError(f"turning versioning on for {bucket}: HTTP {status}")
    status, body = _call(endpoint, "GET", path, "versioning=", b"", access_key, secret_key)
    if status != 200 or b"<Status>Enabled</Status>" not in body:
        raise BucketError(f"versioning on {bucket} does not read back Enabled (HTTP {status})")
    print(f"versioning on {bucket}: Enabled")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--endpoint", default="https://s3.petebeegle.com")
    parser.add_argument("--bucket", default="terraform-state")
    args = parser.parse_args(argv)
    access_key, secret_key = os.environ.get("AWS_ACCESS_KEY_ID"), os.environ.get("AWS_SECRET_ACCESS_KEY")
    if not access_key or not secret_key:
        print("set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY (the gateway's keys, from 1Password)", file=sys.stderr)
        return 2
    try:
        ensure(args.endpoint, args.bucket, access_key, secret_key)
    except (BucketError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
