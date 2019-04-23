from geni.aggregate import cloudlab
from geni.rspec import pg
from geni import utils

# create request
# {
node = pg.RawPC("node")

node.disk_image = "urn:publicid:IDN+clemson.cloudlab.us+image+schedock-PG0:ubuntu18-docker"
node.hardware_type = 'c6320'

request = pg.Request()
request.addResource(node)
# }

# load context
ctx = utils.loadContext()

# create slice
utils.createSlice(ctx, 'popperized')

# create sliver on clemson
utils.createSliver(ctx, cloudlab.Clemson, 'popperized', request)
