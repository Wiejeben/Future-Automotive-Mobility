from function.realtime import Realtime
from argparse import ArgumentParser
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

ap = ArgumentParser()

ap.add_argument("-d", "--display", type=int, default=0,
                help="Whether or not frames should be displayed")

ap.add_argument("-I", "--input-device", type=int, default=0,
                help="Device number input")

ap.add_argument('-w', '--num-workers', dest='num_workers', type=int,
                default=2, help='Number of workers.')

ap.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
                default=5, help='Size of the queue.')

ap.add_argument('-l', '--logger-debug', dest='logger_debug',
                type=int, default=0, help='Print logger debug')

args = vars(ap.parse_args())

Realtime(args).start()
