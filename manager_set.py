import sys

from utils import (BUFFER_SIZE, SNMP_ERRORS, SNMP_SERVICE, TIMEOUT,
                   check_community, check_ip_address, check_oid, check_port)


def print_data(pdu):
    """Resolve SNMP error codes and print the response
    Args:
         pdu (str): data bytes received from agent
    Returns:
         str: SNMP error or response from the agent
    """
    if int(pdu[0]+pdu[1]) == 0:
        return pdu[3:]
    else:
        return SNMP_ERRORS[int(pdu[0]+pdu[1])]

def send_data(agent, pdu):
    """Send data through UDP socket and print the response
    Args:
         pdu (str): data bytes to send
    Returns:
         str: response from the agent
    """
    if len(str.encode(pdu)) > BUFFER_SIZE:
        print "Data length exceed the maximum allowed!"
        sys.exit(1)

    try:
        #SNMP_SERVICE.sendto(str.encode(pdu),agent)
        SNMP_SERVICE.settimeout(TIMEOUT)
        SNMP_SERVICE.sendto(pdu,agent)
        response = SNMP_SERVICE.recvfrom(BUFFER_SIZE)
        return print_data(response[0])
    except Exception as ex:
        return ex

def run_set(args):
    """Run the manager in snmp_set mode
    Args:
         *args: arguments received from the user input
    Returns:
         str: response from the agent
    """
    ip_address = ""
    port = ""
    community = ""
    oid = ""

    if check_ip_address(sys.argv[2]):
        ip_address = sys.argv[2]
    else:
        return "Invalid IP Address"

    if check_port(sys.argv[3]):
        port = sys.argv[3]
    else:
        return "Invalid Port number"

    if check_community(sys.argv[1]):
        community = sys.argv[1]
    else:
        return "Invalid community string"

    if check_oid(sys.argv[4]):
        oid = sys.argv[4]
    else:
        return "Invalid OID"

    agent = (ip_address, int(port))
    value = sys.argv[5]
    pdu = 'set ' + community + ' ' + oid + ' ' + value
    
    return send_data(agent, pdu)

if __name__ == '__main__':
    """basic implementation of an snmp manager in python using only sockets
    Args:
         *args: arguments received from the user input
    Returns:
         str: response from the snmp agent
    """
    args = sys.argv[1:]
    if len(args) < 5:
        print "This program takes exactly 5 arguments, {} given. Usage example:".format(len(args))
        print "python manager_set.py {community_string} {IP_Address} {port} {oid} {value to set}"
        sys.exit(1)
    else:
        print run_set(args)
        sys.exit(0)
