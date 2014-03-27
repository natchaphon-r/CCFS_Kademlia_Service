#!/usr/bin/env python

#python gui.py 4000 127.0.0.1 4000 --entangled-0.1
'''
create_network.py 10 127.0.0.1
python testnode1.py
python testnode2.py
'''
import entangled.node
import server as webserver
from subprocess import call
import sys
import twisted.internet.defer as defer
import twisted.internet.reactor as reactor

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
def errprint(string):
	OKRED ='\033[31m'
	ENDC = '\033[0m'
	print "%s%s%s" % (OKRED,string,ENDC);

class NODE:
	event = None;
	DATA = None; 
	kademlia_node = None;

	def __init__(self,KADEMLIA_PORT = 4050,PEER = [("localhost",4060),("localhost",4001),("localhost",4002)]):
		self.UDP = KADEMLIA_PORT;
		self.PEER = PEER;

	def registerNode(self):
		self.kademlia_node = entangled.node.EntangledNode(udpPort=self.UDP, dataStore=self.DATA)
		self.kademlia_node.joinNetwork(self.PEER)

	def publishKey(self,key,value):
		cprint("[publishKey] key = %s , value = %s" % (key,value));
		df = self.kademlia_node.publishData(key,[value]);
		df.addCallback(pub_completed);
		df.addErrback(error)
	
	def searchKey(self,key,event):
		cprint("[searchKey] key = %s" % key);
		self.event = event

		found_key = self.kademlia_node.searchForKeywords([key]);
		found_key.addCallback(self.event_completed)
		found_key.addErrback(error)
		return found_key;	

	def event_completed(self,result):
		webserver.global_result = result

		if self.event:
			self.event.set();
		else:
			print "event == none"
	
	@defer.inlineCallbacks
	def resultGenerator(self,key):

		deferred_thing = (yield self.kademlia_node.searchForKeywords([key]))
		cprint("thing is %s" % deferred_thing);
		return 

def main():
	if len(sys.argv) < 3:
		errprint('Usage:\n%s WEB_PORT  KADEMLIA_PORT {[KNOWN_NODE_IP KNOWN_NODE_PORT] or FILE}' % sys.argv[0])
		sys.exit(1)		 
	try:
		int(sys.argv[1])
	except ValueError:
		errprint('\nWEB_PORT must be an integer.\n')
		errprint('Usage:\n%s WEB_PORT  KADEMLIA_PORT {[KNOWN_NODE_IP KNOWN_NODE_PORT] or FILE}' % sys.argv[0])
		sys.exit(1)
	try:
		int(sys.argv[2])
	except ValueError:
		errprint('\nKADEMLIA_PORT must be an integer.\n')
		errprint('Usage:\n%s WEB_PORT  KADEMLIA_PORT {[KNOWN_NODE_IP KNOWN_NODE_PORT] or FILE}' % sys.argv[0])
		sys.exit(1)

	if len(sys.argv) == 5:
		PEER = [(sys.argv[3], int(sys.argv[4]))]
	elif len(sys.argv) == 4:
		PEER = []
		f = open(sys.argv[3],'r')
		lines = f.readlines()
		f.close()
		for line in lines:
			peer_ip,peer_udp = line.split()
			PEER.append((peer_ip,int(peer_udp)))
	else:
		PEER = None;

	cprint('PEER is %s' % str(PEER))
	node_instance = NODE(KADEMLIA_PORT = int(sys.argv[2]),PEER = PEER);
	node_instance.registerNode();
	webserver.start(getter = node_instance.searchKey,poster = node_instance.publishKey,web_port = int(sys.argv[1]));

if __name__ == "__main__":
	main();
