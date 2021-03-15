resource "aws_route53_record" "devious-one-NS" {
    zone_id = "Z2WJH5BFPC71M3"
    name    = "devious.one"
    type    = "NS"
    records = ["ns-1351.awsdns-40.org.", "ns-1875.awsdns-42.co.uk.", "ns-951.awsdns-54.net.", "ns-126.awsdns-15.com."]
    ttl     = "172800"

}

resource "aws_route53_record" "devious-one-SOA" {
    zone_id = "Z2WJH5BFPC71M3"
    name    = "devious.one"
    type    = "SOA"
    records = ["ns-1351.awsdns-40.org. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"]
    ttl     = "300"

}

resource "aws_route53_record" "resume-devious-one-A" {
    zone_id = "Z2WJH5BFPC71M3"
    name    = "resume.devious.one"
    type    = "A"

    alias {
        name    = "d1zo8ltkxx4133.cloudfront.net"
        zone_id = "Z2FDTNDATAQYW2"
        evaluate_target_health = false
    }
}

resource "aws_route53_record" "_85b00d871a5cd862e121241ba5d8c15f-resume-devious-one-CNAME" {
    zone_id = "Z2WJH5BFPC71M3"
    name    = "_85b00d871a5cd862e121241ba5d8c15f.resume.devious.one"
    type    = "CNAME"
    records = ["_e527b250351b59fd10b4b95d929397cd.mzlfeqexyx.acm-validations.aws."]
    ttl     = "300"

}

