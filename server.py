import json
import hashlib
from flask import g , app, Flask, request
import time
import threading
import twisted.internet.reactor as reactor
import traceback
# #-------------------------------------------------------------------------------
# def f(depth = 0):
# 	print depth, traceback.print_stack();
# 	if depth < 2:
# 		f(depth+1)
global global_result;

def ls(obj):
	cprint("\n".join([x for x in dir(obj) if x[0] != "_"]));
def post(key,value):
	#event.set()
	cprint("Mock post: %s : %s" % (key,value));
	
def get(key,event):
	global global_result;
	cprint("in get function event.wait is" + str(event.isSet())) 
	cprint("Mock get: %s" % (key));
	global_result = "This is a mock global_result"
	cprint("in get %s " % global_result)
	event.set()
	return "this is a mock, haha you just got mocked"
	
def start(getter,poster):
	global get;
	global post;
	get = getter; post = poster;
	#app.debug = True
	app.run(host= '0.0.0.0',port =5001,debug = True);

def cprint(string):
	OKGREEN = '\033[92m'
	ENDC = '\033[0m'
	print "%s%s%s" % (OKGREEN,string,ENDC);


def makeKey(user_data):
	# HCID = Hash Content Identifier
	# HKID = Hash Key Identifier
	#print "TYPPEEEEEE = %s" % user_data["type"]
	# Type : Purpose
	# Blob : Static; contains data
	# List : Static; exclusive map from next name segment to HID type
	# Commit : Versioned; exclusive map from HKID to HCID
	# Tag : Versioned; non-exclusive map from HKID to HID

	if user_data["type"] == "blob":
		key = json.dumps({"type":"blob","hcid":user_data["hcid"]}, sort_keys = True)
	elif user_data["type"] == "commit":
		key = json.dumps({"type":"commit","hkid":user_data["hkid"]}, sort_keys = True)	
	elif user_data["type"] == "tag":
		key = json.dumps({"type":"tag","hkid":user_data["hkid"],"namesegment":user_data["namesegment"]}, sort_keys = True)
	elif user_data["type"] == "key":
		key = json.dumps({"type":"key","hkid":user_data["hkid"]}, sort_keys = True)
	else: 
		key = None
		cprint("Invalid Type");	
	return key

def checkValid():
	user_data = web.input();

	cprint(web.data());
	if (str(user_data["type"]) ==  "blob") and ((hashlib.sha256(str(web.data())).hexdigest() == str(user_data["hcid"]))):
		return True;
	else:
		return False;

app = Flask(__name__)

@app.route('/',methods=['GET', 'POST'])
def getorpost():
	global global_result;
	cprint("WE ARE HERE!")

	event = threading.Event()
	cprint(str(request.method))
	#help(event)
	#event = None
	if request.method == 'POST':
		key = makeKey(request.values[0]);
		data = web.data(); # validate data with hashes
		return checkValid()

		if checkValid():
			post(key,data,event);
			return key
		else: 
			print "Invalid Input";
	elif request.method == 'GET':
		#global global_result
		global_result = None;
		key = makeKey(request.values);
		cprint("PASS MAKEKEY %s" % str(key))
		#help(reactor)
		thread_object = threading.Thread(group=None, target = get, name=None, args=(key,event), kwargs={})
		thread_object.start()
		#data = reactor.callInThread(get,[key,event],{})#reactCaget(key,event)
		#data = get(key,event)
		#cprint("The data is %s" % str(data))
		#time.sleep(1);
		#print "printing from server %s" % data.callback()
		#f()
		#help(event)
		cprint("got to wait")
		cprint("The value of event.wait is " + str(event.isSet()))
		#event.set()
		if event.wait():
			cprint("Result returned")
			cprint("global result = %s" % global_result)	
			return str(global_result);	
		else:
			cprint("Fail... Time out")
		cprint("got through wait")

		return "got to the end of get"
if __name__ == "__main__":
	app.debug = True
	app.run();
