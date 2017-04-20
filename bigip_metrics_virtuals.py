#!/usr/bin/env python

from auzaar.auzaar_yaml import YAML as YAML
from auzaar.auzaar_os import exec_command as run
from auzaar.auzaar_os import (
    get_env,
    is_valid_address,
    get_program_name,
    epoch_seconds,
    sysargv
)
from auzaar.auzaar_f5 import BigIPCluster
from auzaar.auzaar_ssh import SSH

class BigIPMetrics(object):

    def __init__(self):
        if len(sysargv) != 2:
            self.error_exit('argument required')
        self.target_cluster = sysargv[1]
        yaml_data = YAML(get_program_name().split('.')[0] + '.yaml')
        self.yaml_dict = yaml_data.get_dict()
        self.username = get_env(self.yaml_dict.get('username', 'sje0000'))
        self.password = get_env(self.yaml_dict.get('password', 'sje0000'))
        if not self.username or not self.password:
            self.error_exit('failed to determine username and password')
        self.cluster_addr_list = (self.yaml_dict.get('clusters', {}).
                                  get(self.target_cluster, {}).
                                  get('addr_list', []))
        if len(self.cluster_addr_list) == 0:
            self.hostname = None
        elif len(self.cluster_addr_list) == 1:
            self.hostname = self.cluster_addr_list[0]
        else:
            self.active_bigip()
        if not self.hostname:
            self.error_exit('failed to determine active load balancer')
        self.vs = {}
        self.now_in_seconds = epoch_seconds()
        self.vs_list = (self.yaml_dict.get('clusters', {}).
                        get(self.target_cluster, {}).
                        get('vs_list', None))

    def active_bigip(self):
        if type(self.cluster_addr_list) is list:
            cluster_params = {
                'addr_list': self.cluster_addr_list,
                'username': self.username,
                'password': self.password
            }
            cluster = BigIPCluster(**cluster_params)
            if is_valid_address(cluster.addr_active):
                self.hostname = cluster.addr_active
            else:
                self.hostname = None
        else:
            self.hostname = None

    def dump(self):
        # metricName metricValue timestamp source pointTags
        # timestamp and pointTags not required
        # "lb.vs.vs_name" 123 addr lb="sj_int"
        for vs_name in self.vs.keys():
            vs = self.vs.get(vs_name, {})
            for k, v in vs.items():
                dump_msg = '"lb.vs.{}.{}" {} {} {} lb="{}"'.\
                    format(
                        vs_name,
                        k.replace('.', '_'),
                        v,
                        self.now_in_seconds,
                        self.hostname,
                        self.target_cluster
                    )
                if self.vs_list:
                    if vs_name in self.vs_list:
                        print(dump_msg)
                else:
                    print(dump_msg)

    def error_exit(self, msg):
        raise SystemExit(msg)

    def process(self):
        stats_list = [
            'clientside.bits-in',
            'clientside.bits-out',
            'clientside.cur-conns',
            'clientside.tot-conns',
            'tot-requests'
        ]
        self.vs = {}
        for i, line in enumerate(self.vs_show_out):
            line = str(line.strip())
            if line.startswith('}'):
                continue
            if line.startswith('ltm virtual'):
                current_vs = str(line.split()[2])
                self.vs[current_vs] = {}
            k, v = (line.split()[0], line.split()[1])
            if k in stats_list:
                self.vs[current_vs][k] = v

    def pull(self):
        ssh_params = {
            'hostname': self.hostname,
            'username': self.username,
            'password': self.password,
            'port': 22,
            'pkey': None,
            'key_filename': None,
            'timeout': 5,
            'allow_agent': False,
            'look_for_keys': False,
            'compress': False,
            'sock': None,
            'gss_auth': False,
            'gss_kex': False,
            'gss_deleg_creds': False,
            'gss_host': None,
            'banner_timeout': None
        }
        ssh = SSH(**ssh_params)
        ssh.connect()
        self.vs_show_out = ssh.exec_command('tmsh show /ltm virtual raw field-fmt')
        ssh.disconnect()

def main():
    metrics = BigIPMetrics()
    metrics.pull()
    metrics.process()
    metrics.dump()

if __name__ == '__main__':
    main()
