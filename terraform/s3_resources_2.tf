# Portfolio assets bucket — publicly readable via bucket policy
resource "aws_s3_bucket" "my-hosted-resume" {
  bucket = "my-hosted-resume"
}

resource "aws_s3_bucket_public_access_block" "my-hosted-resume" {
  bucket = aws_s3_bucket.my-hosted-resume.id

  block_public_acls       = true
  block_public_policy     = false
  ignore_public_acls      = true
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "my-hosted-resume" {
  bucket     = aws_s3_bucket.my-hosted-resume.id
  depends_on = [aws_s3_bucket_public_access_block.my-hosted-resume]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowPublicRead"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.my-hosted-resume.arn}/*"
      }
    ]
  })
}

# Resume website bucket — private, served via CloudFront OAI
resource "aws_s3_bucket" "resume-devious-one" {
  bucket = "resume.devious.one"
}

resource "aws_s3_bucket_public_access_block" "resume-devious-one" {
  bucket = aws_s3_bucket.resume-devious-one.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "resume-devious-one" {
  bucket = aws_s3_bucket.resume-devious-one.id

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "PolicyForCloudFrontPrivateContent"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E3GCE4EG15FM3K"
        }
        Action   = "s3:GetObject"
        Resource = "${aws_s3_bucket.resume-devious-one.arn}/*"
      }
    ]
  })
}