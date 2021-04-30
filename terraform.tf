
variable "transcribe_namespace" {
  type          = string
  description   = "used to prefix resource names"
}

variable "transcribe_s3_bucket_name" {
  type          = string
  description   = "bucket where audio is uploaded for transcribe"
  default       = ""
}

locals {
  transcribe_s3_bucket_name = var.transcribe_s3_bucket_name != "" ? var.transcribe_s3_bucket_name : "${var.transcribe_namespace}-transcribe-uploads"
  transcribe_policy_name = "${var.transcribe_namespace}-transcribe-policy"
  transcribe_user_name = "${var.transcribe_namespace}-transcribe-user"
}

resource "aws_s3_bucket" "transcribe_upload" {
  bucket          = local.transcribe_s3_bucket_name
  acl             = "private"
  force_destroy   = true
}

resource "aws_s3control_bucket_lifecycle_configuration" "transcribe_upload" {
  bucket = aws_s3control_bucket.transcribe_upload.arn
  rule {
    expiration {
      days = 2
    }
    id = "uploads"
  }
}


data "aws_iam_policy_document" "transcribe_policy" {
  statement {
    sid = "1"
    actions = [
      "s3:*",
    ]
    resources = [
      "arn:aws:s3:::${local.transcribe_s3_bucket_name}/*",
    ]
  }
  statement {
    sid = "2"
    actions = [
      "transcribe:*",
    ]
    resources = [
      "*",
    ]
  }
}

resource "aws_iam_policy" "transcribe_policy" {
  name   = local.transcribe_policy_name
  path   = "/"
  policy = data.aws_iam_policy_document.transcribe_policy.json
}

resource "aws_iam_user" "transcribe_user" {
  name = local.transcribe_user_name
}

resource "aws_iam_user_policy_attachment" "transcribe_policy_attachment" {
  user       = aws_iam_user.transcribe_user.name
  policy_arn = aws_iam_policy.transcribe_policy.arn
}

resource "aws_iam_access_key" "transcribe_policy_access_key" {
  user = aws_iam_user.transcribe_user.name
}

data "aws_region" "current" {}

output "transcribe_env_vars" {
    sensitive   = true
    value       = {
        TRANSCRIBE_AWS_ACCESS_KEY_ID        = aws_iam_access_key.id,
        TRANSCRIBE_AWS_SECRET_ACCESS_KEY    = aws_iam_access_key.secret,
        TRANSCRIBE_AWS_REGION               = data.aws_region.current.name,
        TRANSCRIBE_AWS_S3_BUCKET_SOURCE     = local.transcribe_s3_bucket_name
        TRANSCRIBE_MODULE_PATH              = "transcribe_aws"
    },
    description = "env vars for running transcribe"
}
