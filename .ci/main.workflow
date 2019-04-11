workflow "Allocate resources on a GENI site" {
  on = "push"
  resolves = "release"
}

action "request" {
  uses = "./"
  args = "./ci/config.py"
  env = {
    GENI_PROJECT = "schedock",
    GENI_EXPERIMENT = "myexp"
    GENI_EXPIRATION = "120",
  }
  secrets = [
    "GENI_USERNAME",
    "GENI_PASSWORD",
    "GENI_PUBKEY_DATA",
    "GENI_CERT_DATA"
  ]
}

action "release" {
  needs = "request"
  uses = "./"
  runs = "release"
  args = "./ci/config.py"
  env = {
    GENI_PROJECT = "schedock",
    GENI_EXPERIMENT = "myexp"
  }
  secrets = [
    "GENI_USERNAME",
    "GENI_PASSWORD",
    "GENI_PUBKEY_DATA",
    "GENI_CERT_DATA"
  ]
}