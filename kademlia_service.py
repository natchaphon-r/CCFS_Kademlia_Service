#!/usr/bin/env python
# Test Code

#python gui.py 4000 127.0.0.1 4000 --entangled-0.1
'''
create_network.py 10 127.0.0.1
python testnode1.py
python testnode2.py
'''
from flask import g, app,Flask
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
    PEER = [("localhost",4060),("localhost",4001),("localhost",4002)];
    kademlia_node = None;
    def __init__(self):
        pass;
    def registerNode(self):
        #cprint("CALLLLLLLLLLLLLLLLLLLLLLLLL")
        self.kademlia_node = entangled.node.EntangledNode(udpPort=self.UDP, dataStore=self.DATA)
        # commands = [];
        #cprint("")
        # commands.append((self.kademlia_node.joinNetwork,[self.PEER],{}));
        # commands.append((cprint,["echo commands echo"],{}));
        # commands.append((self.publishKey,[self.kademlia_node],{}));
        # commands.append((self.searchKey,[self.kademlia_node],{}));

        self.kademlia_node.joinNetwork(self.PEER)
        #call(["echo","commands echo"])
        #help(self.kademlia_node)
        #self.kademlia_node.printContacts();
        
        #cprint("added peers")
        
        #threads.callMultipleInThread(commands);


    def publishKey(self,key,value):
        cprint("[publishKey] key = %s , value = %s" % (key,value));
        #self.kademlia_node.printContacts();
        df = self.kademlia_node.publishData(key,[value]);
        #cprint("calling addCallback")
        df.addCallback(pub_completed);
        df.addErrback(error)
        #reactor.callLater(2,self.searchKey,self.kademlia_node,);
    
    def searchKey(self,key,event):
        cprint("[searchKey] key = %s" % key);
        self.event = event
        #self.kademlia_node.printContacts();
        
        #print "%skey = %s%s" % (OKBLUE,key,ENDC);
        # '''
        # for i in range(1,2):
        #   #p = self.kademlia_node.searchForKeywords([key]);
        #   #p.addCallback(sea_completed);
        #   #p.addErrback(error)
        #   print "WAITING FOR DEFER !_!_!_!_"
        #   wfd = defer.waitForDeferred(p)
        #   print "PRINTING WFD !_!_!_!_!_!_"
        #   print p.result
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
        #cprint("result in event_completed is %s" % str(result))
        #cprint("calling self.event.set()")
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
        #   raise Exception('DESTROY ALL LIFE')         
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
    #call(["clear"])
    #help(app)
    node_instance = NODE();
    #node_instance2 = NODE();
    #print node_instance.PEER
    #node_instance.entangled.node.printContact()
    node_instance.registerNode();
    #reactor.callLater(0.01,cprint,"CALLLLLLL LATTTEERRRRRRRR");
    #node_instance.publishKey('{"hcid": "ca4c4244cee2bd8b8a35feddcd0ba36d775d68637b7f0b4d2558728d0752a2a2", "type": "blob"}',["Testnode2 Published: Bagel"])
    #node_instance.publishKey('{"hkid": "6dedf7e580671bd90bc9d1f735c75a4f3692b697f8979a147e8edd64fab56e85", "type": "commit"}',["Testnode2 Published: Cream Cheese"])
    #node_instance.publishKey('{"hkid": "0f63f06c4c9802cf3b7628bcbfb9008326e3d37e886cbbd361f7bb8a45782bb4", "namesegment": "testBlob", "type": "tag"}',["Testnode2 Published: Salmon"])
    #node_instance.publishKey('{"hkid": "0f63f06c4c9802cf3b7628bcbfb9008326e3d37e886cbbd361f7bb8a45782bb4", "type": "key"}',["Testnode2 Published: Onion/Tomato"])
    #cprint("publish done")
    #ls(reactor)
    #cprint(str(reactor.running))
    #reactor.startRunning();
    #cprint(str(reactor.running))

    #ls(reactor)
    #cprint('got to the new part')
    


    webserver.start(getter = node_instance.searchKey,poster = node_instance.publishKey);
    #cprint("REACTORRRRRRRRRRRRRR PLEASE RUNNNNNN")
    
    #reactor.listenTCP(5000,site)
    #cprint("before Calling Thread")
    #thread_object = threading.Thread(group=None, target = webserver.start, name=None, args=(), kwargs={"getter" : node_instance.searchKey,"poster" : node_instance.publishKey})
    
    #thread_object.start()
    #cpring("between thread_object and reactor.run")
    
    #print "after reactor"
