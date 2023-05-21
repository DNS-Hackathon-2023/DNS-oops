Time-stamp: <2023-05-21 08:20:52 UTC liman>

# DNS-oops/bind-notifyd

This is a simple proof of concept of a server that reacts with
external actions when a zone it serves is updated.

The server uses named (BIND) and acts as secondary for the zone
`oops.krause.nl`, and the trigger for the external action is a zone
update. Named is configured to send a DNS NOTIFY message to a local
`notifyd` daemon*. Notifyd will react to the NOTIFY message and fork
the program specified, giving it the name of the zone, the new serial
number, and the IP address of the server from which it recieved the
notify message as command line arguments.

As a proof of concept, a script was created that announces and
withdraws a service address. For demonstration purposes, the serial
number itself is overloaded with a meaning, where *this* specific
server will react to serial numbers (S) where _S_ mod 3 = 0. When
such a serial number is received, this server will announce its
service address using BGP. When a new serial number with  _S_ mod 3 !=
0, the server will withdraw its service address.

The script interacts with `exabgp` through its CLI componend
`exabgp-cli`, which is used to manipulate the BGP routing information
base.


* [https://dotat.at/prog/nsnotifyd/](https://dotat.at/prog/nsnotifyd/).
