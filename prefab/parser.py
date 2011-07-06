# Command-line Parser

from argparse import ArgumentParser, Action

class Parser(ArgumentParser):

   class ListAction(Action):
      def __call__(self, parser, namespace, values, option, string=None):
         setattr(namespace, self.dest, values.split(','))

   def __init__(self):
      ArgumentParser.__init__(self)

      usage = 'usage: %(prog)s [options] PROJECT'
      parser = ArgumentParser(usage=usage)

      self.add_argument('-b', '--builders', type=str, action=Parser.ListAction,
            help='list (comma separated) of builder config files')
      
      self.add_argument('-p', '--publishers', type=str, action=Parser.ListAction,
            help='list (comma seperated) of publisher config files.')

      self.add_argument('--config-dir', dest='config_dir', type=str, default='./share',
            help='specify root directory where config files are located.')

      #self.add_argument('--builder-config-dir', dest='builder_dir', type=str, default='builders',
            #help='specify directory where builder config files are located')

      #self.add_argument('--project-config-dir', dest='project_dir', type=str, default='projects',
            #help='specify directory where project config files are located')

      #self.add_argument('--publisher-config-dir', dest='publisher_dir', type=str, default='publishers',
            #help='specify directory where publisher config files are located')

      self.add_argument('--list-all-builders', action='store_true', dest='list_all_builders', default=False,
            help='print a list of all builders')

      self.add_argument('--list-all-projects', action='store_true', dest='list_all_projects', default=False,
            help='print a list of all projects')

      self.add_argument('--list-all-publishers', action='store_true', dest='list_all_publishers', default=False,
            help='print a list of all publishers')

      self.add_argument('--dry-run', action='store_true', dest='dry_run', default=False)

      group = self.add_argument_group('Advanced Options')

      group.add_argument('--all-projects', action='store_true', dest='build_all', default=False,
            help='build all projects')

      group.add_argument('--init-project', action='store_true', dest='init_project', default=False,
            help='initialize a project')


      self.add_argument('project_config', nargs='?')

