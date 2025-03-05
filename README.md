# SmartInfra

[English](README.md) | [简体中文](README-zh.md)

SmartInfra is a comprehensive cloud platform that includes a series of functions such as computing and storage, database management, white-box switch management, and automated changes. Specifically, it includes the following:
1. SmartInfra can provide resource allocation and tool management for computing, storage, load balancing, and CICD at the IaaS and PaaS layers.

2. **As the intelligent brain of our self-developed hardware network switches and network solutions, the SmartInfra platform can achieve automatic initialization, automated configuration, and automated operation and maintenance of the entire underlying network, greatly reducing the burden on IT leaders and engineer. At the same time, we have pioneered the cooperation mode of leasing equipment and using the service quality output to users as an indicator. We truly put the customer first, believing that good user experience is the real measure of success. The entire solution also includes supporting services such as DNS and network disks, aiming to provide the ultimate service to customers.**

3. The SmartInfra platform also has the unified operation and maintenance function for the entire Infra layer, including CMDB for the system and network, automated changes, batch configuration, etc.

Currently, the open-source **SmartSalt** is a part of SmartInfra, a system for automated task configuration and execution based on SaltStack. This platform can execute change configurations in a standardized and process-oriented manner, supporting operations such as commands, state playbooks, and transferring file to be executed either periodically or immediately in an asynchronous manner. The execution targets are applicable to the operation and maintenance and batch operation scenarios of all open operating systems.

The architecture is shown:

<img width="978" alt="image" src="salt/static/img/arch.png">

Features
------------------------
1. Host Management: It displays in detail the information of the managed host nodes. It provides two methods, scheduled and manual, to refresh the node information and record it into the database. The refresh interval can be customized, with the default being 60 minutes. At the same time, it provides operation functions (delete/accept/reject) to manage the nodes.

2. System Management: The system designs a virtual role - resource-group, which clearly establishes a many - to - many association among users, resource groups, and Salt resources. This enables a good balance between operational convenience and strict permission control.

3. The authentication method supports three modes, internal system authentication, LDAP authentication, and OAuth authentication, which allows users to conveniently choose the mode that suits them.

4. Host-Group: When creating host-groups, three modes are supported, including selecting all hosts once, selecting single hosts multiple times, and selecting hosts at once by uploading a file.

5. Task Execution: It supports three execution modes, command execution, state playbook execution, and file distribution. Meanwhile, in terms of execution methods, it supports both scheduled execution and immediate execution. The system has read-only policy function, Through rule matching, only query commands can be executed without approval, which improves both efficiency and stability.

6. Audit log recording fully meets the security and compliance requirements within the enterprise.

Get Started
------------------------
### Have a try
https://github.com/Dinosaur-Park/heyelb/wiki/Parasaus-Installation-Guide
| user | password |
| --- | --- |
| admin | admin |

### Docker Installation
- [install Docker](https://download.docker.com/linux/debian/dists/bookworm/pool/stable/amd64/) 

### Deploying
download [docker](docker · smartinfra/smartsalt)，and open "docker" directory

```bash
# start SmartSalt
docker-compose -f docker-compose.yml up -d

# initialize the database
create table...

# create a superuser
python3 manage.py createsuperuser

# exit
exit
```

## access the site
http://127.0.0.1


Dependency list
===============
- [Django](https://github.com/django/django)
- [Bootstrap](https://github.com/twbs/bootstrap)
- [jQuery](https://github.com/jquery/jquery)
- [sb-admin-2](https://github.com/BlackrockDigital/startbootstrap-sb-admin-2)
- [ace](https://github.com/ajaxorg/ace)
- [django-q2](https://github.com/django-q2/django-q2)
- [mysqlclient-python](https://github.com/PyMySQL/mysqlclient-python)
- [django-auth-ldap](https://github.com/django-auth-ldap/django-auth-ldap)
- [django-mirage-field](https://github.com/luojilab/django-mirage-field)


Contribution
===============
Reply and claim the relevant tasks in the corresponding issues, or directly submit a Pull Request (PR). Thank you for your contributions to SmartInfra.

Contributions include but are not limited to the following ways:
Bug fixes
Submission of new features
Code optimization
Improvement of test cases
