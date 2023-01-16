from fitparse import FitFile
from datetime import timedelta
from influxdb import InfluxDBClient
import os, time,subprocess, sys

# wait 5 second as the DB maybe not be up yet. 
time.sleep(2)

from dotenv import load_dotenv
load_dotenv()

# Load Enviroment
DEV = os.getenv('FIT_MODE')
INFLUX_HOST = os.getenv('INFLUX_HOST'+DEV)
GRAFANA_URL = os.getenv('GRAFANA_URL'+DEV)

# def print(string):
#     sys.stdout.write(f"{string}\n")


print("Running in Mode: " + DEV, flush=True)
print("Connection to infuxdb: " + str(INFLUX_HOST), flush=True)


notConnected = False
maxRetiries = 10
count=1
while notConnected is False:

    try:
        #TODO - Influx setup
        client = InfluxDBClient(host=INFLUX_HOST, port=8086) # Connect to the InfluxDB instance

        health = client.health()
        if health.status == "pass":
            print("Connection success.", flush=True)
            notConnected = True
        
        
    except :
        print(f"********** Connection failure: retrying {count} of max {maxRetiries}", flush=True)

        count+=1
        time.sleep(2)

        if count >= maxRetiries:
           exit(0)

print(f"Dropping DB Strava", flush=True)
# client.drop_database('strava')      # Drop Old DB

print(f"Creating DB Strava", flush=True)
client.create_database('strava')    # Create DB

# create list of fitFiles
files = {"quarq":FitFile('fitFiles/FTP-Quarq.fit'), "kickr":FitFile('fitFiles/FTP-Kickr.fit'),  "assioma": FitFile('fitFiles/FTP-Assioma.fit')}

grafana_link = ""
min_timestamp =0
max_timestamp =0

#Loop through file
for id in files: 
    file = files[id]

    print(f"Processing file {id}")
    
    # Iterate through all the data messages in the file
    dataPoints=[]
    for record in file.get_messages("record"):
        
        power = record.get_value('power') # Get the power data
        cad = record.get_value('cadence') # Get the power data

        if power == None: power=0 # replace none with zero
        if cad == None:cad = 0
        
        timestamp = record.get_value('timestamp') # Get the timestamp
        # utc = timestamp  + timedelta(hours=1)
        
        epoch = int(timestamp.timestamp()*1000)
        
        # print(epoch)
        if min_timestamp == 0: min_timestamp = epoch
        if epoch < min_timestamp : min_timestamp = epoch
        if epoch > max_timestamp: max_timestamp = epoch

       
        # record.get_value('timestamp').
        
        #make some minor adjustments to timestamps
        # 
        # if id=="assioma": timestamp = timestamp  - timedelta(seconds=4)
        
        #build the data point to write
        data = {'measurement': 'strava',
                'time': timestamp,
                'tags': { 'powerMeter': id},
                 'fields':   {'power': power, 'cadence':cad}
                }

        dataPoints.append(data)
        
    print(f"{id} - Data Loaded - Writing to influx")
    client.write_points(dataPoints, database='strava')
    print(f"{id} Data written")

GRAFANA_URL=GRAFANA_URL.replace("{min}", str(min_timestamp))
GRAFANA_URL=GRAFANA_URL.replace("{max}", str(max_timestamp))
print(GRAFANA_URL)