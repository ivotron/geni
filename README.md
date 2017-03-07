# geni-lib

Convenience container to execute geni-lib scripts. Usage:

```bash
docker run --rm \
  -v `pwd`/request.py:/request.py \
  ivotron/geni-lib /request.py
```

where `request.py` contains a valid request for infrastructure deployment on 
a GENI site. For example:

```python
import geni.util

from geni.aggregate import cloudlab as cl
from geni.rspec import pg as rspec

ctxt = geni.util.loadContext('/request.json', key_passphrase=True)

node = rspec.RawPC("node")
node.disk_image = "urn:publicid:IDN+image//UBUNTU16-64-STD"

r = rspec.Request()

r.addResource(node)

m = cl.UtahDDC.createsliver(ctxt, "node", r)
```

For more info, check the [official documentation](http://geni-lib.readthedocs.io/en/latest/index.html).
