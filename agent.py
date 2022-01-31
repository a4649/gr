#!/usr/bin/env python

# needed to get user console line arguments
import sys

from utils import BUFFER_SIZE, MIB, SNMP_SERVICE, TIMEOUT

verbose = False

def check_verbose(mode):
	"""Check if user set the verbose flag
    Args:
         *args: argument sent by user
    """
	global verbose
	if mode == '-v':
		verbose = True

def handle_request(request):
	"""Check if request is GET or SET
    Args:
         *args: request sent from the manager
    Returns:
         str: response from the agent
    """
	tmp_data = str.split(request)

	try:
		method = tmp_data[0]
		community = tmp_data[1]
		oid = tmp_data[2]
	except IndexError:
		return '05' # General Error

	if not community == mib.get_community():
		return '06' # No access

	if method == 'get':
		return mib.get_data(oid)
	elif method == 'set':
		new_value = ""
		if tmp_data[3]:
			#for i in range(3, len(tmp_data)): # concatenate the string
			#	new_text = new_text + tmp_data[i] + " "
			#return mib.set_data(oid, new_value)
			return mib.update_value(request)
		else:
			return '03' # Bad value
	else:
		return '05' # General Error

def run_agent(mib):
	"""Bind UDP socket
    Returns:
         str: request if verbose is on
    """
	try:
		SNMP_SERVICE.bind(('0.0.0.0', int(mib.get_port())))
		print "SNMP service listening on port {}...".format(mib.get_port())
		if verbose:
			print "Verbose is ON"
		print "Press CTRL+C to quit"

	except Exception as ex:
		print "Unable to start service: {}".format(ex)
		sys.exit(1)

	try:
		while(True):
			bytes_pair = SNMP_SERVICE.recvfrom(BUFFER_SIZE)
			request_cmd = bytes_pair[0]
			request_from = bytes_pair[1]
			if verbose:
				print request_from[0] + ": " + request_cmd
			SNMP_SERVICE.settimeout(TIMEOUT)
			SNMP_SERVICE.sendto(str.encode(handle_request(request_cmd)), request_from)
	except KeyboardInterrupt:
		sys.exit(0)

if __name__ == '__main__':
    """basic implementation of an snmp agent in python using only sockets
    Args:
         *args: verbose mode
    Returns:
         str: status of the agent
    """
    try:
    	check_verbose(sys.argv[1])
    except IndexError:
    	pass

    mib = MIB()
    if mib.get_status():
    	run_agent(mib)
    else:
    	print "Invalid or missing MIB file"
    	sys.exit(1)
