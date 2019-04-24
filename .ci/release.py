import os

from geni.aggregate import cloudlab
from geni import util


ctx = util.loadContext(key_passphrase=os.environ['GENI_KEY_PASSPHRASE'])
util.deleteSliverExists(cloudlab.Clemson, ctx, 'popperized')
