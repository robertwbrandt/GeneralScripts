#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python script to scan a directory for certain file types
"""
import argparse, os, fnmatch, datetime, subprocess
import textwrap, json, csv

# Import Brandt Common Utilities
import sys, os
sys.path.append( os.path.realpath( os.path.join( os.path.dirname(__file__), "/opt/brandt/common" ) ) )
import brandt
sys.path.pop()

version = 0.1
defaultMedia = ['avi','rm','mp[1-4]','wma','mod','cda','mid','m3u','pls','xm','asf','rmi','midi','au','aif','wav']
defaultIgnore = ['~snapshot','.snapshot','*.tmp']
args = {}
args['verbose'] = False
args['output'] = 'json'
args['pathlength'] = 230
args['media'] = None
args['size'] = []
args['parentsize'] = []
args['ignore'] = None
args['path'] = None
args['thunderbird'] = False
args['pmail'] = False
args['windowsprofile'] = False
args['backup'] = False

searchResult = []
pastUsages = {}

defaultThunderbird = (("Thunderbird","*.msf"),)
defaultPMail = (("PMail","*.pmm"),)
defaultWindowsProfile = (("Windows Profile","ntuser.dat"),)
defaultBackups = (("Backups","* laptop*"),
                  ("Backups","*laptop *"),
                  ("Backups","* HDD*"),
                  ("Backups","*HDD *"),
                  ("Backups","*copy of *"),
                  ("Backups","* old*"),
                  ("Backups","*old *"),
                  ("Backups","*.old*"),
                  ("Backups","* backup*"),
                  ("Backups","*backup *"),
                  ("Backups","* recovered*"),
                  ("Backups","*recovered *"),
                  ("Backups","* archive*"),
                  ("Backups","*archive *"),)


class customUsageVersion(argparse.Action):
  def __init__(self, option_strings, dest, **kwargs):
    self.__version = str(kwargs.get('version', ''))
    self.__prog = str(kwargs.get('prog', os.path.basename(__file__)))
    self.__row = min(int(kwargs.get('max', 80)), brandt.getTerminalSize()[0])
    self.__exit = int(kwargs.get('exit', 0))
    super(customUsageVersion, self).__init__(option_strings, dest, nargs=0)
  def __call__(self, parser, namespace, values, option_string=None):
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
      print "Usage: " + self.__prog + " [options] Path"
      print "Script used to find certain file types in a directory.\n"
      print "Options:"
      options = []
      options.append(("-h, --help",                          "Show this help message and exit."))
      options.append(("-v, --version",                       "Show program's version number and exit."))
      options.append(("-V, --verbose",                       "Explain what is being done."))
      options.append(("-o, --output OUTPUT",                 "Type of output {json | csv }"))      
      options.append(("-i, --ignore [PATTERN,[PATTERN]...]", "Ignore these patterns."))
      options.append(("-m, --media [EXT,[EXT]...]",          "Find media files."))
      options.append(("-s, --size LABEL PATTERN",            "Report the size (usage) of directories matching a give pattern."))
      options.append(("-p, --parentsize LABEL PATTERN",      "Report the size (usage) of parent directory of a file matching a give pattern."))
      options.append(("-l, --pathlength LENGTH",             "Find paths (including filename) which are longer than LENGTH."))
      options.append(("    --thunderbird",                   "Find Thunderbird Mail Folders."))
      options.append(("    --pmail",                         "Find Pegasus Mail Folders."))
      options.append(("    --windowsprofile",                "Find Windows Profile Folders."))
      options.append(("    --backup",                        "Find Backup Folders."))
      options.append(("path",                    "Path to search."))
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
  parser.add_argument('-V', '--verbose',
          required=False,
          default=args['verbose'],
          action="store_true",
          help="Explain what is being done.")    
  parser.add_argument('-o', '--output',
          required=False,
          default=args['output'],
          choices=['json', 'csv'],
          help="Display output type.")  
  parser.add_argument('-m', '--media',
          nargs='*',
          required=False,
          default=None,
          type=str,
          help="Find media files.")
  parser.add_argument('-i', '--ignore',
          nargs='*',
          required=False,
          default=None,
          type=str,
          help="Ignore these patterns.")
  parser.add_argument('-s', '--size',
          nargs=2,    
          required=False,
          default=args['size'],          
          action='append',
          type=str,
          help="Report the size usage of directories matching a give pattern.")
  parser.add_argument('-p', '--parentsize',
          nargs=2,    
          required=False,
          default=args['parentsize'],
          action='append',
          type=str,
          help="Report the size (usage) of parent directory of a file matching a give pattern.")
  parser.add_argument('-l', '--pathlength',
          required=False,
          type=int,
          help="Find paths (including filename) which are longer than LENGTH.")  
  parser.add_argument('--thunderbird', action="store_true")
  parser.add_argument('--pmail', action="store_true")
  parser.add_argument('--windowsprofile', action="store_true")
  parser.add_argument('--backup', action="store_true")
  parser.add_argument('path',
          nargs='+',    
          action='store',
          help="Path to search..")
  args.update(vars(parser.parse_args()))

  if args['thunderbird']:
    try:    args['parentsize'] += defaultThunderbird
    except: args['parentsize'] = defaultThunderbird
  if args['pmail']:
    try:    args['parentsize'] += defaultPMail
    except: args['parentsize'] = defaultPMail 
  if args['windowsprofile']:
    try:    args['parentsize'] += defaultWindowsProfile
    except: args['parentsize'] = defaultWindowsProfile  
  if args['backup']:
    try:    args['size'] += defaultBackups
    except: args['size'] = defaultBackups

  if isinstance(args['media'],list) and len(args['media']) == 0: args['media'] = defaultMedia
  if isinstance(args['ignore'],list) and len(args['ignore']) == 0: args['ignore'] = defaultIgnore
  if args['size']:
    temp = args['size']
    args['size'] = []
    for label, pattern in temp: args['size'].append({'label':label, 'pattern':pattern})
  if args['parentsize']:
    temp = args['parentsize']
    args['parentsize'] = []
    for label, pattern in temp: args['parentsize'].append({'label':label, 'pattern':pattern})
  if args['media']: args['media'] = [ str(x).lower() for x in args['media'] ]
  if args['ignore']: args['ignore'] = [ str(x).lower() for x in args['ignore'] ]


def imatch(string,pattern):
  try:
    return fnmatch.fnmatch(unicode(string).lower(),unicode(pattern).lower())
  except:
    return False


def getSize(path,file=None):
  global pastUsages

  try:
    if file: path = os.path.join(path,file)
    if not pastUsages.has_key(path): pastUsages[path] = int(subprocess.check_output(['du','-s', path]).split()[0].decode('utf-8'))
    return pastUsages[path]
  except:
    return -1  


def getDate(path,file=None):
  try:
    if file: path = os.path.join(path,file)

    return str(datetime.date.fromtimestamp(os.path.getatime(path)).strftime('%Y-%m-%d %H:%M:%S')) 
  except:
    return "---"



def getListing(path):
  try:
    return os.listdir(unicode(path))
  except:
    return []


def checkMedia(path, entry):
  global args,searchResult

  tmp = str(entry).lower()
  for ext in args['media']:
    ext = '*.' + ext
    if imatch(tmp,ext):
      searchResult.append({"type":"media",
                           "path":path,
                           "entry":entry,
                           "size":getSize(path,entry),
                           "modified":getDate(path,entry)})
      break


def checkParentSize(path):
  global args,searchResult

  if os.path.isdir(path):
    for entry in args["parentsize"]:
      for item in getListing(path):
        if imatch(item,entry['pattern']):
          searchResult.append({"type":entry['label'],
                               "path":path,
                               "entry":entry['pattern'],
                               "size":getSize(path),
                               "modified":getDate(path)})
          return True

  return False


def checkPathSize(path):
  global args,searchResult

  if os.path.isdir(path):
    for entry in args["size"]:
      if imatch(os.path.basename(path) + os.path.sep,entry['pattern']):
        searchResult.append({"type":entry['label'],
                             "path":path,
                             "entry":entry['pattern'],
                             "size":getSize(path),
                             "modified":getDate(path)})
        return True

  return False


def checkPathLength(path, entry):
  global args,searchResult

  length = len(path) + len(entry)

  if length >= args['pathlength']:
    searchResult.append({"type":'pathlength',
                         "path":path,
                         "entry":entry,
                         "size":length,
                         "modified":getDate(path,entry)})


def searchPath(path):
  global args,searchResult

  if args['verbose']:
    sys.stderr.write( "Checking path: " )
    sys.stderr.write( path )
    sys.stderr.write( "\n" )

  if not os.path.isdir(path):
    raise ValueError( str(path) + " is not a valid path" )

  path = os.path.abspath(unicode(path))

  if args['size']: checkPathSize(path)
  if not (args["parentsize"] and checkParentSize(path)):
    for item in getListing(path):
      try:
        fullpath = os.path.join(path,item)
      except:
        fullpath = None

      ignore = False
      if args['ignore']:
        for pattern in args['ignore']:
          if imatch(item, pattern):
            ignore = True
            break

      if fullpath and not ignore:
        if os.path.isdir(fullpath):          
            searchPath(fullpath)
        elif os.path.isfile(fullpath):
          if args['media']: checkMedia(path,item)
          if args['pathlength']: checkPathLength(path,item)


# Start program
if __name__ == "__main__":
  command_line_args()

  for path in args['path']:
    searchPath(path)

  if args['output'] == 'json':
    print json.dumps(searchResult, sort_keys=True, indent=2)
  else:
    writer = csv.DictWriter(sys.stdout, fieldnames=['type','path','entry','size','modified'],quoting=csv.QUOTE_NONNUMERIC)
    writer.writeheader()
    for line in searchResult:
      try:
        writer.writerow(line)
      except:
        pass

  sys.exit(0)
