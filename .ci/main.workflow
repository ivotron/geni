workflow "Allocate and release resources on Cloudlab" {
  on = "push"
  resolves = "teardown"
}

workflow "Run experiment on Cloudlab" {
  on = "push"
  resolves = "teardown"
}

action "build context" {
  uses = "popperized/geni/build-context@master"
  env = {
    GENI_FRAMEWORK = "cloudlab"
  }
  secrets = [
    "GENI_PROJECT",
    "GENI_USER",
    "GENI_PASSWORD",
    "GENI_PUBKEY_DATA",
    "GENI_CERT_DATA"
  ]
}

action "allocate resources" {
  uses = "popperized/geni/exec@master"
  args = "./ci/one-baremetal-node.py"
}

action "teardown" {
  uses = "popperized/geni/exec@master"
  args = "./ci/release.py"
}
