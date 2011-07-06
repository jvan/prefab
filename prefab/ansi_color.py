#!/usr/bin/env python

class ansi:
   (black, red, green, yellow, blue, magenta, cyan, grey) = range(30, 38)
   reset = '\033[0m'

   @staticmethod
   def code(fg, bg):
      return '\033[{0};{1}m'.format(bg+10, fg)

   @staticmethod
   def wrap(text, fg=0, bg=0):
      return('{0}{1}{2}'.format(ansi.code(fg, bg), text, ansi.reset))

   @staticmethod
   def ok(text):
      return ansi.wrap(text, ansi.green)

   @staticmethod
   def warning(text):
      return ansi.wrap(text, ansi.yellow)

   @staticmethod
   def error(text):
      return ansi.wrap(text, ansi.red)
   
   def __init__(self, fg, bg=0):
      self.fg = fg
      self.bg = bg

   def __call__(self, text):
      return ansi.wrap(text, self.fg, self.bg)

if __name__ == '__main__':
   print ansi.ok('OK')
   print ansi.warning('WARNING')
   print ansi.error('ERROR')

   blue = ansi(ansi.blue)
   print blue('FOO')

   print ansi(ansi.magenta, ansi.grey)('BAR')

