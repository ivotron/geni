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
for a guide on how to obtain credentials for the GENI Portal.

### Secrets

  * `GENI_BUNDLE_DATA` **Required**. A base64-encoded string 
    containing the bundle issued by a GENI member portal. Guides for 
    obtaining credentials are available for 
    [`geni.net`](https://geni-lib.rtfd.io/en/latest/intro/creds/portal.html) 
    and 
    [`cloudlab.us`](https://geni-lib.rtfd.io/en/latest/intro/creds/cloudlab.html). 
    Example encoding from a terminal: `cat omni.bundle | base64`.
