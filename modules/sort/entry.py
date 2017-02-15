import argparse

def get_tooltip():
  return "Sort an AGD dataset"

def run(args):
  meta_file = args.metadata_file
  if not os.path.exists(meta_file) and os.path.isfile(meta_file):
      raise EnvironmentError("metadata file '{m}' either doesn't exist or is not a file".format(m=meta_file))

  ceph_params = args.ceph_params
  if not os.path.exists(ceph_params) and os.path.isfile(ceph_params):
      raise EnvironmentError("Ceph Params file '{}' isn't correct".format(ceph_params))

  a = args.ceph_read_chunk_size
  if a < 1:
      raise EnvironmentError("Ceph read chunk size most be strictly positive! Got {}".format(a))
  print("Running sort!")

def get_args(subparser):
  def numeric_min_checker(minimum, message):
      def check_number(n):
          n = int(n)
          if n < minimum:
              raise argparse.ArgumentError("{msg}: got {got}, minimum is {minimum}".format(
                  msg=message, got=n, minimum=minimum
              ))
          return n
      return check_number
  default_dir_help = "Defaults to metadata_file's directory"
  subparser.add_argument("-r", "--sort-read-parallel", default=1, type=numeric_min_checker(minimum=1, message="read parallelism min for sort phase"),
                      help="total paralellism level for local read pipeline for sort phase")
  subparser.add_argument("-c", "--column-grouping", default=5, help="grouping factor for parallel chunk sort",
                      type=numeric_min_checker(minimum=1, message="column grouping min"))
  subparser.add_argument("-s", "--sort-parallel", default=1, help="number of sorting pipelines to run in parallel",
                      type=numeric_min_checker(minimum=1, message="sorting pipeline min"))
  subparser.add_argument("-w", "--write-parallel-sort", default=1, help="number of ceph writers to use in parallel",
                      type=numeric_min_checker(minimum=1, message="writing pipeline min"))
  subparser.add_argument("-x", "--write-parallel-merge", default=0, help="number of ceph writers to use in parallel",
                      type=numeric_min_checker(minimum=1, message="writing pipeline min"))
  subparser.add_argument("--sort-process-parallel", default=1, type=numeric_min_checker(minimum=1, message="parallel processing for sort stage"),
                      help="parallel processing pipelines for sorting stage")
  subparser.add_argument("-b", "--order-by", default="location", choices=["location", "metadata"], help="sort by this parameter [location | metadata]")
  subparser.add_argument("--output-name", default="sorted", help="name for the output record")
  subparser.add_argument("--chunk", default=2, type=numeric_min_checker(1, "need non-negative chunk size"), help="chunk size for final merge stage")
  subparser.add_argument("--summary", default=False, action='store_true', help="store summary information")
  subparser.add_argument("--logdir", default=".", help="Directory to write tensorflow summary data. Default is PWD")
  subparser.add_argument("--output-pool", default="", help="The Ceph cluster pool in which the output dataset should be written")
  subparser.add_argument("--ceph-read-chunk-size", default=(2**26), type=int, help="minimum size to read from ceph storage, in bytes")
  subparser.add_argument("metadata_file", help="the json metadata file describing the chunks in the original result set")
  subparser.add_argument("ceph_params", help="Parameters for Ceph Reader")

  

