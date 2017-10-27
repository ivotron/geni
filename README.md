# geni-lib

Convenience container to execute geni-lib scripts. Usage:

```bash
docker run --rm \
  -v `pwd`/request.py:/request.py \
  ivotron/geni-lib /request.py
```

where `request.py` contains a valid request for infrastructure 
deployment on a GENI site. For more info, check the [official 
documentation](http://geni-lib.readthedocs.io/en/latest/index.html).

## CloudLab

This image provides a `geni.cloudlab_util` module that mimics the 
behavior at [CloudLab](http://docs.cloudlab.us/geni-lib.html), 
allowing users to define an experiment profile by providing a snippet 
of python code that defines an experiment. An example of how to make 
use of this:

```python
#!/usr/bin/env python

import geni.cloudlab_util as cl
from geni.rspec import pg as rspec

node = rspec.RawPC("node")
img = "urn:publicid:IDN+apt.emulab.net+image+schedock-PG0:docker-ubuntu16:0"
node.disk_image = img

r = rspec.Request()
r.addResource(node)

m = cl.request(experiment_name='myexp',
               sites=['utah', 'clemson'],
               request=r,
               expiration=240,
               timeout=15,
               cloudlab_user='myuser',
               cloudlab_password='mypassword',
               cloudlab_project='myproject',
               cloudlab_cert_path='/path/to/cloudlab.pem',
               cloudlab_pubkey_path='/path/to/cloudlab_rsa.pub')

# read info in manifests to introspect allocation

# run your experiment...

# once done with experiment, release resources
m = cl.request(experiment_name='myexp',
               cloudlab_user='myuser',
               cloudlab_password='mypassword',
               cloudlab_project='myproject',
               cloudlab_cert_path='/path/to/cloudlab.pem',
               cloudlab_pubkey_path='/path/to/cloudlab_rsa.pub')
```

The example above instantiates an experiment (named `myexp`) 
consisting of 1 node on both `utah` and `clemson` sites. By default, 
if `cloudlab_*` arguments are not given, the script tries to read this 
information from the environment (from variables `CLOUDLAB_USER`, 
`CLOUDLAB_PASSWORD`, etc.). All these need to be in lower case. 
This helps to avoid storing credentials in a script and can be given
as part of the docker invocation instead:

```bash
docker run --rm \
  -e CLOUDLAB_USER=myuser \
  -e CLOUDLAB_PASSWD='my#unbreakable%crazy&password' \
  -e CLOUDLAB_CERT_PATH=$HOME/.ssh/cloudlab.pem \
  -e CLOUDLAB_KEY_PATH=$HOME/.ssh/cloudlab_rsa.pub \
  -e CLOUDLAB_PROJECT=myproject \
  -v `pwd`/request.py:/request.py \
  ivotron/geni-lib /request.py
```

The `request()` function returns a dictionary of manifests, with one 
entry per CloudLab site (with site names as keys). These can be 
introspected to determine the details of the CloudLab instantiation. 
For example, obtaining the IP addresses of requested nodes. By 
default, the request times out after 15 minutes if the status of _all_ 
has not transitioned to `ready`. This can be overridden by passing a 
`timout` argument. Similarly, the expiration of an experiment (in 
minutes) can be specified via the `expiration` argument (4 hours by 
default). Once an experiment has been completed, resources can be 
released with the `release()` function.
