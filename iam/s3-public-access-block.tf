# s3-public-access-block.tf
# Block Public Access at both bucket and account level.
# Per AGENTS.md + far-art-infra doc: never aws_s3_object per asset.

resource "aws_s3_bucket_public_access_block" "far_art_assets" {
  bucket = "far-art-assets"

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_account_public_access_block" "org" {
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

# Object Ownership: BucketOwnerEnforced (ACLs disabled).
resource "aws_s3_bucket_ownership_controls" "far_art_assets" {
  bucket = "far-art-assets"
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}
