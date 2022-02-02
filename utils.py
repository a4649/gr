import socket
import sys

TIMEOUT = 3
BUFFER_SIZE = 256
OCTET_STRING_SIZE = 16
DISPLAY_STRING_SIZE = 32
SNMP_SERVICE = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

SNMP_ERRORS = {
	00: 'No Error',
	02: 'Bad OID',
	03: 'Bad value',
	04: 'Read Only',
	05: 'General Error',
	06: 'No access'
}

def check_file(path_to_file):
	"""Check if provided mib file exists
    	Args:
       	 str: OID
    	Returns:
       	 bool: True or False
    	"""
	try:
		f = open(path_to_file)
		f.close()
		return True
	except IOError:
		return False

def check_octetstring_size(octet_string):
	"""Check if octect string size is valid
    	Args:
       	 str: OID
    	Returns:
       	 bool: True or False
    	"""
	if len(octet_string) < OCTET_STRING_SIZE:
		return True
	else:
		return False

def check_displaystring_size(display_string):
	"""Check if displaystring size is valid
    	Args:
       	 str: display string
    	Returns:
       	 bool: True or False
    	"""
	if len(display_string) < DISPLAY_STRING_SIZE:
		return True
	else:
		return False

def check_oid(oid):
	"""Check if provided OID is valid
    	Args:
       	 str: OID
    	Returns:
       	 bool: True or False
    	"""
	invalid_chars = '!@#$%^&*()-+?_=,<>/"'
	if any(c in invalid_chars for c in oid) or any(c.isalpha() for c in oid):
		return False
	else:
		return True

def check_community(community):
	"""Check if community string is valid: only regular chars
    	Args:
       	 str: community string
    	Returns:
       	 bool: True or False
    	"""
	invalid_chars = '!@#$%^&*()-+?_=,.<>/"'
	if any(char in invalid_chars for char in community):
		return False
	else:
		return True

def check_port(port):
	"""Check if provided port is a valid TCP port
    	Args:
       	 int: TCP port 
    	Returns:
       	 bool: True or False
    	"""
	try:
		if int(port) > 0 and int(port) < 65535:
			return True
		else:
			return False
	except ValueError:
		return False

def check_ip_address(ipaddress):
	"""Check if provided IP Address is a valid IPv4 Address
    	Args:
       	 str: IP Address 
    	Returns:
       	 bool: True or False
    	"""
	try:
		socket.inet_pton(socket.AF_INET, ipaddress)
		return True
	except socket.error as err:
		return False

