workflow "Allocate and release resources on Cloudlab" {
  on = "push"
  resolves = "teardown"
}

action "lint" {
  uses = "actions/bin/shellcheck@master"
  args = "./*/*.sh"
}

action "build context" {
  uses = "./build-context"
  needs = "lint"
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
  needs = "build context"
  args = ".ci/one-baremetal-node.py"
  secrets = ["GENI_KEY_PASSPHRASE"]
}

action "teardown" {
  uses = "./exec"
  needs = "allocate resources"
  args = ".ci/release.py"
  secrets = ["GENI_KEY_PASSPHRASE"]
}
