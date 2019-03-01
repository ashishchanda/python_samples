DOCUMENTATION = '''
Pre-Condition: 
Your hosting machine serves as a PXE server. 
Its PXE related services are running. 

Once you reboot your client it will start sending requests to the DHCP server to get PXE booted. 
This python file will read the logs and get the mac-address fetched from the requests.
'''


## LOGGER
import logging
logger = logging.getLogger('fetch_mac_address')
hdlr = logging.FileHandler('/var/log/chaperone/ChaperoneNFVLog1.log')
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(funcName)s: %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(10)

import time
import subprocess
import select
import paramiko
import os,glob
import atexit
import requests
import sys
import collections

def fetch_mac_address(module):
    wait_counter = 0
    timeout_to_wait = 720
    syslog_path = '/var/log/syslog'
    mac_out_path = '/home/vmware/mac-addresses/'
    mac_addresses = []    
    number_of_hosts = int(module.params['total_hosts'])
    changed = False    
    file = open(syslog_path,'r')
    for line in file:
        pass
    if not os.path.exists(mac_out_path):
            os.makedirs(mac_out_path)
    else:
        for filename in glob.glob(mac_out_path + "mac_*"):
            os.remove(filename)
    mac_out_path = mac_out_path + 'mac_address'
    while 1:
        where = file.tell()
        line = file.readline()
        if not line:
            file.seek(where)
        else:
            if " DHCPDISCOVER(eth1) " in line:
                to_add = line.split("DHCPDISCOVER(eth1) ",1)[1]
                to_add = to_add.strip(' \t\n\r')
                logger.debug("Mac Address found is : %s" % (str(to_add)))
                if to_add not in mac_addresses:
                    mac_addresses.append(to_add)
                    with open(mac_out_path , "a") as mac_file:
                        mac_file.write(to_add + '\r')
                    logger.debug("Mac Address %s collected till now are : %s" % (str(len(mac_addresses)),str(mac_addresses)))
                if len(mac_addresses) == number_of_hosts:
                    changed = True
                    break  
        if wait_counter == timeout_to_wait:               
            break
        wait_counter = wait_counter + 1
        time.sleep(5)
    if changed:
        module.exit_json(changed=changed, msg="I found " + str(len(mac_addresses)) + " hosts with mac addresses " + str(mac_addresses))
    else:
        module.fail_json(changed=changed, msg='I found ' + str(len(mac_addresses)) + ' hosts, waited for around an hour')

def main():
    argument_spec = dict(
    total_hosts=dict(required=False, type='str'),    
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    fetch_mac_address(module)
    
from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