class MIB:
	"""Class that represents a MIB
    	"""
	objects = {}

	@property
	def file(self):
		return self.__file

	@property
	def community(self):
		return self.__community

	@property
	def port(self):
		return self.__port

	@property
	def base_oid(self):
		return self.__base_oid


	def get_objects(self):
		return self.objects

	def get_data(self, oid):
		"""Get data from mib
    		Args:
        	 oid: object ID 
    		Returns:
        	 str: error code and data
        	"""
		for k,v in self.get_objects().items():
			if isinstance(v,dict):
				if k == oid:
					return "00 " + k + "=" + v['type'] + ":" + v['value']
		return "02"

	def get_value(self, oid):
		"""Get current object value from mib
    		Args:
        	 oid: object ID 
    		Returns:
        	 string: current value
        	"""
		for k,v in self.get_objects().items():
			if isinstance(v,dict):
				if k == oid:
					return v['value']
		return False

	def write_mib(self, oid, new_value):
		"""Write changes to mib file
		Args:
	    	 oid: object ID
	    	 new_value: new value to write 
		Returns:
	    	 str: error code
		"""
		old_value = self.get_value(oid) # get current value
		target_oid = oid.replace(self.base_oid,'') # remove base oid from pdu
		try:
			file_input = open(self.file, 'r')
			new_content = ""
			for line in file_input: # iterate each line in MIB file
				tmp_line = line.rstrip() # remove whitespaces at the end of the line
				values = str.split(tmp_line) # get a list of strings by spliting line from white spaces
				if values[0] == target_oid:
					new_line = target_oid + " " + self.objects[oid]['type'] + " " + self.objects[oid]['mode'] + " " + new_value
					new_content += new_line + '\n'
				else:
					new_content += tmp_line + '\n'
			file_input.close()
			file_output = open(self.file, 'w')
			file_output.write(new_content) # write new value
			file_output.close()
			return '00' # OK
		except:
			return '05' # General Error

	def set_data(self, oid, new_value):
		"""Set data to mib
    		Args:
        	 oid: object ID
        	 new_value: new value to write 
    		Returns:
        	 str: error code
    		"""
		try:
			if not self.objects[oid]:
				return '02' # Bad OID
			if not self.objects[oid]['mode'] == 'RW':
				return '04' # Read Only
		except:
			return '05' # General Error

		if self.objects[oid]['type'] == 'Integer':
			try:
				int(new_value)
			except Exception as ex:
				return '03' # Bad Value

		if self.objects[oid]['type'] == 'OctetString':
			if not check_octetstring_size(new_value):
				return '03' # Bad Value

		if self.objects[oid]['type'] == 'DisplayString':
			if not check_displaystring_size(new_value):
				return '03' # Bad Value


		result = self.write_mib(oid, new_value) # write new value to MIB file

		if result == "00": # if write failed, do not update the object in memory
			self.objects[oid]['value'] = new_value
		
		return result
		#return self.write_mib(oid, new_value)

	def update_value(self, request):
		"""Update mib value
    		Args:
        	 str: request 
    		Returns:
        	 str: error code
    		"""
		tmp_data = request.rstrip()
		values = str.split(tmp_data)

		try:
			oid = values[2]
		except IndexError:
			return '05' # General Error

		if self.objects[oid]['type'] == 'DisplayString':
			first = 0
			last = 0
			tmp_text = ""
			text = ""
			for i in range(3, len(values)): # concatenate the string
				tmp_text = tmp_text + values[i] + " "
			tmp_text = tmp_text[:-1]
			text = '\"' + tmp_text + '\"'

			return self.set_data(oid, text)
		else:
			return self.set_data(oid, values[3])

	def get_status(self):
		"""Check if MIB file is valid
		Returns:
        	 bool: True is MIB is valid, False if MIB is not valid
    		"""
		if not check_community(self.__community):
			return False
		if not check_port(self.__port):
			return False
		if len(self.get_objects()) < 1:
			return False
		return True

	def read_mib(self):
		first = 0
		last = 0
		text = ""

		with open(self.file,'r') as file:
			for line in file:
				tmp_line = line.rstrip() # remove whitespaces at the end of the line

				# if line is a comment, ignore it
				if tmp_line[0] == '#':
					continue
				else: # if not, split line by white spaces
					values = str.split(tmp_line)

				try:
					# if line start with number, is the UDP port
					if int(values[0]) > 0 and int(values[0]) < 65535:
						self.__port = values[0]
						self.__community = values[1]
						self.__base_oid = values[2]
				except ValueError:
					pass

				try:				
					# if line starts with a dot, is an object instance
					if values[0][0] == ".":
						object_oid = self.__base_oid + values[0]
						if values[1] == 'DisplayString':
							for idx, p in enumerate(values): # get indexes of chars that belong to a string (DisplayString)
								if '"' in p and first == 0:
									first = idx
								elif '"' in p and first > 0:
									last = idx
								else:
									continue
							for i in range(first, last + 1): # concatenate the string
								text = text + values[i] + " "
							self.objects[object_oid] = {'type':values[1],'mode':values[2],'value':text}
						else:
							self.objects[object_oid] = {'type':values[1],'mode':values[2],'value':values[3]}
				except IndexError:
					pass

	def __init__(self, mib_file):
		"""
		Basic constructor
		Args:
		   str: path to MIB file
		"""
		#self.file = mib_file
		self.__file = mib_file
		self.read_mib()

