#!/bin/bash
#
#     Script to Email Open Port and SSL Report to Administrators
#     Bob Brandt <projects@brandt.ie>
#  
VERSION=0.1
PORT_EXE="/opt/brandt/GeneralScripts/CertScan/portscan.py"
SMTP_EXE="/opt/brandt/GeneralScripts/SMTP/smtpSend.py"
SWITCHES="-o html"
TMP_HTML="/tmp/portinfo.html"
TMP_HTML_HEADER="/tmp/portinfo-header.html"

smtp="smtp.opw.ie"
from="port-watch@opw.ie"
to="bob.brandt@opw.ie"
subject="Open Port and SSL Report for $( date '+%d %b %Y' )"

usage() {
        [ "$2" == "" ] || echo -e "$2"
        echo -e "Usage: $0 [options]"
        echo -e "Options:"
        echo -e " -h, --help     display this help and exit"
        echo -e " -v, --version  output version information and exit"       
        exit ${1:-0}
}

version() {
        echo -e "$0 $VERSION"
        echo -e "Copyright (C) 2011 Free Software Foundation, Inc."
        echo -e "License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>."
        echo -e "This is free software: you are free to change and redistribute it."
        echo -e "There is NO WARRANTY, to the extent permitted by law.\n"
        echo -e "Written by Bob Brandt <projects@brandt.ie>."
        exit 0
}

# Execute getopt
ARGS=$(getopt -o vh -l "help,version" -n "$0" -- "$@") || usage 1 " "

#Bad arguments
#[ $? -ne 0 ] && usage 1 "$0: No arguments supplied!\n"

eval set -- "$ARGS";

while /bin/true ; do
	case "$1" in
        -h | --help )         usage 0 ;;
        -v | --version )      version ;;
        -- )                  shift ; break ;;
        * )                   usage 1 "$0: Invalid argument!\n" ;;
        esac
        shift
done

if "$PORT_EXE" $SWITCHES > "$TMP_HTML"
then
        "$SMTP_EXE" --from "$from" --to "$to" --subject "$subject" --server "$smtp" --html "$TMP_HTML"
        logger -st "port-watch" "Open Port and SSL Report emailed to $to"
fi

exit $?

