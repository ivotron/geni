# Github Action for GENI build-context from bundle

Builds a GENI context from an OMNI credentials bundle.

## Usage

The action creates a context by using the 
[`context-from-bundle`](https://geni-lib.readthedocs.io/en/latest/tutorials/portalcontext.html) 
tool installed as part of the 
[`geni-lib`](https://geni-lib.readthedocs.io/en/latest/index.html) 
Python package. The context is stored in the `$HOME/.bssw/` folder. 
This context can be subsequently loaded by scripts (see 
[`exec`](../exec/) action).

### Example workflow

The following workflow creates a context for sites available through 
the [GENI Portal](https://portal.geni.net):

```hcl
action "build context" {
  uses = "popperized/build-context-from-bundle@master"
  secrets = ["GENI_BUNDLE_DATA"]
}
```

See 
[here](https://geni-lib.readthedocs.io/en/latest/intro/creds/portal.html) 
for a guide on how to obtain credentials the for GENI Portal.

### Environment

  * `GENI_FRAMEWORK`. **Required** One of `cloudlab`, `emulab`, 
    `portal` and `geni`.

### Secrets

  * `GENI_PROJECT`. **Required** The name of the project.
  * `GENI_USERNAME` **Required** Name of username for GENI account.
  * `GENI_PASSWORD` **Required** Password for user.
  * `GENI_PUBKEY_DATA`. **Required** A base64-encoded string 
    containing the public SSH key for the user authenticating with the 
    site. Example encoding from a terminal: `cat $HOME/.ssh/mykey.pub 
    | base64`.
  * `GENI_CERT_DATA` **Required**. A base64-encoded string containing 
    the certificate issued by the GENI member site. Guides for 
    obtaining credentials are available for 
    [`geni.net`](https://geni-lib.rtfd.io/en/latest/intro/creds/portal.html) 
    and 
    [`cloudlab.us`](https://geni-lib.rtfd.io/en/latest/intro/creds/cloudlab.html). 
    Example encoding from a terminal: `cat cloudlab.pem | base64`.
