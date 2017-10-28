#!/usr/bin/env python

"""
OVERVIEW

Extract selected sensor information from Cb Response.
"""

import argparse
import csv
import os
import sys

from cbapi.response import CbEnterpriseResponseAPI
from cbapi.response.models import Sensor


def log_err(msg):
    """Format msg as an ERROR and print to stderr.
    """
    msg = 'ERROR: {0}\n'.format(msg)
    sys.stderr.write(msg)


def log_info(msg):
    """Format msg and print to stdout.
    """
    msg = '{0}\n'.format(msg)
    sys.stdout.write(msg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=str, action="store",
                        help="The credentials.response profile to use.")

    # File output
    parser.add_argument("--prefix", type=str, action="store",
                        help="Output filename prefix.")

    # Cb Response Sensor query paramaters
    s = parser.add_mutually_exclusive_group(required=False)
    s.add_argument("--group-id", type=int,  action="store",
                        help="Target sensor group based on numeric ID.")
    s.add_argument("--hostname", type=str,  action="store",
                        help="Target sensor matching hostname.")
    s.add_argument("--ip", type=str,  action="store",
                        help="Target sensor matching IP address (dotted quad).")

    args = parser.parse_args()

    if args.prefix:
        output_filename = '%s-sensors.csv' % args.prefix
    else:
        output_filename = 'sensors.csv'

    if args.profile:
        cb = CbEnterpriseResponseAPI(profile=args.profile)
    else:
        cb = CbEnterpriseResponseAPI()

    output_file = file(output_filename, 'w')
    writer = csv.writer(output_file, quoting=csv.QUOTE_ALL)

    header_row = ['computer_name', 
                  'computer_dns_name',
                  'sensor_group_id',
                  'os',
                  'os_type',
                  'computer_sid',
                  'last_checkin_time',
                  'registration_time',
                  'network_adapters',
                  'id',
                  'group_id',
                  'num_eventlog_mb',
                  'num_storefiles_mb',
                  'systemvolume_free_size',
                  'systemvolume_total_size',
                  'health',
                  'commit_charge_mb',
                  'build_version_string']
    writer.writerow(header_row)

    query_base = None
    if args.group_id:
        query_base = 'groupid:{0}'.format(args.group_id)
    elif args.hostname:
        query_base = 'hostname:{0}'.format(args.hostname)
    elif args.ip:
        query_base = 'ip:{0}'.format(args.ip)

    if query_base is None:
        sensors = cb.select(Sensor)
    else:
        sensors = cb.select(Sensor).where(query_base)

    num_sensors = len(sensors)
    log_info("Found {0} sensors".format(num_sensors))

    counter = 1
    for sensor in sensors:
        if counter % 10 == 0:
            print "{0} of {1}".format(counter, num_sensors)

        if len(sensor.resource_status) > 0:
            commit_charge = "{0:.2f}".format(float(sensor.resource_status[0]['commit_charge'])/1024/1024)
        else:
            commit_charge = ''
        num_eventlog_mb = "{0:.2f}".format(float(sensor.num_eventlog_bytes)/1024/1024)
        num_storefiles_mb = "{0:.2f}".format(float(sensor.num_storefiles_bytes)/1024/1024)
        systemvolume_free_size = "{0:.2f}".format(float(sensor.systemvolume_free_size)/1024/1024)
        systemvolume_total_size = "{0:.2f}".format(float(sensor.systemvolume_total_size)/1024/1024)

        output_fields = [sensor.computer_name.lower(),
                         sensor.computer_dns_name.lower(),
                         sensor.group_id,
                         sensor.os,
                         sensor.os_type,
                         sensor.computer_sid,
                         sensor.last_checkin_time,
                         sensor.registration_time,
                         sensor.network_adapters,
                         sensor.id,
                         sensor.group_id,
                         num_eventlog_mb,
                         num_storefiles_mb,
                         systemvolume_free_size,
                         systemvolume_total_size,
                         sensor.sensor_health_message,
                         commit_charge,
                         sensor.build_version_string]

        row = [col.encode('utf8') if isinstance(col, unicode) else col for col in output_fields]
        writer.writerow(row)

        counter += 1

    output_file.close()


if __name__ == '__main__':

    sys.exit(main())