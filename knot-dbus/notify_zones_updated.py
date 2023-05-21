#!/usr/bin/env python3

import os
import sys
import dbus
import dbus.mainloop.glib
import signal
import json
import libknot.control
from gi.repository import GLib

api_url = None
node_data_file = '/root/node_data.json'
zones = {}
# libknot.control is very time sensitive, set it to 60 seconds instead of
# the default "almost 0", just like in the PyPi examples
ctl_timeout = 60

verbose_flag = False
if '-v' in sys.argv:
    verbose_flag = True


def verbose(title, msg):
    """
    print msg if verbose flag is True
    """
    if verbose_flag:
        print(f'################ {title} ##################')
        print(msg)


def read_node_data():
    """
    Read node_data.json so we can determine which zones to monitor
    """
    with open(node_data_file, 'r') as f:
        return json.load(f)


def get_active_zones(node_data):
    """
    Get all zones and store them in the zones var with a default value of None
    """
    for zone in node_data["zones"].keys():
        zones[zone] = None


def enable_bgp(service):
    print(f'enabling BGP for {service}')
    try:
        os.popen("sudo systemctl start bird.service")
        os.popen("sudo systemctl start bird6.service")

    except OSError as ose:
        print("Error while running the command", ose)


def disable_bgp(service):
    print(f'disabling BGP for {service}')
    try:
        os.popen("sudo systemctl stop bird.service")
        os.popen("sudo systemctl stop bird6.service")

    except OSError as ose:
        print("Error while running the command", ose)


def connect_to_knot():
    """
    libknot.control connect proces in a function to prevent repetition
    """
    ctl = libknot.control.KnotCtl()
    ctl.connect("/var/run/knot/knot.sock")
    ctl.set_timeout(ctl_timeout)
    return ctl


def send_to_knot(ctl, cmd, section=None, item=None, identifier=None,
                 zone=None, owner=None, ttl=None, rtype=None, data=None,
                 flags=None, filters=None):
    """
    libknot send_block as a function, created clean code further on
    """
    ctl.send_block(cmd=cmd, section=section, item=item,
                   identifier=identifier, zone=zone, owner=owner, ttl=ttl,
                   rtype=rtype, data=data, flags=flags, filters=filters)
    # receive_block() is needed to make libknot process the send_block result
    return ctl.receive_block()


def zone_status(zone):
    """
    libknot zone_status as a function
    """
    ctl = connect_to_knot()
    try:
        resp_dict = send_to_knot(ctl, cmd="zone-status", zone=zone)  # noqa: E501
    except Exception as e:
        print(e)
    finally:
        ctl.send(libknot.control.KnotCtlType.END)
        ctl.close()
    verbose(f'zone-status({zone}) returned:', resp_dict)
    return resp_dict


def sigint_handler(sig, frame):
    """
    Cleanup if the script is interrupted
    """
    if sig == signal.SIGINT:
        loop.quit()
    else:
        raise ValueError("Undefined handler for '{}'".format(sig))


def updated(*args, **kwargs):
    """
    Event handler for Glib.MainLoop
    Also explicitly called at script startup to determine if any event handling
    needs to be done
    """
    (zone, serial) = args
    print("Zone %s updated, SOA serial %d" % (zone, serial))
    zones[zone] = serial
    if None not in zones.values():
        # Build a list of all zones with serials
        all_zone_info = ""
        for key in zones:
            all_zone_info += f'{key}:{zones[key]};'
        print(f'zones updated: {all_zone_info}')
        if (serial % 3 == 1):
            # start/enable BGP
            enable_bgp("knot")
        else:
            # stop/disable BGP
            disable_bgp("knot")
        try:  # loop probably not started when this function is first called
            loop.quit()
        except:  ## noqa E722
            return
        else:
            return


if __name__ == '__main__':
    node_data = read_node_data()
    get_active_zones(node_data)
    signal.signal(signal.SIGINT, sigint_handler)

    while 1:
        loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        try:
            knotd = bus.get_object('cz.nic.knotd', '/cz/nic/knotd',
                                   introspect=False)
        except Exception as e:
            print(f'failed to open DBus, {e}')
            sys.exit(1)
        else:
            events_iface = dbus.Interface(knotd,
                                          dbus_interface='cz.nic.knotd.events')
            events_iface.connect_to_signal("zone_updated", updated)
            loop = GLib.MainLoop()
            loop.run()


# vim: ts=4 sw=4 ai expandtab:
