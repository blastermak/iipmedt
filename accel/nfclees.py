import time
import logging
import ctypes
import string
import nfc

def hex_dump(string):
	"""Dumps data as hexstrings"""
	return ' '.join(["%0.2X" % ord(x) for x in string])
	
### NFC device setup
class NFCReader(object):
	MC_AUTH_A = 0x60
	MC_AUTH_B = 0x61
	MC_READ = 0x30
	MC_WRITE = 0xA0
	card_timeout = 10

	def __init__(self, logger):
		self.__context = None
		self.__device = None
		self.log = logger
		self._card_present = False
		self._card_last_seen = None
		self._card_uid = None
		self._clean_card()
		self.globalId = None

		mods = [(nfc.NMT_ISO14443A, nfc.NBR_106)]

		self.__modulations = (nfc.nfc_modulation * len(mods))()
		for i in range(len(mods)):
			self.__modulations[i].nmt = mods[i][0]
			self.__modulations[i].nbr = mods[i][1]

	def run(self):
		self.__context = ctypes.pointer(nfc.nfc_context())
		nfc.nfc_init(ctypes.byref(self.__context))
		self._clean_card()
		conn_strings = (nfc.nfc_connstring * 10)()
		devices_found = nfc.nfc_list_devices(self.__context, conn_strings, 10)
		self.__device = nfc.nfc_open(self.__context, conn_strings[0])
		_ = nfc.nfc_initiator_init(self.__device)

	def scanfunctie(self):
		self._poll_loop()
		self._clean_card()
		return self.globalId
		
		
	def _poll_loop(self):
		"""Starts a loop that constantly polls for cards"""
		nt = nfc.nfc_target()
		res = nfc.nfc_initiator_poll_target(self.__device, self.__modulations, len(self.__modulations), 10, 2,
											ctypes.byref(nt))
		if res < 0:
			self.globalId = "0"
		elif res >= 1:
			uid = None
			if nt.nti.nai.szUidLen == 4:
				uid = "".join([chr(nt.nti.nai.abtUid[i]) for i in range(4)])
			if uid:
				if not ((self._card_uid and self._card_present and uid == self._card_uid) and \
									time.mktime(time.gmtime()) <= self._card_last_seen + self.card_timeout):
					self._setup_device()
					self.globalId =  uid.encode("hex")
					uid = None
			else:
				print "no card"
			uid = None
			self._card_uid = uid
			self._card_present = True
			self._card_last_seen = time.mktime(time.gmtime())
		else:
			print "no card"
			self._card_present = False
			self._clean_card()

	def returnGobalId(self):
		return(self.globalId)
			
	def _clean_card(self):
		self._card_uid = None

	def _setup_device(self):
		"""Sets all the NFC device settings for reading from Mifare cards"""
		if nfc.nfc_device_set_property_bool(self.__device, nfc.NP_ACTIVATE_CRYPTO1, True) < 0:
			raise Exception("Error setting Crypto1 enabled")
		if nfc.nfc_device_set_property_bool(self.__device, nfc.NP_INFINITE_SELECT, False) < 0:
			raise Exception("Error setting Single Select option")
		if nfc.nfc_device_set_property_bool(self.__device, nfc.NP_AUTO_ISO14443_4, False) < 0:
			raise Exception("Error setting No Auto ISO14443-A jiggery pokery")
		if nfc.nfc_device_set_property_bool(self.__device, nfc.NP_HANDLE_PARITY, True) < 0:
			raise Exception("Error setting Easy Framing property")

#if __name__ == '__main__':
	# logger = logging.getLogger("cardhandler").info
	# bla = NFCReader(logger)
	# bla.run()
	# for num in range(2):
		
	# bla.scanfunctie()
