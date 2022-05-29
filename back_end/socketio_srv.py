import socketio
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from pytz import timezone

# create a Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*", logger=True, engineio_logger=True)
app = socketio.ASGIApp(sio,  static_files = {
     '/': './templates/',
  })

bucket = "datastore"
org = "mib"
token = "my token string"
# Store the URL of your InfluxDB instance
url="http://localhost:8086"
client = influxdb_client.InfluxDBClient(url="http://localhost:8086", token=token, org=org)

def habdle_th():
   temperature_time = []
   humidity_time = []
   temperature_value = []
   humidity_value = []
   query_temperature = '''from(bucket: "datastore") |> range(start: -12h)
          |> filter(fn: (r) => r._measurement == "my_measurement" and r._field == "temperature")
          |> window(every: 2m)
          |> mean()
		'''
   query_humidity = '''from(bucket: "datastore") |> range(start: -12h)
          |> filter(fn: (r) => r._measurement == "my_measurement" and r._field == "humidity")
          |> window(every: 2m)
          |> mean()
		'''
   tables_temperature = client.query_api().query(query_temperature, org=org)
   for table in tables_temperature:
      for record in table.records:
         tt = record.values.get('_stop').astimezone(timezone('Asia/Taipei'))
         temperature_time.append(tt.strftime("%H:%M:%S"))
         temperature_value.append(record.values.get('_value'))
         
   tables_humidity = client.query_api().query(query_humidity, org=org)
   for table in tables_humidity:
      for record in table.records:
         ht = record.values.get('_stop').astimezone(timezone('Asia/Taipei'))
         humidity_time.append(ht.strftime("%H:%M:%S"))
         humidity_value.append(record.values.get('_value'))
         
   th_history = {'t_time':temperature_time, 't_value':temperature_value, 
                 'h_time':humidity_time, 'h_value':humidity_value}
   return th_history

@sio.event
async def connect(sid, environ):
    print(sid, 'connected ')
    await sio.emit('response', "from connect")

@sio.event
def disconnect(sid):
    print(sid, 'disconected')

@sio.event
async def thHistory(sid): 
    th_history = habdle_th()
    print(th_history)    
    await sio.emit('th_history', th_history)

@sio.event
async def getTrap(sid, data):
    print('message: ', data)
    await sio.emit('message', data['Trap'])

@sio.event
async def getHT(sid, data):
    print(f"t is {data.get('t')}")
    print(f"h is {data.get('h')}")
    await sio.emit('th_value', {'t':round(data.get('t'),2),'h':data.get('h')})
    client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("my_measurement").tag(
        "location", "KH_Office").field("temperature", round(data.get('t'),2)
        ).field("humidity", data.get('h'))
    write_api.write(bucket=bucket, org=org, record=p)
    if data.get('t') > 30:
       await sio.emit('fan', 'High')
    if data.get('t') <= 30:
       await sio.emit('fan', 'Low')
       
