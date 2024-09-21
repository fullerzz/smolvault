resource "aws_s3_bucket" "smolvault" {
  bucket_prefix = "smolvault"

  tags = {
    name        = "smolvault"
    environment = var.env
  }
}

resource "aws_s3_bucket_ownership_controls" "smolvault" {
  bucket = aws_s3_bucket.smolvault.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "smolvault" {
  depends_on = [aws_s3_bucket_ownership_controls.smolvault]

  bucket = aws_s3_bucket.smolvault.id
  acl    = "private"
}

resource "aws_s3_bucket" "smolvault-logs" {
  bucket = "${aws_s3_bucket.smolvault.id}-logs"
}

resource "aws_s3_bucket_ownership_controls" "smolvault-logs" {
  bucket = aws_s3_bucket.smolvault-logs.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "smolvault-logs_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.smolvault-logs]
  bucket     = aws_s3_bucket.smolvault-logs.id
  acl        = "log-delivery-write"
}

resource "aws_s3_bucket_logging" "smolvault-logging" {
  bucket = aws_s3_bucket.smolvault.id

  target_bucket = aws_s3_bucket.smolvault-logs.id
  target_prefix = "log/"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "smolvault" {
  bucket = aws_s3_bucket.smolvault.id
  rule {
    bucket_key_enabled = true
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "smolvault" {
  bucket = aws_s3_bucket.smolvault.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
