resource "aws_iam_role" "s3crr_role_for_resume-devious-one_to_my-hosted-resume" {
    name               = "s3crr_role_for_resume.devious.one_to_my-hosted-resume"
    path               = "/service-role/"
    assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "s3.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

