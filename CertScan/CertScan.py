#!/usr/bin/env python
"""
Python script to find and detail all SSL Certs on a network.
notes: You may need to install python-netaddr
       You need to run this script as root or change the setuid on the nmap binary
"""
import argparse, textwrap, datetime, json
import xml.etree.cElementTree as ElementTree
import subprocess
import ssl, OpenSSL, socket, netaddr

# Import Brandt Common Utilities
import sys, os
sys.path.append( os.path.realpath( os.path.join( os.path.dirname(__file__), "/opt/brandt/common" ) ) )
import brandt
sys.path.pop()

args = {}
args['output'] = 'text'
args['target'] = []
args['delimiter'] = ""
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
      print "Usage: " + self.__prog + " [options] targets"
      print "Script to find and detail all SSL Certs on a network.\n"
      print "Options:"
      options = []
      options.append(("-h, --help",            "Show this help message and exit"))
      options.append(("-v, --version",         "Show program's version number and exit"))
      options.append(("-o, --output OUTPUT",   "Type of output {text | csv | xml | json}"))
      options.append(("-d, --delimiter DELIM", "Character to use instead of TAB for field delimiter"))      
      options.append(("targets",               "Target Specifications."))
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
  parser.add_argument('-d', '--delimiter',
          required=False,
          default=args['delimiter'],
          type=str,
          help="Character to use instead of TAB for field delimiter")
  parser.add_argument('-o', '--output',
          required=False,
          default=args['output'],
          choices=['text', 'csv', 'xml', 'json'],
          help="Display output type.")
  parser.add_argument('target',
          nargs='+',
          default= args['target'],
          action='store',
          help="Target Specifications.")
  args.update(vars(parser.parse_args()))
  if args['delimiter']: args['delimiter'] = args['delimiter'][0]
  if not args['delimiter'] and args['output'] == "csv": args['delimiter'] = ","


def get_data():
  global args

  socket.setdefaulttimeout(5)
  certs = []
  for ip in netaddr.IPSet(args['target']):
    ip = str(ip)
    command = 'ping -c 1 "' + ip + '" > /dev/null'  
    command += ' && nmap --privileged --version-light --allports -sV -oX - "' + ip + '"'
    command += ' | xsltproc GeneralScripts/CertScan/certscan.xslt -'

    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if not  p.returncode:
      out = out.strip()
      for line in out.split():
        ip,port = line.split(":")
        try:
          cert = ssl.get_server_certificate((ip,int(port)), ssl_version=ssl.PROTOCOL_SSLv23)
          x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
          subject = ",".join([ "=".join(x) for x in x509.get_subject().get_components() ])
          issuer = ",".join([ "=".join(x) for x in x509.get_issuer().get_components() ])
          notbefore = x509.get_notBefore()
          notafter = x509.get_notAfter()
          expired = str(bool(x509.has_expired()))
        except:
          subject = "Port Error"
          issuer = ""
          notbefore = ""
          notafter = ""
          expired = ""
        certs.append({"address":ip,
                      "port":port,
                      "subject": subject,
                      "issuer": issuer,
                      "notbefore": notbefore,
                      "notafter": notafter,
                      "expired": expired})          
    else:
      certs.append({"address":ip,
                    "port":"",
                    "subject": "IP Error",
                    "issuer": "",
                    "notbefore": "",
                    "notafter": "",
                    "expired": ""})

  return certs


# Start program
if __name__ == "__main__":
  try:
    output = ""
    error = ""
    xmldata = ""
    exitcode = 0
 
    command_line_args()  
    certs = get_data()

  except SystemExit as err:
    pass
  except Exception as err:
    try:
      exitcode = int(err[0])
      errmsg = str(" ".join(err[1:]))
    except:
      exitcode = -1
      errmsg = str(err)

    if args['output'] != 'xml': 
      error = "(" + str(exitcode) + ") " + str(errmsg) + "\nCommand: " + " ".join(sys.argv)
    else:
      xmldata = ElementTree.Element('error', code=brandt.strXML(exitcode), 
                                             msg=brandt.strXML(errmsg), 
                                             cmd=brandt.strXML(" ".join(sys.argv)))
  finally:
    if args['output'] == 'xml':
      xml = ElementTree.Element('certscan')
      if xmldata: xml.append(xmldata)
      for cert in certs:
        xmluser = ElementTree.SubElement(xml, "certificate", **cert)
      print '<?xml version="1.0" encoding="' + encoding + '"?>\n' + ElementTree.tostring(xml, encoding=encoding, method="xml")

    else:
      if error:
        sys.stderr.write( str(error) + "\n" )

      elif args['output'] == 'text':
        print "IP Address", "port", "Subject", "Issuer", "Not Before", "Not After", "Expired"
        for cert in certs:
          print cert['address'], cert['port'], cert['subject'], cert['issuer'], cert['notbefore'], cert['notafter'], cert['expired']

      elif args['output'] == 'csv':
        print args['delimiter'].join(["IP Address","port", "Subject", "Issuer", "Not Before", "Not After", "Expired"])
        for cert in certs:
          print args['delimiter'].join([cert['address'], cert['port'], cert['subject'], cert['issuer'], cert['notbefore'], cert['notafter'], cert['expired']])

      elif args['output'] == 'json':
        print json.dumps(certs, sort_keys=True, indent=2)

    sys.exit(exitcode)
