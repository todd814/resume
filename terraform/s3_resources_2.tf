resource "aws_s3_bucket" "my-hosted-resume" {
    bucket = "my-hosted-resume"
    acl    = "private"
    policy = <<POLICY
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-hosted-resume/*"
    }
  ]
}
POLICY
}

resource "aws_s3_bucket" "resume-devious-one" {
    bucket = "resume.devious.one"
    acl    = "private"
    policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "PolicyForCloudFrontPrivateContent",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E3GCE4EG15FM3K"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::resume.devious.one/*"
    }
  ]
}
POLICY
}