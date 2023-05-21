# DNS-oops

The **DNS Out-Of-Protocol Signalling** project had two goals

1. To implment server even signalling described in
   [dns-oops](https://datatracker.ietf.org/doc/draft-grubto-dnsop-dns-out-of-protocol-signalling/)
   in [nsd](https://www.nlnetlabs.nl/projects/nsd/), and

2. To create a proof of concept (PoC) that event signalling can be
   used in a system of servers using different software.
   
[KnotDNS](https://www.knot-dns.cz) has implmented `dbus` events,
described
[here](https://www.knot-dns.cz/docs/3.2/singlehtml/#dbus-event), to
provide a mechanism for programs outside of `KnotDNS` to react to
events in the DNS server. This is based on the description on the
Internet draft mentioned above, and step 1 of the project was to
implement a similar mechanism in `nsd`.

Step 2 was to utilise this mechanism in a PoC where BGP announcements
can be managed automagically based on the status of the DNS server
daemon. Just for fun, a system of three virtual DNS servers using
different DNS software were deployed as virtual machines in different
geographic locations using a cloud service. The signalling mechanism
was used to configure the servers to react to zone updates.

In this PoC, the serial number is used to determine *which* of the
three servers to deploy. Depending on the serial number, one specific
will announce the services prefixes and the others will withdraw the
prefixes.

The signalling algorithm overloads the serial number with information
other than just the version number of the zone. On the secondary
servers, the serial number is first divided by 3. If the remainder is
0 then one server A will engage. If the remainder is 1, server B will
engage, and if the remainder is 2 server C will engage.

**Server A** was fit with a regular unmodified `BIND` (named) DNS
server configured to send DNS NOTIFY messages to a `nsnotifyd` daemon,
which in turn interacted with an `exabgp` BGP routing daemon.

**Server B** was fit with a `KnotDNS` DNS server interacting with a
`BIRD` routing daemon.

**Server C** was fit with a doctored `nsd` DNS server interacting with
a `BIRD` routing daemon.

The various subprojects are described in the respective subdirectories
below.
