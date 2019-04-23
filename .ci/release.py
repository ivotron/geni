from geni.aggregate import cloudlab
from geni import util


ctx = util.loadContext()
util.deleteSliverExists(cloudlab.Clemson, ctx, 'popperized')
