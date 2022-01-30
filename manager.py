import sys

from utils import BUFFER_SIZE, SNMP_ERRORS, SNMP_SERVICE

agent = None

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

def send_data(pdu):
    """Send data through UDP socket and print the responde
    Args:
         pdu (str): data bytes to send
    Returns:
         str: response from the agent
    """
    if len(str.encode(pdu)) > BUFFER_SIZE:
        print "Data length exceed the maximum allowed!"
        sys.exit(1)

    try:
        #print "target: {}".format(agent)
        #print "message: {}".format(pdu)
        SNMP_SERVICE.sendto(str.encode(pdu),agent)
        response = SNMP_SERVICE.recvfrom(BUFFER_SIZE)
        return print_data(response[0])
    except Exception as ex:
        print ex
        sys.exit(1)

def run_get(*args):
    """Run the manager in snmp_get mode
    Args:
         *args: arguments received from the user input
    Returns:
         str: response from the agent
    """
    global agent

    try:
        community = sys.argv[2]
        ip_address = sys.argv[3]
        port = sys.argv[4]
        agent = (ip_address, int(port))
        oid = sys.argv[5]
        pdu = 'get ' + community + ' ' + oid
        return send_data(pdu)
    except Exception as ex:
        return "Invalid usage. Usage:\npython manager.py get {community_string} {IP_Address} {port} {oid}"

def run_set(*args):
    """Run the manager in snmp_set mode
    Args:
         *args: arguments received from the user input
    Returns:
         str: response from the agent
    """
    global agent

    try:
        community = sys.argv[2]
        ip_address = sys.argv[3]
        port = sys.argv[4]
        agent = (ip_address, int(port))
        oid = sys.argv[5]
        value = sys.argv[6]
        pdu = 'set ' + community + ' ' + oid + ' ' + value
        return send_data(pdu)
    except Exception as ex:
        return "Invalid usage. Usage:\npython manager.py set {community_string} {IP_Address} {port} {oid} {value}"

if __name__ == '__main__':
    """basic implementation of an snmp manager in python using only sockets
    Args:
         *args: arguments received from the user input
    Returns:
         str: response from the snmp agent
    """
    try:
        if sys.argv[1] == 'get':
            print run_get(*sys.argv[1:])
        elif sys.argv[1] == 'set':
            print run_set(*sys.argv[1:])
        else:
            print "Invalid usage. Examples:"
            print "python manager.py get {community_string} {IP_Address} {port} {oid}"
            print "python manager.py set {community_string} {IP_Address} {port} {oid} {value to set}"
            sys.exit(1)
    except Exception as ex:
      print ex
      sys.exit(1)
