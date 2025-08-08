# SmartInfra

[English](README.md) | [简体中文](README-zh.md)

SmartInfra is a comprehensive cloud platform that includes a series of functions such as computing and storage, database management, white-box switch management, and automated changes. Specifically, it includes the following:
1. SmartInfra can provide resource allocation and tool management for computing, storage, load balancing, and CICD at the IaaS and PaaS layers.

2. **As the intelligent brain of our self-developed network switches and network solutions, the SmartInfra platform can achieve automatic initialization, automated configuration, and automated operation and maintenance of the entire underlying network, greatly reducing the burden on IT leaders and engineer. At the same time, we have pioneered the cooperation mode of leasing equipment and using the service quality output to users as an indicator. We truly put the customer first, believing that good user experience is the real measure of success. The entire solution also includes supporting services such as DNS and network disks, aiming to provide the ultimate service to customers.**

3. The SmartInfra platform also has the unified operation and maintenance function for the entire Infra layer, including CMDB for the system and network, automated changes, batch configuration, etc.

Currently, the module which will be open is a part of SmartInfra, a system for automated task configuration and execution based on **SaltStack&Ansible**. This platform supports change configurations in a standardized and process-oriented manner. It will be available on all standard operating systems.

The architecture is shown:

<img width="978" alt="image" src="salt/static/img/arch.png">

Features
------------------------
1. Host Management: It displays the information of the managed host nodes. These nodes information will be refreshed and recorded into the database. The refresh interval Support customization, and the default value is 60 minutes. At the same time, you can manage these nodes through some options(delete/accept/reject).

2. System Management: The system designs a virtual role - resource-group, which clearly builds a relationship among users, resource groups, and Salt/Ansible resources. This enables a good balance between operational convenience and strict permission control.

3. The authentication method supports three types, such as internal, LDAP, and OAuth, which allows users to conveniently choose the mode that they favorite.

4. Host-Group: When creating host-groups, three modes are supported, including selecting all hosts once, selecting single host multiple times, and selecting hosts at once by uploading a file.

5. Task Execution: It supports four types, including shell, state, playbook, and transferring files. Meanwhile, in terms of execution methods, it supports both scheduled execution and immediate execution. The system supports read-only policy function, when rules are matched, it will be executed without approval, which improves both efficiency and stability.

6. Audit function fully meets the security and compliance requirements within the enterprise.

Get Started
------------------------
### Have a try
http://119.13.95.124

| user | password |
| --- | --- |
| admin | admin |

### Docker Installation
- [install Docker](https://download.docker.com/linux/debian/dists/bookworm/pool/stable/amd64/) 

### Deploying
download [docker](docker) directory，and change into the "docker" directory

```bash
# start SmartInfra
docker-compose -f docker-compose.yml up -d

# exit
exit
```
Yes, it is ready for you now!

## Access the site
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
- Bug fixes
- Submission of new features
- Code optimization
- Improvement of test cases
