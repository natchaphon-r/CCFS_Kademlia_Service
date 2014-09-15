import json
import hashlib
from flask import Flask, request
import threading
import twisted.internet.reactor as reactor
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
global global_result

def ls(obj):
	cprint("\n".join([x for x in dir(obj) if x[0] != "_"]))
def post(key,value):
	cprint("Mock post: %s : %s" % (key,value))
	
def get(key,event):
	global global_result
	cprint("in get function event.wait is" + str(event.isSet())) 
	global_result = "Mock global_result"
	event.set()
	if checkValid(key):
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

def makeKey(user_data):
	# HCID = Hash Content Identifier
	# HKID = Hash Key Identifier
	# Type : Purpose
	# Blob : Static; contains data
	# List : Static; exclusive map from next name segment to HID type
	# Commit : Versioned; exclusive map from HKID to HCID
	# Tag : Versioned; non-exclusive map from HKID to HID
	key = list()
	
	if user_data["type"] == "blob":
		key.append(json.dumps({"type":"blob","hcid":user_data["hcid"]}, sort_keys = True))
		#	key = json.dumps({"type":"blob","hcid":user_data["hcid"]}, sort_keys = True)
	elif user_data["type"] == "commit":
		key.append(json.dumps({"type":"blob","hcid":hashlib.sha256(str(user_data)).hexdigest()}, sort_keys = True))
		key.append(json.dumps({"type":"commit","hkid":user_data["hkid"]}, sort_keys = True))	
	elif user_data["type"] == "tag":
		key.append(json.dumps({"type":"blob","hcid":hashlib.sha256(str(user_data)).hexdigest()}, sort_keys = True))
		key.append(json.dumps({"type":"tag","hkid":user_data["hkid"],"namesegment":user_data["namesegment"]}, sort_keys = True))
	elif user_data["type"] == "key":
		key.append(json.dumps({"type":"blob","hcid":hashlib.sha256(str(user_data)).hexdigest()}, sort_keys = True))
		key.append(json.dumps({"type":"key","hkid":user_data["hkid"]}, sort_keys = True))
	else: 
		key = None
		cprint("Invalid Type")
	return key

def checkValid(values,data):

	trueblob = (str(values["type"]) ==  "blob") and ((hashlib.sha256(str(data)).hexdigest() == str(values["hcid"])))
	truecommit = (str(values["type"]) ==  "commit") and (len(values["hkid"]) == 256/4)
	truetag = (str(values["type"]) ==  "tag") and (len(values["hkid"]) == 256/4) and (len(values["namesegment"]) > 0)
	truekey = (str(values["type"]) ==  "key") and (len(values["hkid"]) == 256/4)
	
	if (trueblob or truecommit or truetag or truekey):
		return True
	else:
		return False

app = Flask(__name__)

@app.route('/',methods=['GET', 'POST'])
def getorpost():
	global global_result
	
	event = threading.Event()

	if request.method == 'POST':

		#if type(request.value) is list
		keys = makeKey(request.values)
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
		key = makeKey(request.values)
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
	app.run()
