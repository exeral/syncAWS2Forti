

# syncAWS2Forti
sync AWS target groups to Fortigate virtualserver members

AWS lambda function to synchronize targetGroup members with a fortigate virtualserver

This script: 
- retrieve targetGroup instances
- retrieve IP from instances
- retrieve Fortigate virtualserver config from ssh cli
- compare differences
- add or remove fortigate entries through ssh cli

Plug this lambda to a Cloudwatch rule on AutoScalingGroups changes.

Tested on Python2.7

## variables:
use the following environment variables:
- **targetGroup**
the AWS arn for targetGroup
`example: arn:aws:elasticloadbalancing:eu-west-1:112233445566:targetgroup/target-group-name/00ff00ff00f`
- **fortigate_vs**
the name of the virtual server in fortigate
- **fortigate_ip**
Your firewall IP
- **fortigate_password**
cli password
- **fortigate_user**
cli username
"firewall>address" admin profile is required. do not use a superadmin account

## usage:
```
➜  ~ python2 ./syncTargets.py
/usr/lib/python2.7/dist-packages/Crypto/Cipher/blockalgo.py:141: FutureWarning: CTR mode needs counter parameter, not IV
  self._cipher = factory.new(key, *args, **kwargs)
Config in Fortigate
{'1011724198': {'ip': '10.117.24.198', 'port': '80'}, '5': {'ip': '5.5.5.5', 'port': '80'}, '1011750148': {'ip': '10.117.50.148', 'port': '80'}, '101173757': {'ip': '10.117.37.57', 'port': '80'}}
Config in ELB targetGroups
{'i-0fd1fa87406321116': {'ip': '10.117.24.198', 'port': '80'}}
fortigate $
fortigate (vip) $
fortigate (test-vs) $
fortigate (realservers) $
fortigate (realservers) $
fortigate (test-vs) $ Unknown action

fortigate (test-vs) $
entry 5 removed from fortigate virtualserver: test-vs
fortigate $
fortigate (vip) $
fortigate (test-vs) $
fortigate (realservers) $
fortigate (realservers) $
fortigate (test-vs) $ Unknown action

fortigate (test-vs) $
entry 1011750148 removed from fortigate virtualserver: test-vs
fortigate $
fortigate (vip) $
fortigate (test-vs) $
fortigate (realservers) $
fortigate (realservers) $
fortigate (test-vs) $ Unknown action

fortigate (test-vs) $
entry 101173757 removed from fortigate virtualserver: test-vs
```

## credits

Fortigate config parsing from https://www.reddit.com/r/learnpython/comments/49ml1d/parsing_a_fortigate_config/d0t5w8i?utm_source=share&utm_medium=web2x
