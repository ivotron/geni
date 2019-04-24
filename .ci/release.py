import os

from geni.aggregate import cloudlab
from geni import util


ctx = util.loadContext(key_passphrase=os.environ['GENI_KEY_PASSPHRASE'])

if util.sliceExists(ctx, 'popperized'):
    util.deleteSliverExists(cloudlab.Clemson, ctx, 'popperized')
else:
    print("Slice 'popperized' does not exist")
