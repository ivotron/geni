# Github action for executing GENI scripts

A wrapper for [geni-lib](https://bitbucket.org/barnstorm/geni-lib), 
the Python library for programatically allocating resources in sites 
that are part of the NSF-sponsored [GENI 
federation](https://www.geni.net) such as 
[CloudLab](https://cloudlab.us).

## Usage

This action takes a Python script that manipulates infrastructure on a 
GENI site via `geni-lib`. A context needs to be created by executing 
the [`build-context`](../build-context) or 
[`build-context-from-bundle`](../build-context-from-bundle) actions; 
both store the resulting context in the `$HOME/.bssw/` folder. Once a 
context is created, the given script can load it by invoking the 
[`geni.util.loadContext()`](https://bitbucket.org/barnstorm/geni-lib/src/1b480c83581207300f73679af6844d327794d45e/geni/util.py#lines-357) 
function and execute arbitrary orchestration tasks against 
GENI-enabled infrastructure. Check the [official `geni-lib` 
documentation](https://geni-lib.rtfd.io) for more information on how 
to use `geni-lib`. Concrete examples can be found 
[here](https://bitbucket.org/barnstorm/geni-lib/src/1b480c83581207300f73679af6844d327794d45e/samples/?at=0.9-DEV) 
and [here](http://docs.cloudlab.us/geni-lib.html).

> **NOTE**: in non-interactive mode, the `geni.util.loadContext()` 
> function requires the key passphrase (via the `key_passphrase` 
> argument) for the public key provided to the action that builds the 
> context. In those cases, the `GENI_KEY_PASSPHRASE` secret needs to 
> be defined and passed to the `geni.util.loadContext()` function. See 
> an example [here](../.ci/teardown.py).

### Example workflow

The following shows an example workflow that allocates resources on 
GENI infrastructure:

```hcl
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
    "GENI_USERNAME",
    "GENI_PASSWORD",
    "GENI_PUBKEY_DATA",
    "GENI_CERT_DATA"
  ]
}

action "allocate resources" {
  uses = "popperized/geni/exec@master"
  args = "one-baremetal-node.py"
  secrets = ["GENI_KEY_PASSPHRASE"]
}

# ...
# other actions that use allocated resources
# ...

action "teardown" {
  uses = "popperized/geni/exec@master"
  args = "release.py"
  secrets = ["GENI_KEY_PASSPHRASE"]
}
```

The scripts used above can be found [in this folder](../.ci/) and work 
on CloudLab. The value of `GENI_KEY_PASSPHRASE` in the case of 
CloudLab is CloudLab's account password.

### Secrets

  * `GENI_KEY_PASSPHRASE`. **Optional** The key passphrase associated 
    to the public key used when building a context.
