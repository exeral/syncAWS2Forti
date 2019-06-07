#!/usr/bin/env python2

import os
import json
import boto3
import paramiko

targetGroup = os.environ['targetGroup']
fortigate_vs = os.environ['fortigate_vs']
server = os.environ['fortigate_ip']
password = os.environ['fortigate_password']
username = os.environ['fortigate_user']

def forti_delete_server(index):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('config firewall vip\nedit '+fortigate_vs+'\nconfig realservers\ndelete '+str(index)+'\nend\nexit')
    print ssh_stdout.read()
    print("entry "+str(index)+' removed from fortigate virtualserver: '+fortigate_vs)
    ssh.close()

def forti_add_server(ip,port):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('config firewall vip\nedit '+fortigate_vs+'\nconfig realservers\nedit '+str(ip).replace('.', '')+'\nset ip '+ip+'\nset port '+port+'\nend\nexit')
    print ssh_stdout.read()
    print("server "+ip, port+' added to fortigate virtualserver: '+fortigate_vs)
    ssh.close()

def lambda_handler(event, context):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server, username=username, password=password)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('show firewall vip '+fortigate_vs)

    forticonf = ssh_stdout.read().replace("dve-billing-vpn1 $ ".encode() ,"".encode())
    config = {}
    fortiConfig = {}
    elbConfig = {}

    # parsing fortigate raw config
    for line in forticonf.splitlines():
        if line.strip():
            args   = line.split()
            action = args.pop(0)
            #action, *args = line.split()

            if action == 'config':
                header  = ' '.join(args)
                if header not in config:
                    config[header] = {}

            if action == 'edit':
                section = ' '.join(args).strip('"')
                if section not in config[header]:
                    config[header][section] = {}

            if action == 'set':
                name  = args.pop(0)
                value = ' '.join(args).strip('"')
                config[header][section][name] = value
    if 'realservers' in config:
        fortiConfig = config['realservers']
    ssh.close()

    elbv2 = boto3.client('elbv2')
    targets = elbv2.describe_target_health(TargetGroupArn=targetGroup).get('TargetHealthDescriptions')
    for target in targets:
        instanceId = target['Target']['Id']
        port = target['Target']['Port']
        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(instanceId)
        ip = instance.private_ip_address
        elbConfig[instanceId] = {'ip': ip, 'port': str(port)}

    print("Config in Fortigate")
    print fortiConfig
    print("Config in ELB targetGroups")
    print elbConfig
    for key, value in elbConfig.iteritems():
        if value not in fortiConfig.values():
            #add the value to forti
            forti_add_server(value['ip'],value['port'])
    for key, value in fortiConfig.iteritems():
        if value not in elbConfig.values():
            #remove the value from forti
            forti_delete_server(key)


lambda_handler(None,None)
