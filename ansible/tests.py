from django.test import TestCase

# Create your tests here.

xx = ("10.0.85.139 ansible_port=22"
      "1.1.1.1")
print(len(xx.split()))
pb_hosts_dir ='/tmp/'
an_port =22
an_user = 'root'
with open(pb_hosts_dir + 'hosts', "w") as phdh:
    phdh.write("[all]\n")
    for each_host in xx.splitlines():
        if len(each_host.split()) == 1:
            each_host = each_host + " ansible_port=%d ansible_user=%s" % (an_port, an_user)
        phdh.write(each_host+"\n")