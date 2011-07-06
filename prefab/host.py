from fabric.api import settings, run

from vm import VM
from utils import Port, message

class Host:
   ''' Virtual machine host.

   A host machine contains one or more virtual machines. It is defined by a 
   user name and a url.
   
   
   Host machines are configured in YAML documents.'''

   def __init__(self, doc):
      ''' Constructor.

      doc -- YAML config file.'''

      self.name = doc['url']
      self.user = doc['user']

      self.vms = []
      
      for machine in doc['machines']:
         self.add_vm(VM(machine, self.name))


   def __str__(self):
      s = '(host name={0}; user={1})\n'.format(self.name, self.user)
      s += '\t' + '\n\t'.join('%s' % vm for vm in self.vms)
      return s

   #=======================================================
   # Interface
   #
   #=======================================================

   def add_vm(self, vm):
      ''' Add a virtual machine to the host system.'''
      self.vms.append(vm)


   def init(self, project):
      ''' Initialize a project.'''

      for vm in self.vms:
         # Forward port and start virtual machine
         port = Port()
         port.forward(self, vm)
         vm.start()

         # Initialize the project
         project.initialize(vm)

         # Shut down the virtual machine and close port
         vm.shutdown()
         port.close()


   def build_and_fetch(self, project, stage):
      ''' Build a project and fetch the resulting programs, packages, etc.'''

      for vm in self.vms:
         # Forward port and start virtual machine
         port = Port()
         port.forward(self, vm)
         vm.start()

         # Get updates from code repository
         project.pull(vm)

         # Create build directory
         message('Creating build directory {0}'.format(project.paths.build))
         vm.run('mkdir {0}'.format(project.paths.build)) 

         # Build project and fetch packages
         project.build(vm)
         project.fetch(vm)

         # Shut down the virtual machine and close port
         vm.shutdown()
         port.close()


   def run_script(self, script):
      ''' Execute commands on virtual machines.''' 

      for vm in self.vms:
         # Forward port and start virtual machine
         port = Port()
         port.forward(self, vm)
         vm.start()

         vm_type = vm.type
         cmds = script.machines[vm_type]
         message('Running script on {0} (type={1})'.format(vm.name, vm_type))
         for cmd in cmds:
            message('cmd={0}'.format(cmd), 1)
            with settings(host_string='{0}@localhost:{1}'.format(vm.user, vm.port)):
               run(cmd)

         # Shut down the virtual machine and close port
         vm.shutdown()
         port.close()

