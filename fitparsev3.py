from fitparse import FitFile
from datetime import timedelta
from influxdb import InfluxDBClient
import platform
import pytz

#TODO - Influx setup
client = InfluxDBClient(host='influxdb', port=8086) # Connect to the InfluxDB instance
client.drop_database('strava')      # Drop Old DB
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

        if power == None: power=0 # replace none with zero
        
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
                'fields': {'power': power}}

        dataPoints.append(data)
        
    print(f"{id} - Data Loaded - Writing to influx")
    client.write_points(dataPoints, database='strava')
    print(f"{id} Data written")

link = f"http://192.168.1.155:3000/d/qJnkG6cVk/new-dashboard?orgId=1&from={min_timestamp}&to={max_timestamp}"
link = f"http://192.168.1.4:3000/d/fit/fit-power-comparison?orgId=1&from={min_timestamp}&to={max_timestamp}"
print(link)