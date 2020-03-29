from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import random
import threading



ADMIN_PASSWD=""
DATA_DICT={}
LIST_ADDR=[]
USED_NAMES=[]
class LWebSocketServer(WebSocket):
	def handleMessage(self):
		thr=threading.Thread(target=self.process_message,args=(),kwargs={})
		thr.start()
	def handleConnected(self):
		pass
	def handleClose(self):
		USED_NAMES.remove(self.CHAT_NAME)
		del DATA_DICT[self.address]
		LIST_ADDR.remove(self.address)
		print("leave:\t"+self.CHAT_NAME)
		self.sendall("leave:"+self.CHAT_NAME)
	def sendall(self,m):
		for c in LIST_ADDR:
			DATA_DICT[c]["socket"].sendMessage(m)
	def process_message(self,*args):
		msg=self.data
		self.sendMessage("null")
		if ((not hasattr(self,"CHAT_NAME") and msg!="setup") or (msg=="setup" and hasattr(self,"CHAT_NAME"))):
			return
		if (msg[:4]=="txt:"):
			print("Message:\t"+self.CHAT_NAME+":\t"+msg[4:])
			self.sendall("txt:"+str(len(self.CHAT_NAME))+":"+self.CHAT_NAME+msg[4:])
			return
		if (msg[:10]=="admin_req:"):
			print("Admin req:\t"+self.CHAT_NAME+"("+str(msg[10:]==ADMIN_PASSWD)+")")
			msg=msg[10:]
			if (msg==ADMIN_PASSWD):
				DATA_DICT[self.address]["rank"]="admin"
				self.sendMessage("rank:1:admin")
				return
			self.sendMessage("rank:0:admin:"+DATA_DICT[self.address]["rank"])
			return
		if (msg=="setup"):
			pid=1
			while True:
				self.CHAT_NAME="Person #%s"%(pid)
				pid+=1
				if (USED_NAMES.count(self.CHAT_NAME)==0):break
			USED_NAMES.append(self.CHAT_NAME)
			print("join:\t"+self.CHAT_NAME)
			DATA_DICT[self.address]={"address":self.address,"name":self.CHAT_NAME,"rank":"normal","socket":self}
			LIST_ADDR.append(self.address)
			self.sendall("join:"+self.CHAT_NAME)
			return
		if (msg[:4]=="chn:"):
			msg=msg[4:]
			if (len(msg)<3):
				print("Chn:\t"+self.CHAT_NAME+"-unsuccessfull (Too short)")
				self.sendMessage("chn:0:"+msg)
				return
			if (len(msg)>20):
				print("Chn:\t"+self.CHAT_NAME+"-unsuccessfull (Too long)")
				self.sendMessage("chn:1:"+msg)
				return
			if (USED_NAMES.count(msg)>0):
				print("Chn:\t"+self.CHAT_NAME+"-unsuccessfull (Already used)")
				self.sendMessage("chn:2:"+msg)
				return
			print("Chn:\t"+self.CHAT_NAME+"-successfull (Changed to:"+msg+")")
			self.sendMessage("chn:true:"+msg)
			USED_NAMES.remove(self.CHAT_NAME)
			self.CHAT_NAME=msg
			USED_NAMES.append(self.CHAT_NAME)
			DATA_DICT[self.address]["name"]=self.CHAT_NAME
			return
for i in range(0,50):
	ADMIN_PASSWD+=random.choice(list("""`1234567890-=qwertyuiop[]asdfghjkl;'zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?"""))# removed '\'
with open("./admin.txt","w") as f:f.write(ADMIN_PASSWD)
server=SimpleWebSocketServer("",8080,LWebSocketServer)
print("\nWebSocketServer has started on port 8080!\n")
server.serveforever()