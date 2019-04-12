#!/usr/bin/env python
from geni.aggregate.apis import DeleteSliverError
from geni.aggregate.frameworks import ClearinghouseError
from geni.minigcf.config import HTTP
from geni.util import loadContext

import datetime
import json
import os
import time
import sys

HTTP.TIMEOUT = 600


def get_var(varname):
    var = os.environ.get(varname, None)
    if not var:
        raise Exception("Expecting '{}' environment variable".format(varname))
    return var


def get_slice(create_if_not_exists=False, renew_slice=False):

    with open('/tmp/context.json', 'w') as f:
        data = {
            "framework": "emulab-ch2",
            "cert-path": geni_cert_path,
            "key-path": geni_cert_path,
            "user-name": geni_user,
            "user-urn": "urn:publicid:IDN+emulab.net+user+"+geni_user,
            "user-pubkeypath": geni_key_path,
            "project": geni_project
        }
        json.dump(data, f)

    print("Loading GENI context")
    c = loadContext("/tmp/context.json", key_passphrase=geni_password)

    slice_id = (
        "urn:publicid:IDN+emulab.net:{}+slice+{}"
    ).format(geni_project, experiment_name)

    exp = datetime.datetime.now() + datetime.timedelta(minutes=expiration)

    print("Available slices: {}".format(c.cf.listSlices(c).keys()))

    if slice_id in c.cf.listSlices(c):
        print("Using existing slice {}".format(slice_id))
        if renew_slice:
            print("Renewing slice for {} more minutes".format(expiration))
            c.cf.renewSlice(c, experiment_name, exp=exp)
    else:
        if create_if_not_exists:
            print("Creating slice {} ({} minutes)".format(slice_id,
                                                          expiration))
            c.cf.createSlice(c, experiment_name, exp=exp)
        else:
            print("We couldn't find a slice for {}.".format(experiment_name))
            return None

    return c


def do_request(ctxt, timeout=15, ignore_failed_slivers=True,
               skip_unavailable_hwtypes=True):

    print("Creating sliver")

    manifest = None

    try:
        manifest = aggregate.createsliver(ctxt, experiment_name, request)
    except ClearinghouseError:
        # sometimes slice creating takes a bit, so we wait for 30 secs
        time.sleep(30)
        manifest = aggregate.createsliver(ctxt, experiment_name, request)
    except Exception as e:
        print("Failed trying to create sliver.")
        print(e)
        if ignore_failed_slivers:
            print("Will ignore and keep going")
            try:
                aggregate.deletesliver(ctxt, experiment_name)
            except DeleteSliverError as delerror:
                print('Got DeleteSilverError... skipping site.')
                print(delerror)

    print("Waiting for resources to come up online")
    timeout = time.time() + 60 * timeout
    while True:
        time.sleep(60)
        try:
            status = aggregate.sliverstatus(ctxt, experiment_name)
        except Exception:
            break

        if status['pg_status'] == 'ready':
            break

        if time.time() > timeout:
            if ignore_failed_slivers:
                break

            do_release(ctxt)

            raise Exception(
                "Timeout waiting for resources ({} mins)".format(timeout))

    return manifest


def do_release(ctxt):
    if not ctxt:
        print('No slice for experiment, all done.')
        return

    try:
        print('Deleting sliver.')
        aggregate.deletesliver(ctxt, experiment_name)
    except ClearinghouseError as e:
        print('Got ClearinghouseError: "{}". Retrying.'.format(e))
        time.sleep(10)
        try:
            aggregate.deletesliver(ctxt, experiment_name)
        except DeleteSliverError as err:
            print('Got DeleteSilverError: "{}". Skipping.'.format(err))
    except DeleteSliverError as e:
        print('Got DeleteSilverError: "{}". Skipping site.'.format(e))
    except Exception:
        raise

    print('Finished releasing resources on all sites')


def do_renew(ctxt):
    if not ctxt:
        print('No slice for experiment, all done.')
        return

    exp = datetime.datetime.now() + datetime.timedelta(minutes=expiration)

    try:
        aggregate.renewsliver(ctxt, experiment_name, exp)
        status = aggregate.sliverstatus(ctxt, experiment_name)
    except Exception as e:
        print("#####################")
        print("{}: {}\n. Skipping.".format(e))
        print("#####################")
    print(json.dumps(status, indent=2))


geni_user = get_var('GENI_USERNAME')
geni_password = get_var('GENI_PASSWORD')
geni_project = get_var('GENI_PROJECT')
geni_cert_path = get_var('GENI_CERT_PATH')
geni_key_path = get_var('GENI_PUBKEY_PATH')
experiment_name = get_var('GENI_EXPERIMENT')
expiration = int(os.environ.get('GENI_EXPIRATION', 120))
request = None
aggregate = None

if __name__ == '__main__':
    cmd = sys.argv[1]
    cfg = sys.argv[2]

    exec(compile(open(cfg, 'rb').read(), cfg, 'exec'), globals())

    if not request:
        print("'request' variable not defined in {}".format(cfg))
        sys.exit(1)

    if not aggregate:
        print("'aggregate' variable not defined in {}".format(cfg))
        sys.exit(1)

    print('Aggregate: {}'.format(aggregate.name))
    print('Request:\n{}'.format(request.toXMLString(pretty_print=True)))

    if cmd == 'request':

        ctxt = get_slice(create_if_not_exists=True, renew_slice=True)
        manifest = do_request(ctxt)

        if not manifest:
            print("Got an empty manifest")
            sys.exit(1)

        try:
            manifest_str = serialize_manifest(manifest)
        except NameError:
            print("No 'serialize_manifest' function defined, dumping to XML")
            manifest_str = manifest.text

        outfile_path = '{}/{}.xml'.format(
            os.environ['GITHUB_WORKSPACE'], experiment_name)

        with open(outfile_path, 'w') as mf:
            mf.write(manifest_str)

    elif cmd == 'renew':
        ctxt = get_slice(create_if_not_exists=False, renew_slice=True)
        do_renew(ctxt)
    elif cmd == 'release':
        ctxt = get_slice()
        do_release(ctxt)
    else:
        print('Unknown command {}'.format(cmd))
        sys.exit(1)
