from fabric.api import cd
import os

from utils import message

class Project:

   #=======================================================
   # Embedded classes
   #
   #=======================================================

   class Paths:
      ''' Directory names for project.'''

      def __init__(self, project):
         ''' Constructor.

         project -- Project object.'''

         self.root    = os.path.join('~', 'Development', project.name)
         self.repo    = os.path.join(self.root, 'repo')
         self.staging = os.path.join(self.root, 'staging', project.stage)
         self.source  = os.path.join(self.staging, 'source')
         self.build   = os.path.join(self.staging, 'build')

   def __init__(self, doc, stage):
      ''' Constructor.

      doc   -- YAML config file.
      stage -- Name for staging directory.'''
      
      self.name = doc['name']
      self.repo = doc['repo']
      self.url  = doc['url']
      self.build_cmds = doc['build']
      self.fetch_list = doc['fetch']
      self.stage = stage
      self.paths = Project.Paths(self)


   def __str__(self):
      return '(project name={0}; repo={1}; url={2})'.format(self.name, self.repo, self.url)

   #=======================================================
   # Interface
   #
   #=======================================================

   def initialize(self, vm):
      ''' Initialize a project on a virtual machine.'''
      
      message('Initializing project {0} on {1}'.format(self.name, vm.name))

      # Delete the existing root directory
      # TODO: warn/prompt user before deleting existing directory?
      message('Deleting RootDir {0}'.format(self.paths.root))
      vm.run('rm -rf {0}'.format(self.paths.root))

      # Create the code repository directory
      message('Creating RepoDir {0}'.format(self.paths.repo))
      vm.run('mkdir -p {0}'.format(self.paths.repo))

      # Clone the repository
      # TODO: create Repository class which contains clone, pull, etc. logic
      message('Cloning repository {0}'.format(self.url))
      if self.repo == 'mercurial':
         vm.run('hg clone --noupdate {0} {1}'.format(self.url, self.paths.repo))
      elif self.repo == 'git':
         vm.run('git clone --mirror {0} {1}'.format(self.url, self.paths.repo))


   def pull(self, vm):
      ''' Get updates from code repository and create archive.'''

      with cd(self.paths.repo):
         self._pull(vm)
         self._archive(vm)


   def _pull(self, vm):
      message('Pulling from repo')
      if self.repo == 'mercurial':
         vm.run('hg pull')
      elif self.repo == 'git':
         vm.run('git fetch --all')


   def _archive(self, vm):
      message('Creating archive {0}'.format(self.paths.source))
      if self.repo == 'mercurial':
         vm.run('hg archive -r tip {0}'.format(self.paths.source))
      elif self.repo == 'git':
         vm.run('git clone . {0}'.format(self.paths.source)) 


   def build(self, vm):
      ''' Build a project on a virtual machine.'''

      def var_replace(string):
         return string.format(SOURCE_DIR=self.paths.source)

      with cd(self.paths.build):
         for cmd in self.build_cmds:
            cmd = var_replace(cmd)
            message('Running command: {0}'.format(cmd))
            vm.run(cmd)


   def fetch(self, vm):
      ''' Fetch files from a virtual machine.'''

      def get_files():
         files = vm.run('ls {0}'.format(' '.join(self.fetch_list[vm.type])))
         return [x.strip() for x in files.split('\n')]

      with cd(self.paths.build):
         packages = get_files()
         for pkg in packages:
            message('Fetching package => {0}'.format(pkg))
            # Copy the files from the remote machine to the local directory
            vm.get(os.path.join(self.paths.build, pkg),
                   os.path.join('local', vm.name, pkg))

