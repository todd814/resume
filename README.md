# resume <br>
[![CI](https://github.com/todd814/resume/actions/workflows/ci.yml/badge.svg)](https://github.com/todd814/resume/actions/workflows/ci.yml) [![Terraform Plan & Test](https://github.com/todd814/resume/actions/workflows/terraform.yml/badge.svg)](https://github.com/todd814/resume/actions/workflows/terraform.yml) [![Lint](https://github.com/todd814/resume/actions/workflows/lint.yml/badge.svg)](https://github.com/todd814/resume/actions/workflows/lint.yml) <br>
Source code for my online resume processed using GitHub Actions and hosted on AWS S3 as a single page website.<br>
I've also set up terraform cloud integration to automate my AWS infrastructure (IAC) configuration files are located within the terraform dir.<br>
My AWS infrastructure currently consists of a Route53 hosted zone. CloudFront handles content distribution and page resources are located in a S3 bucket. <br>
https://resume.devious.one <br>