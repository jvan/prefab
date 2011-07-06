from fabric.api import run, get, cd, settings, hide
from time import sleep

from utils import message, OK, WARNING, ERROR

class VM:
   ''' Virtual machine.'''

   def __init__(self, doc, host):
      ''' Constructor.

      doc  -- YAML configuration document.
      host -- Host object.''' 

      self.name = doc['name']
      self.type = doc['type']
      self.user = doc['user']
      self.port = doc['port']
      self.ip   = doc['ip']
      self.host = host


   def __str__(self):
      return '(vm name={0}; user={1}; port={2}; ip={3})'.format(self.name, self.user, self.port, self.ip)


   #=======================================================
   # Interface
   #
   #=======================================================

   def is_running(self):
      ''' Returns True if the virtual machines is currently running.'''

      with settings(hide('running', 'stdout'),
                     host_string=self.host):
         output = run('virsh list', shell=False, pty=False)
      return self.name in output


   def start(self):
      ''' Boot the virtual machine.'''

      if self.is_running():
         message('Virtual machine ({0}) is already running'.format(self.name), WARNING)
         return

      message('Starting virtual machine ({0})'.format(self.name))
      with settings(host_string=self.host):
         run('virsh start {0}'.format(self.name), shell=False, pty=False)
       
         # TODO: better method to ensure that machine has booted 
         sleep(15)


   def shutdown(self):
      ''' Shut down the virtual machine.'''

      if not self.is_running():
         message('Virtual machine ({0}) is not currently running !!'.format(self.name), WARNING)
         return
   
      message('Stopping virtual machine ({0})'.format(self.name))
      with settings(host_string=self.host):
         run('virsh shutdown {0}'.format(self.name), shell=False, pty=False)
         while self.is_running():
            sleep(5)


   def run(self, cmd):
      ''' Run a command on the virtual machine through forwarded port.
      
      cmd -- Command to be executed (str).'''

      with settings(host_string='{0}@localhost:{1}'.format(self.user, self.port)):
         return run(cmd, shell=False, pty=False)


   def get(self, source, target):
      ''' Copy a file from the virtual machine through forwarded port.
      
      source -- File on virtual machine.
      target -- Destination on local machine.'''

      with settings(host_string='{0}@localhost:{1}'.format(self.user, self.port)):
         get(source, target)
