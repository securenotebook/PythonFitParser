from fitparse import FitFile
from datetime import timedelta
from influxdb import InfluxDBClient
import os, time,subprocess, sys
import ipcalc
from rich import inspect

def log(string):
    print(string, flush=True)

from dotenv import load_dotenv
log("Loading Enviroment variables forom .env")
load_dotenv()

DEV         = os.getenv('FIT_MODE')
INFLUX_HOST = os.getenv('INFLUX_HOST'+DEV)
GRAFANA_URL = os.getenv('GRAFANA_URL'+DEV)
DROP        = os.getenv('DROP_DB')
DATABASE    = os.getenv('DATABASE_NAME')

log(f"Running in Mode: {DEV}")
log(f"Using infuxdb: {INFLUX_HOST}")


def getInfluxConnection():
    # Load Enviroment
    
    retryAmount = 5
    sleep=2
    count=1
    while True:
        time.sleep(sleep)

        if count == retryAmount:
            return False

        try:
            
            log(f"Connecting to {INFLUX_HOST}")
            client = InfluxDBClient(host=INFLUX_HOST, port=8086) 

            client.ping() #Will throw exception if not valid

            log(f"Connected to DB {DATABASE} on host {INFLUX_HOST}")

            #Drop and recreate DB
            if DROP == 'True':
                log(f"Dropping DB {DATABASE}")
                client.drop_database(DATABASE)    
                log(f"Creating DB {DATABASE}")
                client.create_database(DATABASE)  

            dbs = client.get_list_database()

            foundDb = False
            log(f"Verify DB {DATABASE} exists on host {INFLUX_HOST}")
            for db in dbs:
                if db['name'] == DATABASE:
                    log(f"DB {DATABASE} found")
                    foundDb = True
                    continue
            
            #create DB if not exising
            if foundDb == False:
                log(f"DB {DATABASE} not found on host {INFLUX_HOST}")
                log(f"Creating DB {DATABASE}")
                client.create_database(DATABASE)  
            
            return client

        except Exception as e:
            log(f"Connection to {INFLUX_HOST} Failed, retrying in {sleep} seconds. [{count} of {retryAmount}]")
            log(f"Error: [{e}]")
            count+=1