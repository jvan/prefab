#!/usr/bin/env python
#
# USAGE: fab-run [builder] [script]
#

from prefab.host import Host

import yaml
import sys

class Script:
   def __init__(self, filename):
      doc = yaml.load(open(filename))
      self.machines = { } 
      for m_type, cmds in doc.items():
         self.machines.setdefault(m_type, cmds)

def main():
   builder_config = sys.argv[1]
   script_file = sys.argv[2]

   doc = yaml.load(open(builder_config))
   builder = Host(doc)
   print builder

   script = Script(script_file)
   
   builder.run_script(script)
   
if __name__ == '__main__':
   main()
