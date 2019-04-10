# Github action for GENI

Wrapper for [geni-lib](https://bitbucket.org/barnstorm/geni-lib), the 
library for programatically allocating resources in sites that are 
part of the NSF-sponsored [GENI federation](https://www.geni.net) such 
as [CloudLab](https://cloudlab.us).

## Usage

There is only one action defined, which expects a Python script that 
creates a valid request for infrastructure deployment on a GENI site. 
Two variables, `request` and `aggregate`, should be defined by the 
script. These are used by one of the following commands:

  * `request`. Create a slice on `aggregate` and allocate resources 
    specified in `request`. If the slice already exists, any sliver 
    for `GENI_EXPERIMENT` on the given `aggregate` is deleted. In 
    addition, if the slice exists, the `renew` command gets executed 
    first.

  * `release`. Release resources for `GENI_EXPERIMENT` on `aggregate`. 
    The sliver for the experiment on the specified aggregate is 
    deleted.

  * `renew`. Renews the slice in the specified `aggregate`, for as 
    long as determined by the `GENI_EXPIRATION` environment variable.

By default, the `request` command is invoked. For more information on 
how to create requests, check the [official geni-lib 
documentation](https://geni-lib.rtfd.io).

### Example workflow file

```hcl
workflow "Allocate resources on a GENI site" {
  on = "push"
  resolves = "request"
}

action "request" {
  uses = "popperized/geni@master"
  args = "config.py"
  env = {
    GENI_EXPERIMENT = "myexp"
    GENI_EXPIRATION = "120",
  }
  secrets = [
    "GENI_USER",
    "GENI_PASSWORD",
    "GENI_PROJECT",
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

node.disk_image = "urn:publicid:IDN+apt.emulab.net+image+schedock-PG0:docker-ubuntu16:0"
node.hardware_type = 'c6320'

request = pg.Request()
request.addResource(node)

aggregate = cloudlab.Clemson
```

The above requests a bare-metal node of type `c6320` on CloudLab's 
Clemson site. More examples available 
[here](https://bitbucket.org/barnstorm/geni-lib/src/1b480c83581207300f73679af6844d327794d45e/samples/?at=0.9-DEV).

### Secrets

  * `GENI_USER` **Required** Name of user for the 
