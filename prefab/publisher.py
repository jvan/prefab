from fabric.api import local

class Publisher:

   def __init__(self, doc):
      self.url = doc['url']
      self.user = doc['user']
      self.files = doc['files']

   def __str__(self):
      s = '(publisher url={}; user={})\n'.format(self.url, self.user)
      s += '  ' + '\n  '.join('(file={})'.format(x) for x in self.files)
      return s

   def get_files(self):
      files = []
      for glob in self.files:
         search = local('find ./local -name {}'.format(glob), True) 
         files.extend([x.strip() for x in search.split('\n')])
      return files
