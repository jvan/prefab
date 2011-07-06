#!/usr/bin/env python
#
# NAME: fab-build
#
# USAGE: fab-build OPTIONS [PROJECT CONFIG]
#
# DESCRIPTION:
#    Build a project on a network of virtual machines.
#

from prefab.host import Host
from prefab.project import Project
from prefab.parser import Parser
from prefab.ansi_color import ansi
from prefab.utils import message, WARNING, ERROR

import yaml
import os

from datetime import datetime


#==========================================================
# Utility functions
#
#==========================================================

def find_config_files(path):
   ''' Return a list of all YAML files the given directory.'''
   return [x for x in os.listdir(path) if x.endswith('.yaml')]


def print_config_dir(root_dir, title):
   ''' Pretty print the names (minus extension) of all config files
   in a given directory.'''
   HIGHLIGHT = ansi(ansi.cyan)
   print '=' * 10 + ' ' + title + ' ' + '=' * (48-len(title))
   print ' * ' + '\n * '.join(map(lambda x: HIGHLIGHT(x.split('.')[0]), find_config_files(root_dir)))
   print '=' * 60


class ConfigFileMissing:
   def __init__(self, config_file):
      self.filename = config_file


def get_config_file(root_dir, config_name):
   ''' Return the path to a config file.

   Search the given directory for a config file. The file extension
   (.yaml) is optional. Thus, if the file setup.yaml exists in the 
   directory either 'setup' or 'setup.yaml' could be used.
   
   If the file does not exist a ConfigFileMissing exception will
   be raised.

   root_dir    -- Directory to search.
   config_name -- Config file name (extension optional). '''

   config = os.path.join(root_dir, config_name)
   if not config.endswith('.yaml'):
      config += '.yaml'
   if not os.path.exists(config):
      raise ConfigFileMissing(config)
   return config


def config_list(base_dir, configs=None):
   ''' Return a list of config files in a given directory.
   
   Find config files and return a list of path names. The
   option argument 'configs' is a list containing config 
   names (extension optional). If this argument is missing
   then all config (YAML) files in the directory will be 
   returned.

   base_dir -- Directory to search.
   configs  -- List of config file names. (Optional)'''

   if configs:
      return [get_config_file(base_dir, config)
               for config in configs]

   return [get_config_file(base_dir, config)
               for config in find_config_files(base_dir)]


def builder_list(args):
   ''' Return a list of builder config paths.'''
   builder_dir = os.path.join(args.config_dir, 'builders')
   return config_list(builder_dir, args.builders)

def publisher_list(args):
   ''' Return a list of publisher config paths.'''
   publish_dir = os.path.join(args.config_dir, 'publishers')
   return config_list(publish_dir, args.publishers)

def project_list(args):
   project_dir = os.path.join(args.config_dir, 'projects')
   if args.build_all:
      return config_list(project_dir)
   return [get_config_file(project_dir, args.project_config)]

def import_builders(builders, builder_dir):
   message('IMPORTING BUILDERS')
   for config in builders:
      try:
         doc = yaml.load(open(config))
         for include in doc['include']:
            search = get_config_file(builder_dir, include)
            if search in builders:
               message('builder config ({}) already imported'.format(include), WARNING)
            else:
               message('importing builder config ({})'.format(include))
               builders.append(search)
         builders.remove(config)
      except KeyError:
         pass
   
   return builders

def merge_builders(builders):
   hosts = { }
   for config in builders:
      doc = yaml.load(open(config)) 
      builder = Host(doc)
      key = builder.user + builder.name
      if key not in hosts:
         hosts.setdefault(key, builder)
      else:
         message('MERGING BUILDER {}'.format(config), WARNING)
         hosts[key].vms.extend(builder.vms)

   return hosts.values()

def sanity_check(builders):
   ports = { } 
   ips = { }
   for builder in builders:
      for vm in builder.vms:
         if vm.port in ports:
            message('ERROR: port {} assigned to multiple machines'.format(vm.port), ERROR)
         else:
            ports.setdefault(vm.port, None)

         if vm.ip in ips:
            message('ERROR: ip {} assigned to multiple machines'.format(vm.ip), ERROR)
         else:
            ips.setdefault(vm.ip, None)

def print_config_files(configs, label):
   print '{} [{}]'.format(label, len(configs))
   for config in configs:
      print ' -- {}'.format(config)


#==========================================================
# Main Program
#
#==========================================================

def main():
   import sys

   parser = Parser()
   args = parser.parse_args()

   builder_dir = os.path.join(args.config_dir, 'builders')
   project_dir = os.path.join(args.config_dir, 'projects')
   publish_dir = os.path.join(args.config_dir, 'publishers')

   if args.list_all_builders:
      print_config_dir(builder_dir, 'BUILDERS')
      sys.exit(0)

   if args.list_all_projects:
      print_config_dir(project_dir, 'PROJECTS')
      sys.exit(0)

   if args.list_all_publishers:
      print_config_dir(publish_dir, 'PUBLISHERS')
      sys.exit(0)

   if not args.project_config:
      parser.print_usage()
      sys.exit(1)

   try:
      builders   = builder_list(args)
      publishers = publisher_list(args)
      projects   = project_list(args)
   except ConfigFileMissing, err:
      print 'ERROR: config file ({}) does not exist'.format(err.filename)
      sys.exit(1)
   except IndexError:
      print 'ERROR: no project name/config specified'
      sys.exit(1)

   builders = import_builders(builders, builder_dir)
   
   print_config_files(builders, 'BUILDERS')
   print_config_files(publishers, 'PUBLISHERS')
   print_config_files(projects, 'PROJECTS')

   builders = merge_builders(builders)
   sanity_check(builders)

   stage=datetime.now().strftime("%Y%m%d_%H%M%S")
   #stage = '123456789'

   projects = [Project(yaml.load(open(config)), stage) for config in projects]

   for builder in builders:
      
      if args.dry_run:
         print builder
   
      for project in projects:

         if args.dry_run:
            print project
   
         if args.init_project:
            if not args.dry_run:
               builder.init(project)
            else:
               print ' !! initializng project !!'
         else:
            if not args.dry_run:
               builder.build_and_fetch(project, stage)
            else:
               print ' !! building project !!'


if __name__ == '__main__':
   main()



