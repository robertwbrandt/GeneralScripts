#!/usr/bin/env python
"""
	Python script to find and detail certian ports on a network.
	You need to run this script as root or change the setuid on the nmap binary
"""
from __future__ import print_function
import sys, argparse, textwrap, datetime, json, pprint
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

ports = [ { "name":   "FTP",
            "port":   21,
            "action": "ReportOpen"},
          { "name":   "Telnet",
            "port":   23,
            "action": "ReportOpen"},
          { "name":   "HTTPS",
            "port":   443,
            "action": "ReportCert"},
          { "name":   "Alt-HTTPS",
            "port":   981,
            "action": "ReportCert"},
          { "name":   "Alt-HTTPS",
            "port":   1311,
            "action": "ReportCert"},
          { "name":   "Alt-HTTPS",
            "port":   7000,
            "action": "ReportCert"},
          { "name":   "Alt-HTTPS",
            "port":   8009,
            "action": "ReportCert"},
          { "name":   "Alt-HTTPS",
            "port":   8090,
            "action": "ReportCert"},
          { "name":   "Alt-HTTPS",
            "port":   8443,
            "action": "ReportCert"}
        ]

targets = ["10.200.199.0/24", "10.200.200.0/24", "10.201.199.0/24", "10.201.200.0/24", "192.168.201.0/24", "10.150.0.0/16"]

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

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
      print(self.__prog + " " + self.__version)
      print("Copyright (C) 2013 Free Software Foundation, Inc.")
      print("License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.")
      version  = "This program is free software: you can redistribute it and/or modify "
      version += "it under the terms of the GNU General Public License as published by "
      version += "the Free Software Foundation, either version 3 of the License, or "
      version += "(at your option) any later version."
      print(textwrap.fill(version, self.__row))
      version  = "This program is distributed in the hope that it will be useful, "
      version += "but WITHOUT ANY WARRANTY; without even the implied warranty of "
      version += "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the "
      version += "GNU General Public License for more details."
      print(textwrap.fill(version, self.__row))
      print("\nWritten by Bob Brandt <projects@brandt.ie>.")
    else:
      print("Usage: " + self.__prog + " [options]")
      print("Script to find and detail all SSL Certs on a network.")
      print("This script requires root privileges or nmap must have root SUID.\n")
      print("Options:")
      options = []
      options.append(("-h, --help",            "Show this help message and exit"))
      options.append(("-v, --version",         "Show program's version number and exit"))
      options.append(("-o, --output OUTPUT",   "Type of output {text | csv | json | html}"))
      length = max( [ len(option[0]) for option in options ] )
      for option in options:
        description = textwrap.wrap(option[1], (self.__row - length - 5))
        print("  " + option[0].ljust(length) + "   " + description[0])
      for n in range(1,len(description)): print(" " * (length + 5) + description[n])
    exit(self.__exit)
def command_line_args():
  global args, version, parser
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('-v', '--version', action=customUsageVersion, version=version, max=80)
  parser.add_argument('-h', '--help', action=customUsageVersion)
  parser.add_argument('-o', '--output',
          required=False,
          default=args['output'],
          choices=['text', 'csv', 'json', 'html'],
          help="Display output type.")
  args.update(vars(parser.parse_args()))


def parseNmapGrep(line=""):
  '''
  https://nmap.org/book/output-formats-grepable-output.html
  '''
  host = {}
  if str(line[:5]).lower() == "host:":
    host = {"ip":"", "dns":"", "status":"", "ports":{}, "protocols":{}, "ignored state":"", "os":"", "seq index":"", "ip id seq":""}
    for field in line.split("\t"):
      field = str(field).strip()

      if str(field[:5]).lower() == "host:":
        field = str(field[5:]).strip().replace("(","/").replace(")","")
        host["ip"],host["dns"] = field.split("/")[:2]
        host["ip"] = str(host["ip"]).strip()
        host["dns"] = str(host["dns"]).strip().lower()

      if str(field[:7]).lower() == "status:":
        host["status"] = str(field[7:]).strip()

      if str(field[:14]).lower() == "ignored state:":
        host["ignored state"] = str(field[14:]).strip()

      if str(field[:3]).lower() == "os:":
        host["os"] = str(field[3:]).strip()

      if str(field[:10]).lower() == "seq index:":
        host["seq index"] = str(field[10:]).strip()

      if str(field[:10]).lower() == "ip id seq:":
        host["ip id seq"] = str(field[10:]).strip()

      if str(field[:6]).lower() == "ports:":
        for port in str(field[6:]).split(","):
          port = [ str(x).strip().replace("|","/") for x in str(port).split("/") ] + ['','','','','','']
          if port[0].isdigit(): port[0] = int(port[0])

          host["ports"][port[0]] = { "state":port[1],
                                     "protocol":port[2],
                                     "owner":port[3],
                                     "service":port[4],
                                     "sunrpc":port[5],
                                     "version":port[6]}

      if str(field[:10]).lower() == "protocols:":
        for protocol in str(field[10:]).split(","):
          protocol = [ str(x).strip().replace("|","/") for x in str(protocol).split("/") ] + ['','']
          if protocol[0].isdigit(): protocol[0] = int(protocol[0])

          host["protocols"][protocol[0]] = { "state":protocol[1], "name":protocol[2]}

  return host

