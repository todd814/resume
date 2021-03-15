resource "aws_iam_policy" "s3crr_for_resume-devious-one_to_my-hosted-resume" {
    name        = "s3crr_for_resume.devious.one_to_my-hosted-resume"
    path        = "/service-role/"
    description = ""
    policy      = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:Get*",
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::resume.devious.one",
        "arn:aws:s3:::resume.devious.one/*"
      ]
    },
    {
      "Action": [
        "s3:ReplicateObject",
        "s3:ReplicateDelete",
        "s3:ReplicateTags",
        "s3:GetObjectVersionTagging"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::my-hosted-resume/*"
    }
  ]
}
POLICY
}