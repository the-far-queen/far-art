#!/usr/bin/env bash
# put-public-access-block.sh
# Apply S3 Block Public Access on bucket + account for far-art-assets.
# All four switches must be true after this script runs.

set -euo pipefail

: "${ACCOUNT:?Set ACCOUNT to the AWS account ID (e.g. 123456789012)}"
REGION="${REGION:-eu-west-3}"
BUCKET="${BUCKET:-far-art-assets}"

# Bucket-level
aws s3api put-public-access-block \
  --region "$REGION" \
  --bucket "$BUCKET" \
  --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }'

# Account-level
aws s3control put-public-access-block \
  --region "$REGION" \
  --account-id "$ACCOUNT" \
  --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }'

# Verify
aws s3api get-public-access-block \
  --region "$REGION" \
  --bucket "$BUCKET"
