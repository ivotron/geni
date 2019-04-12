from geni.aggregate import cloudlab
from geni.rspec import pg

node = pg.RawPC("node")

node.disk_image = "urn:publicid:IDN+clemson.cloudlab.us+image+schedock-PG0:ubuntu18-docker"
node.hardware_type = 'c6320'

request = pg.Request()
request.addResource(node)

aggregate = cloudlab.Clemson
