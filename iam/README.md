# iam/ — Infrastructure-as-code for far-art-assets

Per the contract in the parent [README.md](../README.md) and [AGENTS.md](../AGENTS.md):
- No AKIA secrets in GitHub.
- No `AWS_*` environment variables in Doppler `ci` config.
- OIDC federation only — GHA → STS Role ci/release → S3 assetstore.
- The laptop uses MinIO via Doppler `dev` config, never the assetstore.
- No `aws_s3_object` Terraform per PNG (anti-pattern from far-art-infra).

## Files

### Trust policies (OIDC)

- `trust-far-art-dvc-ci.json` — federated principal for the `ci` GitHub
  Environment. AND on `aud`, `repository`, `environment`, `sub`. Ref is
  not gated (PRs welcome).
- `trust-far-art-dvc-release.json` — federated principal for the
  `release` GitHub Environment on `main`. AND on `aud`, `repository`,
  `environment`, `ref=refs/heads/main`, `sub`.

### Permission policies (IAM)

- `perm-far-art-dvc-ci.json` — read-only: `ListBucket` (prefix
  `far-art`, `far-art/*`), `GetObject{,Version,Tagging}` on
  `arn:aws:s3:::far-art-assets/far-art/*`.
- `perm-far-art-dvc-release.json` — read + write: above plus
  `PutObject`, `PutObjectTagging`, `AbortMultipartUpload`,
  `ListMultipartUploadParts`. **No `DeleteObject`** — lifecycle only.
- `perm-kms-ci.json` — `kms:Decrypt` + `kms:DescribeKey`, gated by
  `kms:ViaService=s3.eu-west-3.amazonaws.com` (no other service can
  use this key).
- `perm-kms-release.json` — adds `kms:GenerateDataKey` to the above.

### Bucket + lifecycle

- `bucket-policy-far-art-assets.json` — denies insecure transport
  (`aws:SecureTransport=false`) and denies public ACLs on put
  (`s3:x-amz-acl ∈ {public-read, public-read-write}`). Combined with
  Block Public Access below — both layers apply, neither substitutes
  for the other.
- `lifecycle-far-art-assets.json` — three rules:
  1. `abort-incomplete-mpu-7d` — abort incomplete MPU after 7 days.
  2. `expire-noncurrent-90d` — non-current versions expire at 90 days.
  3. `expire-draft-30d` — objects tagged `stage=draft` expire at 30 days.
  No rule expires `stage=gate`; gates are kept.
- `public-access-block.json` — the configuration payload (all four
  switches true) used by `put-public-access-block.sh`.
- `put-public-access-block.sh` — applies BPA at bucket + account level.
  Replace `ACCOUNT` and run. Verify with the final `get-public-access-block`
  call — all four switches must be `true`.
- `s3-public-access-block.tf` — Terraform equivalent of the script.
  Bucket + account level + Object Ownership = BucketOwnerEnforced.

## Placeholders to substitute

- `ACCOUNT` — your AWS account ID.
- `KEY-ID` — your KMS key ID (only needed if you enable KMS encryption).

## Interdits

- AKIA in GitHub Secrets.
- `AWS_*` in Doppler `ci`.
- `dvc push laptop → assetstore` (use `minio` remote from the laptop).
- `aws_s3_object` Terraform per asset (anti-pattern from far-art-infra).
- `commit_asset: allow` for asset images of minors.

## Sister

- `.github/workflows/ci.yml` + `.github/workflows/release.yml` — the
  jobs that exercise these trust + permission policies.


## Note on GitHub Actions workflows

The companion `.github/workflows/ci.yml` + `.github/workflows/release.yml`
files exist locally but were NOT pushed in the initial commit because the
PAT used for the push lacked the `workflow` scope (GitHub requires it for
workflow files). To enable CI:

1. Re-run the push with a workflow-scoped token, OR
2. Add the workflows manually via the GitHub web UI (Settings → Actions
   → New workflow → set up workflow yourself → paste from local file).
3. Verify: `gh workflow list` shows `ci` and `release`.

Both files are preserved on disk; only the push was restricted.
