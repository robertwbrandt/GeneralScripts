#!/usr/bin/env python
"""
Python script to find and detail all OPW SSL Certs on a network.
notes: You may need to install python-netaddr
       You need to run this script as root or change the setuid on the nmap binary
"""
import argparse, textwrap, fnmatch, datetime
import xml.etree.cElementTree as ElementTree
import subprocess

# Import Brandt Common Utilities
import sys, os
sys.path.append( os.path.realpath( os.path.join( os.path.dirname(__file__), "/opt/brandt/common" ) ) )
import brandt
sys.path.pop()

args = {}
args['cache'] = 144000
args['emails'] = []
args['ipaddresses'] = ['192.168.201.0/24','10.200.199.0/24','10.200.200.0/24','10.201.199.0/24','10.201.200.0/24']
#args['ipaddresses'] = ['10.200.200.10/30']

version = 0.3
encoding = 'utf-8'

class customUsageVersion(argparse.Action):
  def __init__(self, option_strings, dest, **kwargs):
    self.__version = str(kwargs.get('version', ''))
    self.__prog = str(kwargs.get('prog', os.path.basename(__file__)))
    self.__row = min(int(kwargs.get('max', 80)), brandt.getTerminalSize()[0])
    self.__exit = int(kwargs.get('exit', 0))
    super(customUsageVersion, self).__init__(option_strings, dest, nargs=0)
  def __call__(self, parser, namespace, values, option_string=None):
    # print('%r %r %r' % (namespace, values, option_string))
    if self.__version:
      print self.__prog + " " + self.__version
      print "Copyright (C) 2013 Free Software Foundation, Inc."
      print "License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>."
      version  = "This program is free software: you can redistribute it and/or modify "
      version += "it under the terms of the GNU General Public License as published by "
      version += "the Free Software Foundation, either version 3 of the License, or "
      version += "(at your option) any later version."
      print textwrap.fill(version, self.__row)
      version  = "This program is distributed in the hope that it will be useful, "
      version += "but WITHOUT ANY WARRANTY; without even the implied warranty of "
      version += "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
      version += "GNU General Public License for more details."
      print textwrap.fill(version, self.__row)
      print "\nWritten by Bob Brandt <projects@brandt.ie>."
    else:
      print "Usage: " + self.__prog + " [options] email ..."
      print "Script used to find details about Zarafa users.\n"
      print "Options:"
      options = []
      options.append(("-h, --help",           "Show this help message and exit"))
      options.append(("-v, --version",        "Show program's version number and exit"))
      options.append(("-c, --cache MINUTES",  "Cache time. (in minutes)"))
      options.append(("email",                "Email Addressed to send results to."))
      length = max( [ len(option[0]) for option in options ] )
      for option in options:
        description = textwrap.wrap(option[1], (self.__row - length - 5))
        print "  " + option[0].ljust(length) + "   " + description[0]
      for n in range(1,len(description)): print " " * (length + 5) + description[n]
    exit(self.__exit)
def command_line_args():
  global args, version
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('-v', '--version', action=customUsageVersion, version=version, max=80)
  parser.add_argument('-h', '--help', action=customUsageVersion)
  parser.add_argument('-c', '--cache',
          required=False,
          default=args['cache'],
          type=int,
          help="Cache time. (in minutes)")
  parser.add_argument('emails',
          nargs='+',
          default= args['emails'],
          action='store',
          help="Email Addressed to send results to.")
  args.update(vars(parser.parse_args()))

def get_data():
  global args
  command = '/opt/brandt/GeneralScripts/CertScan/CertScan.py -o xml '
  command += " ".join(args['ipaddresses'])
  cachefile = '/tmp/OPWCertScan.cache'    

  args['cache'] *= 60
  age = args['cache'] + 1
  try:
    age = (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.stat(cachefile).st_mtime)).seconds
  except:
    pass

  if age > args['cache']:
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err: raise IOError(err)

    f = open(cachefile, 'w')
    f.write(out)
    f.close()
  else:
    f = open(cachefile, 'r')
    out = f.read()
    f.close()
  return out

# Start program
if __name__ == "__main__":
	command_line_args()  
	xml = ElementTree.fromstring(get_data())
	print '<?xml version="1.0" encoding="' + encoding + '"?>\n' + ElementTree.tostring(xml, encoding=encoding, method="xml")
