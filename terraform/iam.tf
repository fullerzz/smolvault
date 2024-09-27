resource "aws_iam_user" "smolvault-user" {
  name = "smolvault-user-${var.env}"
}

resource "aws_iam_access_key" "smolvault-user" {
  user = aws_iam_user.smolvault-user.name
}

data "aws_iam_policy_document" "smolvault-policy" {
  statement {
    effect    = "Allow"
    actions   = ["s3:*"]
    resources = [aws_s3_bucket.smolvault.arn, "${aws_s3_bucket.smolvault.arn}/*"]
  }
  statement {
    effect    = "Allow"
    actions   = ["kms:*"]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "smolvault-user-policy" {
  name   = "smolvault-user-policy-${var.env}"
  user   = aws_iam_user.smolvault-user.name
  policy = data.aws_iam_policy_document.smolvault-policy.json
}
