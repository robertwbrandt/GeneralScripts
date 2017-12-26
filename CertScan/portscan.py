#!/usr/bin/env python
"""
	Python script to find and detail certian ports on a network.
	You need to run this script as root or change the setuid on the nmap binary
"""
import argparse, textwrap, datetime, json
import xml.etree.cElementTree as ElementTree
import subprocess

# Import Brandt Common Utilities
import sys, os
sys.path.append( os.path.realpath( os.path.join( os.path.dirname(__file__), "/opt/brandt/common" ) ) )
import brandt
sys.path.pop()

args = {}
args['output'] = 'text'
version = 0.3
encoding = 'utf-8'
parser = None

ports = [("ftp",21),
         ("telnet",23),
         ("HTTPS",443),
         ("Alternative HTTPS",981),
         ("Alternative HTTPS",1311),
         ("Alternative HTTPS",7000),
         ("Alternative HTTPS",8009),
         ("Alternative HTTPS",8090),
         ("Alternative HTTPS",8443)]

targets = ["192.168.1.0/24"]

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
      print "Usage: " + self.__prog + " [options]"
      print "Script to find and detail all SSL Certs on a network."
      print "This script requires root privileges or nmap must have root SUID.\n"      
      print "Options:"
      options = []
      options.append(("-h, --help",            "Show this help message and exit"))
      options.append(("-v, --version",         "Show program's version number and exit"))
      options.append(("-o, --output OUTPUT",   "Type of output {text | csv | xml | json}"))
      length = max( [ len(option[0]) for option in options ] )
      for option in options:
        description = textwrap.wrap(option[1], (self.__row - length - 5))
        print "  " + option[0].ljust(length) + "   " + description[0]
      for n in range(1,len(description)): print " " * (length + 5) + description[n]
    exit(self.__exit)
def command_line_args():
  global args, version, parser
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('-v', '--version', action=customUsageVersion, version=version, max=80)
  parser.add_argument('-h', '--help', action=customUsageVersion)
  parser.add_argument('-o', '--output',
          required=False,
          default=args['output'],
          choices=['text', 'csv', 'xml', 'json'],
          help="Display output type.")
  args.update(vars(parser.parse_args()))







#nmap --system-dns -oG - -sT -O -p 21,23,443,981,1311,7000,8009,8090,8443 192.168.1.0/24
#echo | openssl s_client -servername 10.200.150.15 -connect 10.200.200.25:443 2> /dev/null | openssl x509 -noout -dates -issuer

# Start program
if __name__ == "__main__":
  command_line_args()  


  cmd =  "nmap --system-dns -oG - -sT -A"
  cmd += " -p " + ",".join([ str(port) for name,port in ports ])
  targets = [''] + targets
  cmd += " ".join(targets)

  print "Trying to run command:", cmd

  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  if p.returncode != 0:
    print err
    sys,exit(p.returncode)

  # https://nmap.org/book/output-formats-grepable-output.html
  data = [ x.split("\t") for x in out.split("\n") if str(x[:5]).lower() == "host:" and "ports:" in str(x).lower() ]
  hosts = []
  for line in data:
    host = {"ip":"", "dns":"", "status":"", "ports":{}, "ignored state":"", "os":"", "seq index":"", "ip id seq":""}
    for entry in line:
      if str(entry[:5]).lower() == "host:":
        entry = str(entry[5:]).strip().replace("(","/").replace(")","")
        host["ip"],host["dns"] = entry.split("/")[:2]
        host["ip"] = str(host["ip"]).strip()
        host["dns"] = str(host["dns"]).strip().lower()

      if str(entry[:6]).lower() == "ports:":
        for port in str(entry[6:]).split(","):
          print port
      
      print host

