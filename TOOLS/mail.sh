#!/bin/bash
#######################################################################################################################

# ----- Check script is started as root:
if [ "$EUID" -ne 0 ]; then
    echo -e "ERROR: Please run as root!"; exit 2
fi

if [ "$#" -eq "0" ]; then
    echo -e "Keine Argument angegeben, Benutze 'ein' oder 'aus'"; exit 1
fi

if [ "$1" = "aus" ]; then
    echo -e "Mail Verkehr verhindern"
    /sbin/iptables -A OUTPUT -p tcp --dport 25 -j REJECT
    /sbin/iptables -A INPUT -p tcp --dport 25 -j DROP
    /sbin/iptables -A OUTPUT -p tcp --dport 993 -j REJECT
    /sbin/iptables -A INPUT -p tcp --dport 993 -j DROP
    /sbin/iptables -A OUTPUT -p tcp --dport 143 -j REJECT
    /sbin/iptables -A INPUT -p tcp --dport 143 -j DROP
    /sbin/iptables -A OUTPUT -p tcp --dport 587 -j REJECT
    /sbin/iptables -A INPUT -p tcp --dport 587 -j DROP
    /sbin/iptables -A OUTPUT -p tcp --dport 110 -j REJECT
    /sbin/iptables -A INPUT -p tcp --dport 110 -j DROP
    /sbin/iptables -A OUTPUT -p tcp --dport 995 -j REJECT
    /sbin/iptables -A INPUT -p tcp --dport 995 -j DROP
elif [ "$1" = "ein" ]; then
    echo -e "Mail Verkehr zulassen"
    /sbin/iptables -D OUTPUT -p tcp --dport 25 -j REJECT
    /sbin/iptables -D INPUT -p tcp --dport 25 -j DROP
    /sbin/iptables -D OUTPUT -p tcp --dport 993 -j REJECT
    /sbin/iptables -D INPUT -p tcp --dport 993 -j DROP
    /sbin/iptables -D OUTPUT -p tcp --dport 143 -j REJECT
    /sbin/iptables -D INPUT -p tcp --dport 143 -j DROP
    /sbin/iptables -D OUTPUT -p tcp --dport 587 -j REJECT
    /sbin/iptables -D INPUT -p tcp --dport 587 -j DROP
    /sbin/iptables -D OUTPUT -p tcp --dport 110 -j REJECT
    /sbin/iptables -D INPUT -p tcp --dport 110 -j DROP
    /sbin/iptables -D OUTPUT -p tcp --dport 995 -j REJECT
    /sbin/iptables -D INPUT -p tcp --dport 995 -j DROP
else
    echo -e "falscher parameter benutze 'ein' oder 'aus'"
fi
