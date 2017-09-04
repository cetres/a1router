# -*- coding: UTF-8 -*-
import os
import datetime
import subprocess
import socket
import logging
import yaml
import requests
from bs4 import BeautifulSoup


CONFIG_FILE = "~/.a1router"
STATUS_FILE = "/var/run/a1router/rstatus.yaml"


class Router(object):
    _logger = None
    _config = { "ip_address": None,
                "username": None,
                "password": None}
    _mq = None
    
    def __init__(self, ip_address=None, username=None, password=None, log_level=logging.INFO):
        global CONFIG_FILE
        config_file = os.path.expanduser(CONFIG_FILE)
        self._logger = logging.getLogger('a1router')
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        self._logger.addHandler(sh)
        self._logger.setLevel(log_level)
        if os.path.exists(config_file):
            self._logger.info("Config file found. Reading...")
            with open(config_file, 'r') as stream:
                try:
                    config = yaml.load(stream)
                    self._config.update(config)
                except yaml.YAMLError as exc:
                    logging.critical(exc)
        else:
            self._logger.warn("Config file not found: {}".format(CONFIG_FILE))
        if ip_address:
            self._config["ip_address"] = ip_address
        if username:
            self._config["username"] = username
        if password:
            self._config["password"] = password
        if not self._ip_address:
            self._logger.critical("No IP address informed")
            raise RuntimeError("No IP address informed")
        if self._ping(self._ip_address):
            self._logger.info("Router is alive - {}".format(self._ip_address))
        else:
            self._logger.critical("Router is dead - {}".format(self._ip_address))
            raise RuntimeError("Router is dead - {}".format(self._ip_address))
        if self._config["assoc_event"].get("type"):
            module_name="mq_%s" % self._config["assoc_event"]["type"]
            self._logger.debug("Importing module %s" % module_name)
            mq = __import__("a1router." + module_name, fromlist=[''])
            print(mq)
            self._mq = mq.MQ(self._config["assoc_event"])
            
        
    def _ping(self, ip_address):
        self._logger.debug("Start ping to {}".format(ip_address))
        rep = subprocess.Popen(["ping", "-c1", ip_address], stdout=subprocess.DEVNULL)
        rep.communicate()
        return True if rep.returncode == 0 else False
    
    
    @property
    def _ip_address(self):
        return self._config["ip_address"]
    
    @property
    def _auth(self):
        return (self._config["username"], self._config["password"])


    def assoc_event(self, status):
        now = datetime.datetime.now().strftime("%s")
        for s,v in status.items():
            status[s]["last_time"] = now
        status_file = self._config["assoc_event"].get("status", STATUS_FILE)
        if os.path.exists(status_file):
            self._logger.info("Status file found. Reading...")
            with open(status_file, 'r') as stream:
                try:
                    status_antigo = yaml.load(stream)
                    status_antigo.update(status)
                    status = status_antigo
                except yaml.YAMLError as exc:
                    logging.critical(exc)
                    raise RuntimeError("Error while reading status file {}".format(status_file))
        with open(status_file, 'w') as stream:
            yaml.dump(status, stream, default_flow_style=False)
                
        


class Dlink(Router):
    
    def get_wan_address(self):
        url = 'http://%s/Status/wan_connection_status.asp' % self._ip_address
        r = requests.get(url, auth=self._auth)
        soup = BeautifulSoup(r.text, 'lxml-xml')
        wan_ip_address = soup.find("wan_ip_address").text
        self._logger.debug("WAN address: {}".format(wan_ip_address))
        return wan_ip_address

    def get_wifi_assoc(self):
        url = 'http://%s/Status/wifi_assoc.asp' % self._ip_address
        r = requests.get(url, auth=self._auth)
        #logging.debug(r.text)
        soup = BeautifulSoup(r.text, "lxml-xml")
        assoc = {}
        for a in soup.find_all("assoc"):
            assoc[a.find("mac").text] = { "channel": a.find("channel").text,
                                        "rate": a.find("rate").text,
                                        "quality": a.find("quality").text,
                                        "type": a.find("type").text,
                                        "ip_address": a.find("ip_address").text
                                      }
        self._logger.debug("Assoc found: {}".format(len(assoc)))
        if self._config.get("assoc_event"):
            self.assoc_event(assoc)
        return assoc
