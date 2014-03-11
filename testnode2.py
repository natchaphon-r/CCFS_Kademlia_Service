#!/usr/bin/env python
# Test Code

#python gui.py 4000 127.0.0.1 4000 --entangled-0.1
'''
create_network.py 10 127.0.0.1
python testnode1.py
python testnode2.py
'''
from flask import g, app
from subprocess import call
import entangled.node
import time
import pdb 
import threading
import twisted.internet.reactor as reactor
import twisted.internet.defer as defer
from twisted.internet import threads
import server as webserver
from twisted.web.server import NOT_DONE_YET
from twisted.internet.threads import blockingCallFromThread
from entangled.kademlia.datastore import SQLiteDataStore
import os
#global node1;node1 = 0; 
#global global_result;

def sleep(secs):
	d = defer.Deferred();
	reactor.callLater(secs,d.callback,None)
	return d;

def pub_completed(result):
	cprint(" Publish Completed : %s" % result);

def sea_completed(result):
	cprint(" Search Completed : %s" % result);
	
def error(result):
	cprint(" error : %s" %result);

def ls(obj):
	cprint("\n".join([x for x in dir(obj) if x[0] != "_"]));

def testpublishandretrieve(node_instance):
	node_instance.publishKey("Bagel","Cream Cheese");
	cprint(node_instance.searchKey("Bagel"));

def cprint(string):
	OKBLUE ='\033[94m'
	ENDC = '\033[0m'
	print "%s%s%s" % (OKBLUE,string,ENDC);

#----------------------------------------------------------	
class NODE:
	event = None;
	UDP = 4050; 
	DATA = None; 
	PEER = [("127.0.0.1",4060),("127.0.0.1",4001),("127.0.0.1",4002)];
	kademlia_node = None;
	def __init__(self):
		pass;
	def registerNode(self):

		self.kademlia_node = entangled.node.EntangledNode(udpPort=self.UDP, dataStore=self.DATA)
		commands = [];
		commands.append((self.kademlia_node.joinNetwork,[self.PEER],{}));
		commands.append((self.publishKey,[self.kademlia_node],{}));
		commands.append((self.searchKey,[self.kademlia_node],{}));
		threads.callMultipleInThread(commands);

	def publishKey(self,key,value):
		cprint("publishKey, key = %s , value = %s" % (key,value));
		df = self.kademlia_node.publishData(key,[value]);
		cprint("calling addCallback")
		df.addCallback(pub_completed);
		df.addErrback(error)
		reactor.callLater(2,self.searchKey,self.kademlia_node);
	
	def searchKey(self,key,event):
		self.event = event
		cprint("key = %s" % key);
		#print "%skey = %s%s" % (OKBLUE,key,ENDC);
		# '''
		# for i in range(1,2):
		# 	#p = self.kademlia_node.searchForKeywords([key]);
		# 	#p.addCallback(sea_completed);
		# 	#p.addErrback(error)
		# 	print "WAITING FOR DEFER !_!_!_!_"
		# 	wfd = defer.waitForDeferred(p)
		# 	print "PRINTING WFD !_!_!_!_!_!_"
		# 	print p.result
		# '''

		#found_key = blockingCallFromThread(reactor, self.kademlia_node.searchForKeywords.callRemote,[key]); 
		found_key = self.kademlia_node.searchForKeywords([key]);
		found_key.addCallback(self.event_completed)
		found_key.addErrback(error)
		#self.resultGenerator(key);
		#cprint("found_key = %s" % found_key);
		#print thing;

		#cprint("key = %s" % key);
		#call(["echo", "carrot"])
		return found_key;	
	def event_completed(self,result):
		#global global_result 
		webserver.global_result = result
		cprint("result in event_completed is %s" % str(result))
		cprint("calling self.event.set()")
		if self.event:
			self.event.set();
		else:
			print "event == none"
	
	@defer.inlineCallbacks
	def resultGenerator(self,key):

		deferred_thing = (yield self.kademlia_node.searchForKeywords([key]))
		cprint("thing is %s" % deferred_thing);
		#call(["echo", "carrot"])
		return 
		#thing = deferred_thing.getResult()
		#if thing != None:
			#will become the result of the Deferred
		#yield thing;
		#return
		#else:
			# will trigger an errback
		#	raise Exception('DESTROY ALL LIFE')			
'''
	def after_this_request(f):
		if not hasattr(g, 'after_request_callbacks'):
			g.after_request_callbacks = []
		g.after_request_callbacks.append(f)
		return f

	@app.after_request
	def call_after_request_callbacks(response):
		for callback in getattr(g, 'after_request_callbacks', ()):
			callback(response)
		return response
'''
#-----------------------------------------------------------
if __name__ == "__main__":
	node_instance = NODE();
	node_instance.registerNode();
	node_instance.publishKey('{"hcid": "ca4c4244cee2bd8b8a35feddcd0ba36d775d68637b7f0b4d2558728d0752a2a2", "type": "blob"}',["Testnode2 Published: Bagel"])
	cprint("publish done")
	
	webserver.start(getter = node_instance.searchKey,poster = node_instance.publishKey);
	#reactor.listenTCP(5000,site)
	print "starting reactor"
	reactor.run();
	print "after reactor"