def smartUpdate(dict1,dict2):
  for key in list(set(dict2.keys()) - set(['ports','protocols'])):
    if dict2[key]: dict1[key] = dict2[key]

  for port in dict2["ports"].keys():
    for key in dict2["ports"][port].keys():
      if dict2["ports"][port][key]: dict1["ports"][port] = dict2["ports"][port]
 
  for protocol in dict2["protocols"].keys():
    for key in dict2["protocols"][protocol].keys():  
      if dict2["protocols"][protocol][key]: dict1["protocols"][protocol] = dict2["protocols"][protocol]
 
  return dict1


def sortIPPort(item):
  ip, port = item
  item = [ int(octal) for octal in ip.split('.') ] + [ int(port) ]
  return tuple(item)

# Start program
if __name__ == "__main__":
  command_line_args()  

  cmd =  "nmap --system-dns -oG - -sT"
  cmd += " -p " + ",".join([ str(x["port"]) for x in ports ])
  targets = [''] + targets
  cmd += " ".join(targets)
  eprint("Trying to run command:", cmd)

  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()
  if p.returncode != 0:
    eprint(err)
    sys,exit(p.returncode)

  hosts = {}
  for line in out.split("\n"):
    host = parseNmapGrep(line)
    if host:
      if not hosts.has_key(host["ip"]):
        hosts[host["ip"]] = host
      else:
        hosts[host["ip"]] = smartUpdate(hosts[host["ip"]], host)



  # Aggressive Scanning!
  recheckhosts=set()
  for ip in hosts.keys():
    for port in ports:
      if hosts[ip]["ports"].has_key(port["port"]) and hosts[ip]["ports"][port["port"]].has_key("state"):
        if port["action"] == "ReportOpen" and hosts[ip]["ports"][port["port"]]["state"] == "open":
          recheckhosts.add(ip)

        if port["action"] == "ReportClosed" and hosts[ip]["ports"][port["port"]]["state"] == "closed":
          recheckhosts.add(ip)


  if recheckhosts:
    eprint("Use Aggressive Scanning on open and closed ports.")
    cmd = "nmap --system-dns -oG - -A " + " ".join(recheckhosts)
    eprint("Trying to run command:", cmd)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
      eprint(err)
      sys,exit(p.returncode)

    for line in out.split("\n"):
      host = parseNmapGrep(line)
      if host:
        hosts[host["ip"]] = smartUpdate(hosts[host["ip"]], host)



  sslhosts={}
  for ip in hosts.keys():
    for port in ports:
      if hosts[ip]["ports"].has_key(port["port"]) and hosts[ip]["ports"][port["port"]].has_key("state"):
        if port["action"] == "ReportCert" and hosts[ip]["ports"][port["port"]]["state"] == "open":
          if sslhosts.has_key(ip):
            sslhosts[ip] += [port["port"]]
          else:
            sslhosts[ip] = [port["port"]]

  if sslhosts: eprint("Checking for SSL Certs.")
  for host in sslhosts.keys():
    for port in sslhosts[host]:
      cmd = 'echo | timeout 5 openssl s_client -servername ' + str(host) + ' -connect ' + str(host) + ':' + str(port) + ' 2> /dev/null | openssl x509 -noout -dates -issuer'
      eprint("Trying to run command:", cmd)

      p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      out, err = p.communicate()
      for line in out.split("\n"):
        line = line.split("=",1)
        if str(line[0]).lower() in ["notbefore","notbefore","issuer"]:
          if not hosts[host]["ports"][port].has_key("cert"):
            hosts[host]["ports"][port]["cert"] = {}

        if str(line[0]).lower() == "notbefore":
          hosts[host]["ports"][port]["cert"]["notbefore"] = str(line[1]).strip()
        if str(line[0]).lower() == "notafter":
          hosts[host]["ports"][port]["cert"]["notafter"] = str(line[1]).strip()
        if str(line[0]).lower() == "issuer":
          hosts[host]["ports"][port]["cert"]["issuer"] = str(line[1]).strip()

  output={}
  for host in hosts.keys():
    output[host] = { "dns":    hosts[host]["dns"], 
                     "status": hosts[host]["status"], 
                     "os":     hosts[host]["os"],
                     "ports":  hosts[host]["ports"] }
    output[host]["ip-pretty"] = str(host)
    if hosts[host]["dns"]: output[host]["ip-pretty"] += " (" + hosts[host]["dns"] + ")"
    for port in ports:
      hosts[host]["ports"][port["port"]]["port-pretty"] = port["name"] + " (" + str(port["port"]) + ")"
      if hosts[host]["ports"][port["port"]].has_key("cert"):
        hosts[host]["ports"][port["port"]]["cert"]["notbefore-sort"] = datetime.datetime.strptime(hosts[host]["ports"][port["port"]]["cert"]["notbefore"],'%b %d %H:%M:%S %Y %Z').strftime('%Y/%m/%d %H:%M:%S')
        hosts[host]["ports"][port["port"]]["cert"]["notafter-sort"] = datetime.datetime.strptime(hosts[host]["ports"][port["port"]]["cert"]["notafter"],'%b %d %H:%M:%S %Y %Z').strftime('%Y/%m/%d %H:%M:%S')


  if args['output'] == "json":
    print(json.dumps(output))
  elif args['output'] == "csv":
    hostkeys = sorted(output.keys(), key=my_key)
    for host in hostkeys:
      portkeys = sorted(output[host]["ports"].keys())
      for port in portkeys:
        tmp = [ host,output[host]["dns"],port,output[host]["ports"][port]["service"],output[host]["ports"][port]["state"],output[host]["ports"][port]["os"] ]
        if output[host]["ports"][port].has_key("cert"):
          tmp += [ output[host]["ports"][port]["cert"]["notbefore"],output[host]["ports"][port]["cert"]["notafter"],str(output[host]["ports"][port]["cert"]["issuer"]).replace(",","_") ]
        else:
          tmp += ["","",""]
        print(",".join([str(x) for x in tmp]))
  elif args['output'] == "text":
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(output)
  elif args['output'] == "html":
    date = datetime.datetime.now().strftime('%d %b %Y')
    print('')
    print('<html>')
    print('\t<head>')
    print('\t\t<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>')
    print('\t\t<title>Open Ports and SSL Report for ' + date + '</title>')
    print('\t</head>')
    print('\t<body>')
    print('\t\t<style type="text/css">')
    print('\t\t\tbody,div,p { text-align: left; color:black; font-family:"Liberation Sans"}')
    print('\t\t\ttable,thead,tbody,tfoot,tr,th,td { text-align: right; color:black; font-family:"Liberation Sans"; font-size:x-small }')
    print('\t\t\tth { text-align: center; padding: 0px 10px 0px 10px; }')
    print('\t\t\ttd { text-align: left; padding: 0px 10px 0px 10px; white-space: nowrap; }')
    print('\t\t\ttr.details:hover { background: #BBBFFF }')
    print('\t\t\t.lag { color:red; font-weight: bold; }')
    print('\t\t\t.Warning { background: #FFFFFFF }')
    print('\t\t\t.Error { background: #FFFFCC }')
    print('\t\t\t.Critical { background: #FFCCCC }')
    print('\t\t</style>')

    tmp = [ str(x["name"] + "(" + str(x["port"]) + ")") for x in ports if x["action"] == "ReportOpen" ]
    if len(tmp) > 1: tmp = ", ".join(tmp[:-1]) + " and " + tmp[-1]

    print('\t\t<br/>Below are tables which list of machines with open ' + str(tmp) + ' ports and machines with SSL ports.<br/>')

    print('\t\t<table border="1" align="center">')
    print('\t\t\t<caption><h2>Open Ports</h2></caption>')

    testport = [ p["port"] for p in ports if p["action"] == "ReportOpen" ]
    openhosts = []
    for host in output.keys():
      for port in output[host]["ports"]:
        if port in testport and output[host]["ports"][port]["state"] == "open":
          openhosts.append([host,port])
    openhosts = sorted(openhosts, key=sortIPPort)

    if openhosts:
      print('\t\t\t<tr>')
      print('\t\t\t\t<th align="center" height="32">IP (DNS Name)</th>')
      print('\t\t\t\t<th align="center">Port</th>')
      print('\t\t\t\t<th align="center">State</th>')
      print('\t\t\t\t<th align="center">Operating System</th>')
      print('\t\t\t</tr>')
      for host,port in openhosts:
        print('\t\t\t<tr>')
        print('\t\t\t\t<td>' + output[host]["ip-pretty"] + '</td>')
        print('\t\t\t\t<td>' + output[host]["ports"][port]["port-pretty"] + '</td>')
        print('\t\t\t\t<td class="lag">' + output[host]["ports"][port]["state"] + '</td>')
        print('\t\t\t\t<td>' + output[host]["os"] + '</td>')
        print('\t\t\t</tr>')
    else:
      print('\t\t\t<tr>')
      print('\t\t\t\t<th align="center" height="32" colspan="4">No Open Ports were found!</th>')
      print('\t\t\t</tr>')
    print('\t\t</table>')
    print('\t\t<br/>')


    # print('\t\t<table border="1" align="center">')
    # print('\t\t\t<caption><h2>Closed Ports</h2></caption>')

    # testport = [ p["port"] for p in ports if p["action"] == "ReportClosed" ]
    # closedhosts = []
    # for host in output.keys():
    #   for port in output[host]["ports"]:
    #     if port in testport and output[host]["ports"][port]["state"] == "closed":
    #       closedhosts.append([host,port])
    # closedhosts = sorted(closedhosts, key=sortIPPort)

    # if closedhosts:
    #   print('\t\t\t<tr>')
    #   print('\t\t\t\t<th align="center" height="32">IP (DNS Name)</th>')
    #   print('\t\t\t\t<th align="center">Port</th>')
    #   print('\t\t\t\t<th align="center">State</th>')
    #   print('\t\t\t\t<th align="center">Operating System</th>')
    #   print('\t\t\t</tr>')
    #   for host,port in closedhosts:
    #     print('\t\t\t<tr>')
    #     print('\t\t\t\t<td>' + output[host]["ip-pretty"] + '</td>')
    #     print('\t\t\t\t<td>' + output[host]["ports"][port]["port-pretty"] + '</td>')
    #     print('\t\t\t\t<td class="lag">' + output[host]["ports"][port]["state"] + '</td>')
    #     print('\t\t\t\t<td>' + output[host]["os"] + '</td>')
    #     print('\t\t\t</tr>')
    # else:
    #   print('\t\t\t<tr>')
    #   print('\t\t\t\t<th align="center" height="32" colspan="4">No Open Ports were found!</th>')
    #   print('\t\t\t</tr>')
    # print('\t\t</table>')
    # print('\t\t<br/>')


    print('\t\t<table border="1" align="center">')
    print('\t\t\t<caption><h2>SSL Certificates</h2></caption>')

    testport = [ p["port"] for p in ports if p["action"] == "ReportCert" ]
    sslhosts = []
    for host in output.keys():
      for port in output[host]["ports"]:
        if port in testport and output[host]["ports"][port]["state"] == "open":
          sslhosts.append([host,port])
    sslhosts = sorted(sslhosts, key=sortIPPort)

    if sslhosts:
      print('\t\t\t<tr>')
      print('\t\t\t\t<th align="center" height="32">IP (DNS Name)</th>')
      print('\t\t\t\t<th align="center">Port</th>')
      print('\t\t\t\t<th align="center">Not Before</th>')
      print('\t\t\t\t<th align="center">Not After</th>')
      print('\t\t\t\t<th align="center">Issuer</th>')
      print('\t\t\t</tr>')
      for host,port in sslhosts:
        print('\t\t\t<tr>')
        print('\t\t\t\t<td><a href="https://' + str(host)  + ':' + str(port) + '">' + output[host]["ip-pretty"] + '</a></td>')
        print('\t\t\t\t<td>' + output[host]["ports"][port]["port-pretty"] + '</td>')
        if output[host]["ports"][port].has_key("cert"):
          classStr = ""
          lastMonth = datetime.datetime.now() - datetime.timedelta(weeks=5)
          if lastMonth > datetime.datetime.strptime(output[host]["ports"][port]["cert"]["notafter-sort"],'%Y/%m/%d %H:%M:%S'):
            classStr = ' class="lag"'

          print('\t\t\t\t<td' + classStr + '>' + output[host]["ports"][port]["cert"]["notbefore"] + '</td>')
          print('\t\t\t\t<td' + classStr + '>' + output[host]["ports"][port]["cert"]["notafter"] + '</td>')
          print('\t\t\t\t<td' + classStr + '>' + output[host]["ports"][port]["cert"]["issuer"] + '</td>')
        else:
          print('\t\t\t\t<th colspan="3" class="lag">Invalid Certificate</th>')
        print('\t\t\t</tr>')
    else:
      print('\t\t\t<tr>')
      print('\t\t\t\t<th align="center" height="32" colspan="4">No SSL Ports were found!</th>')
      print('\t\t\t</tr>')
    print('\t\t</table>')


    print("\t\t<br/>This email was produced automatically by a script, please don't respond.<br/>")
    print('\t</body>')
    print('</html>')

  sys.exit(0)
