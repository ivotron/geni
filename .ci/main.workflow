workflow "Allocate and release resources on Cloudlab" {
  on = "push"
  resolves = "teardown"
}

workflow "Run experiment on Cloudlab" {
  on = "push"
  resolves = "teardown"
}

action "build context" {
  uses = "./build-context"
  env = {
    GENI_FRAMEWORK = "cloudlab"
  }
  secrets = [
    "GENI_PROJECT",
    "GENI_USERNAME",
    "GENI_PASSWORD",
    "GENI_PUBKEY_DATA",
    "GENI_CERT_DATA"
  ]
}

action "allocate resources" {
  uses = "./exec"
  args = "./ci/one-baremetal-node.py"
}

action "teardown" {
  uses = "./exec"
  args = "./ci/release.py"
}
