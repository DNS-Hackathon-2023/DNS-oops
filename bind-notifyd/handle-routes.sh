#!/bin/sh

IPV4_PREFIX=""
IPV6_PREFIX=""

if expr $2 % 3 ; then
    exabgp-cli withdraw route $IPV6_PREFIX
    exabgp-cli withdraw route $IPV4_PREFIX
    echo withdrawing IPv6 and IPv4 route
else
    exabgp-cli announce route $IPV6_PREFIX next-hop self
    exabgp-cli announce route $IPV4_PREFIX next-hop self
    echo announcing IPv6 and IPv4 route
fi
