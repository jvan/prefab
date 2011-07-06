import subprocess
import paramiko
import socket
from time import sleep

from ansi_color import ansi

(OK, WARNING, ERROR) = range(3)

def message(text, status=OK):
   if status == OK:
      print ansi.ok(' -- {0} --'.format(text))
   elif status == WARNING:
      print ansi.warning(' ** {0} **'.format(text))
   elif status == ERROR:
      print ansi.error(' !! {0} !!'.format(text))

def is_host_up(host, port):
   original_timeout = socket.getdefaulttimeout()
   new_timeout = 3
   socket.setdefaulttimeout(new_timeout)
   host_status = False
   try:
      transport = paramiko.Transport((host, port))
      host_status = True
   except Exception, e:
      message('Host {0} on port {1} is down'.format(host, port), ERROR)
      print e
   socket.setdefaulttimeout(original_timeout)
   return host_status

#def ping(ip):
   #return subprocess.call('ping -c 1 {0}'.format(ip), shell=True) == 0

class Port:

   def __init__(self):
      self.process =None

   def forward(self, host, vm):
      port, host, remote = vm.port, vm.ip, host.name
      message('Forwarding {0}:22 to localhost:{1}'.format(host, port))
      args = ['ssh', '-N', '-L', '{0}:{1}:22'.format(port, host), remote]
      self.process = subprocess.Popen(args)
      sleep(3)
      message('SSH process running (id={0})'.format(self.process.pid))

   def close(self):
      message('Killing SSH process (id={0})'.format(self.process.pid))
      self.process.kill()
      sleep(3)

