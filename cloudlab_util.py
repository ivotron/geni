#!/usr/bin/env python

from geni.aggregate import cloudlab as cl
from geni.aggregate import protogeni as pg
from geni.aggregate.apis import DeleteSliverError
from geni.aggregate.frameworks import ClearinghouseError
from geni.minigcf.config import HTTP
from geni.util import loadContext

import datetime
import json
import os
import time

HTTP.TIMEOUT = 300

aggregate = {
    'apt': cl.Apt,
    'cl-clemson': cl.Clemson,
    'cl-utah': cl.Utah,
    'cl-wisconsin': cl.Wisconsin,
    'ig-utahddc': cl.UtahDDC,
    'pg-kentucky': pg.Kentucky_PG,
    'pg-utah': pg.UTAH_PG,
}


def check_var(argument, varname):
    if not argument and not os.environ[varname]:
        raise Exception("Expecting '{}' environment variable".format(varname))

    return os.environ[varname]


def get_slice(cloudlab_user, cloudlab_password,
              cloudlab_project, cloudlab_cert_path,
              cloudlab_key_path, experiment_name, expiration=120,
              create_if_not_exists=False, renew_slice=False):

    cloudlab_user = check_var(cloudlab_user, 'CLOUDLAB_USER')
    cloudlab_password = check_var(cloudlab_password, 'CLOUDLAB_PASSWORD')
    cloudlab_project = check_var(cloudlab_project, 'CLOUDLAB_PROJECT')
    cloudlab_cert_path = check_var(cloudlab_cert_path, 'CLOUDLAB_CERT_PATH')
    cloudlab_key_path = check_var(cloudlab_key_path, 'CLOUDLAB_PUBKEY_PATH')

    with open('/tmp/context.json', 'w') as f:
        data = {
            "framework": "emulab-ch2",
            "cert-path": cloudlab_cert_path,
            "key-path": cloudlab_cert_path,
            "user-name": cloudlab_user,
            "user-urn": "urn:publicid:IDN+emulab.net+user+"+cloudlab_user,
            "user-pubkeypath": cloudlab_key_path,
            "project": cloudlab_project
        }
        json.dump(data, f)

    c = loadContext("/tmp/context.json", key_passphrase=cloudlab_password)

    slice_id = (
        "urn:publicid:IDN+emulab.net:{}+slice+{}"
    ).format(cloudlab_project, experiment_name)

    exp = datetime.datetime.now() + datetime.timedelta(minutes=expiration)

    if slice_id in c.cf.listSlices(c):
        if renew_slice:
            c.cf.renewSlice(c, experiment_name, exp=exp)
    else:
        if create_if_not_exists:
            c.cf.createSlice(c, experiment_name, exp=exp)
        else:
            return None

    return c


def do_request(ctxt, exp_name, requests, timeout, ignore_failed_slivers):

    manifests = {}
    for site, request in requests.iteritems():
        print("Creating sliver on " + site)

        try:
            manifests[site] = aggregate[site].createsliver(ctxt, exp_name,
                                                           request)
        except ClearinghouseError:
            # sometimes slice creating takes a bit, so we wait for 30 secs
            time.sleep(30)
            manifests[site] = aggregate[site].createsliver(ctxt, exp_name,
                                                           request)

    print("Waiting for resources to come up online")
    sites = set(requests.keys())
    ready = set()
    timeout = time.time() + 60 * timeout
    while True:
        time.sleep(60)
        for site in sites - ready:
            try:
                status = aggregate[site].sliverstatus(ctxt, exp_name)
            except:
                break

            if status['pg_status'] == 'ready':
                ready.add(site)

        if sites == ready:
            # all good!
            break

        if time.time() > timeout:
            if ignore_failed_slivers:
                break

            for site in sites - ready:
                do_release(ctxt, exp_name, [site])
                del manifests[site]
            raise Exception("Not all nodes came up after 15 minutes")

    return manifests


def do_release(ctxt, exp_name, sites):
    for site in sites:
        try:
            print('Deleting sliver on ' + site + ".")
            aggregate[site].deletesliver(ctxt, exp_name)
        except ClearinghouseError:
            print('Got ClearinghouseError... attempting to delete again.')
            time.sleep(10)
            try:
                aggregate[site].deletesliver(ctxt, exp_name)
            except DeleteSliverError:
                print('Got DeleteSilverError... skipping site.')
                continue
        except DeleteSliverError:
            print('Got DeleteSilverError... skipping site.')
            continue
        except:
            raise

    print('Finished releasing resources on all sites')


def request(experiment_name=None, requests=None, timeout=15, expiration=120,
            cloudlab_user=None, cloudlab_password=None,
            cloudlab_project=None, cloudlab_cert_path=None,
            cloudlab_key_path=None, ignore_failed_slivers=True):

    if not experiment_name or not requests:
        raise Exception("Expecting 'experiment_name' and 'requests' args")

    ctxt = get_slice(cloudlab_user, cloudlab_password, cloudlab_project,
                     cloudlab_cert_path, cloudlab_key_path,
                     experiment_name, expiration,
                     create_if_not_exists=True, renew_slice=True)

    return do_request(ctxt, experiment_name, requests,
                      timeout, ignore_failed_slivers)


def print_slivers(experiment_name, cloudlab_user=None,
                  cloudlab_password=None, cloudlab_project=None,
                  cloudlab_cert_path=None, cloudlab_key_path=None):
    print('Checking if slice for experiment exists')
    ctxt = get_slice(cloudlab_user, cloudlab_password, cloudlab_project,
                     cloudlab_cert_path, cloudlab_key_path,
                     experiment_name)
    if ctxt is None:
        print("We couldn't find a slice for {}.".format(experiment_name))
    else:
        for site in aggregate.keys():
            status = aggregate[site].sliverstatus(ctxt, experiment_name)
            print(json.dumps(status, indent=2))


def release(experiment_name=None, cloudlab_user=None,
            cloudlab_password=None, cloudlab_project=None,
            cloudlab_cert_path=None, cloudlab_key_path=None):

    ctxt = get_slice(cloudlab_user, cloudlab_password, cloudlab_project,
                     cloudlab_cert_path, cloudlab_key_path,
                     experiment_name)
    if ctxt is not None:
        do_release(ctxt, experiment_name, aggregate.keys())
    else:
        print('No slice for experiment, all done.')
