import socket
import sys
from time import sleep
from threading import Thread

from VectorMessenger import helpers as h
from VectorMessenger.MessengerCore.MessengerBase import VMUDPBase
from VectorMessenger.MessengerCore.Encryption import VMCrypt

class MessengerClient(VMUDPBase):
	def __init__(self, vm_client_ui = None, cfg = None):
		super().__init__()
		self.cfg = cfg if cfg != None else h.VMConfig.init(1)
		self.ui = vm_client_ui
		self.startMessagePolling()
	
	def messagePolling(self):
		self.ui.createLog('Message polling thread is active')
		while self.messagePollingEnabled:
			try:
				data, _ = self.sock.recvfrom(1024)
			except socket.error:
				pass
			else:
				msg = VMCrypt.decrypt(data)
				self.ui.showMessage(msg)
				h.createUniversalLog('Received message', self.ui.createLog)
			sleep(0.5)
		h.createUniversalLog('Message polling thread was stopped', self.ui.createLog)

	def startMessagePolling(self):
		self.messagePollingEnabled = True
		self.messagePollingThread = Thread(target=self.messagePolling)
		self.messagePollingThread.start()
	
	def stopMessagePolling(self):
		self.messagePollingEnabled = False
		self.sock.close()

	def sendMessage(self, text: str):
		self.__refreshConfig()
		text_bytes = VMCrypt.encrypt('@{}: {}'.format(self.cfg['username'], text))
		self.sock.sendto(text_bytes, (self.cfg['connection']['ip'], self.cfg['connection']['port']))

	def __refreshConfig(self):
		self.cfg = h.VMConfig.get(1)