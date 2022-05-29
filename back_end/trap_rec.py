#python snmp trap receiver
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.entity.rfc3413 import ntfrcv
import socketio


oid_filter = ['1.3.6.1.2.1.1.3.0','1.3.6.1.6.3.1.1.4.1.0',
              '1.3.6.1.6.3.18.1.4.0','1.3.6.1.6.3.1.1.4.3.0',
              '1.3.6.1.2.1.1.5.0','1.3.6.1.4.1.232.11.2.11.1.0'
             ]
snmpEngine = engine.SnmpEngine()
sio = socketio.Client()
sio.connect('http://192.168.10.11:8000')

TrapAgentAddress='192.168.10.13'; #Trap listerner address
Port=162;  #trap listerner port

print("Agent is listening SNMP Trap on "+TrapAgentAddress+" , Port : " +str(Port));
print('--------------------------------------------------------------------------');
config.addTransport(
    snmpEngine,
    udp.domainName + (1,),
    udp.UdpTransport().openServerMode((TrapAgentAddress, Port))
)

#Configure community here
config.addV1System(snmpEngine, 'my-area', 'public')

def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
          varBinds, cbCtx):
    print("Received new Trap message");
    for name, val in varBinds:
        if name.prettyPrint() == '1.3.6.1.6.3.18.1.3.0':
           source_ip = val.prettyPrint()
        print(name.prettyPrint(),': ',val.prettyPrint())      
        if not name.prettyPrint() in oid_filter:
           event = val.prettyPrint()
    msg = f"Source IP: {source_ip}, Event: {event}"
    print(f"start emit {source_ip} {event}")
    sio.emit("getTrap", {"Trap":msg})  
        

ntfrcv.NotificationReceiver(snmpEngine, cbFun)

snmpEngine.transportDispatcher.jobStarted(1)  

try:
    snmpEngine.transportDispatcher.runDispatcher()
except:
    snmpEngine.transportDispatcher.closeDispatcher()
    raise

