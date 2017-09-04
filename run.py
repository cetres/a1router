# -*- coding: UTF-8 -*-
import logging
import argparse
from a1router import Dlink

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Read a router for informations')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug information')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    d = Dlink(log_level=log_level)
    print(d.get_wan_address())
    print(d.get_wifi_assoc())


