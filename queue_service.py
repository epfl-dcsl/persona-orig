#!/usr/bin/env python3

import argparse
import tensorflow as tf
from runtime import dist_common

import logging
logging.basicConfig()
log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)

def run():
    parser = argparse.ArgumentParser(description="Queue Service", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    dist_common.queue_only_args(parser=parser)
    cluster_name = dist_common.cluster_name
    args = parser.parse_args()
    queue_index = args.queue_index
    cluster_spec = dist_common.make_cluster_spec(cluster_members=args.cluster_members)
    cluster_spec.task_address(job_name=cluster_name, task_index=queue_index)
    server = tf.train.Server(cluster_spec, config=None, job_name=cluster_name, task_index=queue_index)
    log.debug("Starting queue host server")
    with tf.Session(server.target) as sess:
        with dist_common.quorum(cluster_spec=cluster_spec, task_index=queue_index, session=sess) as wait_op:
            wait_op()

if __name__ == "__main__":
    run()