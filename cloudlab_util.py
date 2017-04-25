#!/usr/bin/env python

from geni.aggregate import cloudlab as cl
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
    'utah': cl.Utah,
    'wisconsin': cl.Wisconsin,
    'clemson': cl.Clemson,
    'utahddc': cl.UtahDDC,
    'apt': cl.Apt
}


def check_var(argument, varname):
    if not argument and not os.environ[varname]:
        raise Exception("Expecting '{}' environment variable".format(varname))

    return os.environ[varname]


def get_slice(cloudlab_user, cloudlab_password,
              cloudlab_project, cloudlab_cert_path,
              cloudlab_key_path, experiment_name, expiration,
              create_if_not_exists=False):

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
        c.cf.renewSlice(c, experiment_name, exp=exp)
    elif slice_id not in c.cf.listSlices(c) and create_if_not_exists:
        c.cf.createSlice(c, experiment_name, exp=exp)
    else:
        return None

    return c


def do_request(ctxt, exp_name, sites, request, timeout):
    # in case they were still up from previous execution
    do_release(ctxt, experiment_name, sites)

    manifests = {}
    for site in sites:
        print("Creating sliver on " + site)
        manifests[site] = aggregate[site].createsliver(ctxt, exp_name, request)

    print("Waiting for resources to come up online")
    timeout = time.time() + 60 * timeout
    while True:
        time.sleep(30)
        all_up = []
        for site in sites:
            try:
                status = aggregate[site].sliverstatus(ctxt, exp_name)
            except:
                break

            if status['pg_status'] != 'ready':
                break
            all_up += [site]

        if sites == all_up:
            # all good!
            break

        if time.time() > timeout:
            do_release(ctxt, sites, exp_name)
            raise Exception("Not all nodes came up after 15 minutes")

    return manifests


def do_release(ctxt, exp_name, sites):
    for site in sites:
        try:
            aggregate[site].deletesliver(ctxt, exp_name)
        except ClearinghouseError:
            time.sleep(30)
            try:
                aggregate[site].deletesliver(ctxt, exp_name)
            except DeleteSliverError:
                continue
        except DeleteSliverError:
            continue
        except:
            raise


def request(experiment_name=None, sites=None, timeout=15, expiration=240,
            request=None, cloudlab_user=None, cloudlab_password=None,
            cloudlab_project=None, cloudlab_cert_path=None,
            cloudlab_key_path=None):

    if not experiment_name or not sites or not request:
        raise Exception("Expecting 'sites', 'name' and 'request' args")

    ctxt = get_slice(cloudlab_user, cloudlab_password, cloudlab_project,
                     cloudlab_cert_path, cloudlab_key_path,
                     experiment_name, expiration,
                     create_if_not_exists=True)

    return do_request(ctxt, experiment_name, sites, request, timeout)


def release(experiment_name=None, cloudlab_user=None, cloudlab_password=None,
            cloudlab_project=None, cloudlab_cert_path=None,
            cloudlab_key_path=None):

    get_slice(cloudlab_user, cloudlab_password, cloudlab_project,
              cloudlab_cert_path, cloudlab_key_path,
              experiment_name, 2, create_if_not_exists=False)
