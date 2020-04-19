import sys
import argparse

from HW25P import HW25P


parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mac', default="C9:65:1E:2B:6B:CC", help='Mac address of the device')
args = parser.parse_args()

MAC = args.mac

band = HW25P(MAC, debug=True)
band.device_info()
band.battery_data()
band.heart_rate_data()

band.disconnect()
band._log.info("Band is disconnected")
sys.exit(0)
