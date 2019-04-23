from geni.aggregate import cloudlab
from geni import utils


ctx = utils.loadContext()
utils.deleteSliverExists(cloudlab.Clemson, ctx, 'popperized')
