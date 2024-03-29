# Copyright 2019 École Polytechnique Fédérale de Lausanne. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from tensorflow.python.ops import data_flow_ops, string_ops

from ..common.service import Service
from common.parse import numeric_min_checker, path_exists_checker
from ..common import parse

import tensorflow as tf

persona_ops = tf.contrib.persona.persona_ops()
from tensorflow.contrib.persona import queues, pipeline

class CalculateCoverageService(Service):
    """ A class representing a service module in Persona """

    #default inputs
    def get_shortname(self):
        return "coverage"

    def output_dtypes(self):
        return []
    def output_shapes(self):
        return []

    def extract_run_args(self, args):
        dataset = args.dataset
        paths = [ a["path"] for a in dataset["records"] ]
        dataset_dir = args.dataset_dir
        if dataset_dir is None:
            file_path = args.dataset[parse.filepath_key]
            dataset_dir = os.path.dirname(file_path)
        return (os.path.join(dataset_dir, a) for a in paths)

    def add_graph_args(self, parser):
        parser.add_argument("-p", "--parse-parallel", default=1, type=numeric_min_checker(minimum=1, message="read parallelism"),
                            help="total paralellism level for reading data from disk")

        parser.add_argument("-i", "--dataset-dir", type=path_exists_checker(),  help="Directory containing ALL of the chunk files")
        parser.add_argument("-feature","--feature", default='B', help="Feature name")
        parser.add_argument("-o", "--output", help="output directory")

    def make_graph(self, in_queue, args):
        """ Make the graph for this service. Returns two
        things: a list of tensors which the runtime will
        evaluate, and a list of run-once ops"""
        # make the graph
        dataset_dir = args.dataset_dir
        if dataset_dir is None:
            file_path = args.dataset[parse.filepath_key]
            dataset_dir = os.path.dirname(file_path)
        if not os.path.exists(dataset_dir) and os.path.isfile(dataset_dir):
            raise EnvironmentError("metadata file '{m}' either doesn't exist or is not a file".format(m=args.dataset))

        if in_queue is None:
            raise EnvironmentError("in queue is none")

        dataset_dir = os.path.dirname(dataset_dir)
        op = import_sga_local(in_queue=in_queue,
                                       outdir=dataset_dir,
                                       parallel_parse=args.parse_parallel,
                                       argsj = args,
                                       feature = args.feature,
				       path = args.output)
        run_once = []
        return [[op]] , run_once



def compress_pipeline(results, compress_parallelism):

    buf_pool = persona_ops.buffer_pool(size=0, bound=False, name="bufpool")

    for buf, num_recs, first_ord, record_id in results:
        compressed_buf = persona_ops.buffer_pair_compressor(buffer_pool=buf_pool, buffer_pair=buf)

        yield compressed_buf, num_recs, first_ord, record_id

def import_sga_local(in_queue, argsj,outdir=None, parallel_parse=1,feature = "NFAT", path="."):
    manifest = argsj.dataset
    if 'reference' not in manifest:
        raise Exception("No reference data in manifest {}. Unaligned BAM not yet supported. Please align dataset first.".format(args.dataset))

    """
    key: tensor with chunk key string
    local_directory: the "base path" from which these should be read
    column_grouping_factor: the number of keys to put together
    parallel_parse: the parallelism for processing records (decomp)
    """

    ref_lens = []
    ref_seqs = []
    for contig in manifest['reference_contigs']:
       ref_lens.append(contig['length'])
       ref_seqs.append(contig['name'])

    parallel_key_dequeue = tuple(in_queue.dequeue() for _ in range(parallel_parse))
    result_chunks = pipeline.local_read_pipeline(upstream_tensors=parallel_key_dequeue, columns=['results'])

    result_chunk_list = [ list(c) for c in result_chunks ]


    parsed_results = pipeline.agd_reader_multi_column_pipeline(upstream_tensorz=result_chunk_list)
    parsed_results_list = list(parsed_results)

    parsed_result = pipeline.join(parsed_results_list, parallel=1, capacity=8, multi=True)[0]



    result_buf, num_results, first_ord, record_id = parsed_result
    result_buf = tf.unstack(result_buf)[0]



    result = persona_ops.import_sga(results_handle=result_buf, num_records=num_results,ref_sequences=ref_seqs,ref_seq_sizes=ref_lens, feature = feature,path=path,name="importsgaop")

    return result
