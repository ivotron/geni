# Github action for GENI

Wrapper for [geni-lib](https://bitbucket.org/barnstorm/geni-lib), the 
library for programatically allocating resources in sites that are 
part of the NSF-sponsored [GENI federation](https://www.geni.net) such 
as [CloudLab](https://cloudlab.us).

## Usage

There is only one action defined, which expects a Python script that 
creates a valid request for infrastructure deployment on a GENI site. 
Two variables, `request` and `aggregate`, should be defined by the 
script. These are used by the following commands:

  * `request`. Creates a slice on `aggregate` and allocates resources 
    specified in `request`. If the slice already exists, any sliver 
    for `GENI_EXPERIMENT` on the given `aggregate` is deleted. In 
    addition, if the slice exists, the `renew` command gets executed 
    first.

  * `release`. Releases resources for `GENI_EXPERIMENT` on `aggregate`. 
    The sliver for the experiment on the specified aggregate is 
    deleted.

  * `renew`. Renews the slice in the specified `aggregate`, for as 
    long as determined by the `GENI_EXPIRATION` environment variable.

By default, the `request` command is invoked. For more information on 
how to create requests, check the [official geni-lib 
documentation](https://geni-lib.rtfd.io).

### Example workflow file

```hcl
workflow "Run experiment on a GENI site" {
  on = "push"
  resolves = "teardown"
}

action "allocate" {
  uses = "popperized/geni@master"
  args = "request config.py"
  env = {
    GENI_PROJECT = "myproject",
    GENI_EXPERIMENT = "myexp",
    GENI_EXPIRATION = "120",
  }
  secrets = [
    "GENI_USER",
    "GENI_PASSWORD",
    "GENI_PUBKEY_DATA",
    "GENI_CERT_DATA"
  ]
}

# ...
# a bunch of actions that use allocated resources
# ...

action "teardown" {
  needs = "allocate"
  uses = "popperized/geni@master"
  args = "release config.py"
  env = {
    GENI_PROJECT = "myproject",
    GENI_EXPERIMENT = "myexp",
    GENI_EXPIRATION = "120",
  }
  secrets = [
    "GENI_USER",
    "GENI_PASSWORD",
    "GENI_PUBKEY_DATA",
    "GENI_CERT_DATA"
  ]
}
```

and the contents of the `config.py` file might look like:

```python
from geni.aggregate import cloudlab
from geni.rspec import pg

node = pg.RawPC("node")

node.disk_image = "urn:publicid:IDN+clemson.cloudlab.us+image+schedock-PG0:ubuntu18-docker"
node.hardware_type = 'c6320'

request = pg.Request()
request.addResource(node)

aggregate = cloudlab.Clemson
```

The particular example above requests one bare-metal node of type 
`c6320` on CloudLab's Clemson site. More examples available 
[here](https://bitbucket.org/barnstorm/geni-lib/src/1b480c83581207300f73679af6844d327794d45e/samples/?at=0.9-DEV).

### Environment

  * `GENI_PROJECT`. **Required** The name of the project.
  * `GENI_EXPERIMENT` **Required** Name of the experiment.
  * `GENI_EXPIRATION` **Optional** Number of minutes after which the 
    reservation will expire. Defaults to `120`.

### Secrets

  * `GENI_USERNAME` **Required** Name of user, e.g. for 
    <https://geni.net>, <https://cloudlab.us>, etc.
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
