import ecdsa
import json
import hashlib
import os
from flask import Flask, request
import threading
import twisted.internet.reactor as reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
global global_result

def deleteBadKey(key):
	# Not yet implemented
	pass

def verifyECDSA(payload,sig,key_string):
	vk = ecdsa.VerifyingKey.from_string(key_string[1:], curve=ecdsa.NIST521p)
	tocheck = hashlib.sha256(payload).digest()

	sig = sig.decode('hex')
	assert sig[0] == '\x04'
	sig = sig[1:]

	try:
	    vk.verify(sig,payload, hashfunc=hashlib.sha256) #last element , extract everything except from the last element
	    print "Good data"
	    return True
	except ecdsa.BadSignatureError:
	    print "Bad data"
	    return False


def ls(obj):
	cprint("\n".join([x for x in dir(obj) if x[0] != "_"]))

def post(key,value):
	cprint("Mock post: %s : %s" % (key,value))
	
def get(key,event):
	global global_result
	cprint("in get function event.wait is" + str(event.isSet())) 
	global_result = "Mock global_result"
	event.set()
	if checkValid(key,None):
		return "Mock Data"
	else:
		return "Error: Invalid Request"

	
def start(getter,poster,web_port):
	global get
	global post

	get = getter
	post = poster
	port = web_port

	app.debug = True
	resource = WSGIResource(reactor, reactor.getThreadPool(), app)
	site = Site(resource)
	reactor.listenTCP(port, site)

	reactor.run()

def cprint(string):
	OKGREEN = '\033[92m'
	ENDC = '\033[0m'
	print "%s%s%s" % (OKGREEN,string,ENDC)

def makeKey(user_value, user_data):
	#JSON Object as a key

	# HCID = Hash Content Identifier
	# HKID = Hash Key Identifier
	# Type : Purpose
	# Blob : Static; contains data
	# List : Static; exclusive map from next name segment to HID type
	# Commit : Versioned; exclusive map from HKID to HCID
	# Tag : Versioned; non-exclusive map from HKID to HID
	
	key = list()
	
	if user_value["type"] == "blob":
		key.append(json.dumps({"type":"blob","hcid":user_value["hcid"]}, sort_keys = True))
		#	key = json.dumps({"type":"blob","hcid":user_data["hcid"]}, sort_keys = True)
	elif user_value["type"] == "commit": # verify before post/respond data
		key.append(json.dumps({"type":"blob","hcid":hashlib.sha256(str(user_data)).hexdigest()}, sort_keys = True))
		key.append(json.dumps({"type":"commit","hkid":user_value["hkid"]}, sort_keys = True))	
	elif user_value["type"] == "tag": # verify before post/respond data
		key.append(json.dumps({"type":"blob","hcid":hashlib.sha256(str(user_data)).hexdigest()}, sort_keys = True))
		key.append(json.dumps({"type":"tag","hkid":user_value["hkid"],"namesegment":user_data["namesegment"]}, sort_keys = True))
	elif user_value["type"] == "key":
		key.append(json.dumps({"type":"blob","hcid":hashlib.sha256(str(user_data)).hexdigest()}, sort_keys = True))
		key.append(json.dumps({"type":"key","hkid":user_value["hkid"]}, sort_keys = True))
	else: 
		key = None
		cprint("Invalid Type")
	return key

def verifyblob(hkid,data):
	return hashlib.sha256(str(data)).hexdigest() == data

def verifytagcommit(hkid,data):
	if len(values["hkid"]) != (256/4):
		return False

	payload, sig = data.rsplit(',\n', 1)
	_, obHKID = payload.rsplit(',\n',1)

	if obHKID != hkid: 
		return False

	event = threading.Event()
	retrievedKey = json.dumps({"type":"blob","hcid":user_value["hcid"]}, sort_keys = True)
	thread_object = threading.Thread(group=None, target = get, name=None, args=(retrievedKey,event), kwargs={})
	thread_object.start()

	if event.wait():
		if (len(global_result) > 0):
			data_string = global_result[0]
		else:
			return(str(global_result))
	else:
		cprint("Fail... Time out")
	return verifyECDSA(payload,sig,data_string)

def checkValid(values,data):
	if str(values["type"]) ==  "blob":
		return verifyblob(values["hcid"],data)

	if (str(values["type"]) ==  "commit") or (str(values["type"]) ==  "tag"):
		return verifytagcommit(values["hkid"],data)

	if (str(values["type"]) ==  "key") and (len(values["hkid"]) == 256/4):
		return True 

	return False

#################################	
app = Flask(__name__)
@app.route('/test',methods=['GET'])
def testSign():
	MSG = "Hello World"
	

	#Create signing key
	sk = ecdsa.SigningKey.generate(ecdsa.NIST256p)
	#Create verifying key
	vk = sk.get_verifying_key()
	topost = MSG+","+vk.to_pem()+","+sk.sign(MSG).encode("hex")
	# post("storage_key",topost)
	# #################################################
	# event = threading.Event()
	# thread_object = threading.Thread(group=None, target = get, name=None, args=("storage_key",event), kwargs={})
	# thread_object.start()

	# #if event.wait(2):
	# return "TestSign" + global_result
	# return "Time-out occured"
	# #################################################
	#got = topost.split(',')
	got = topost.split(',')
	msg_tocheck = got[0]
	try:
		vk.verify(got[2].decode("hex"),msg_tocheck)
		return("Good Message: " + got[0])
	except ecdsa.BadSignatureError:
		return("Bad signature")

@app.route('/',methods=['GET', 'POST'])
def getorpost():
	global global_result
	
	event = threading.Event()

	if request.method == 'POST':

		#if type(request.value) is list
		keys = makeKey(request.values,request.data)
		#key = makeKeyList(request.values)
		data = request.data

		if checkValid(request.values,request.data):
			for key in keys:
				post(key,data)
				return "key is valid:\n %s" % key
		else: 
			return "Invalid Input: \n %s" % key

	elif request.method == 'GET':
		global_result = None
		key = makeKey(request.values,None)
		#key = makeKeyList(request.values)

		thread_object = threading.Thread(group=None, target = get, name=None, args=(key,event), kwargs={})
		thread_object.start()

		if event.wait():
			if (len(global_result) > 0):

				return global_result[0]
			else:
				return(str(global_result))

		else:
			cprint("Fail... Time out")

		return "Time-out occured"

if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')
