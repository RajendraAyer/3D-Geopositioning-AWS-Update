try:
    import os
    import sys
    import datetime
    import pymap3d as pm
    import math
    import time
    import boto3
    from gpiozero import DistanceSensor
    from time import sleep
    import threading

    print("All Modules Loaded ...... ")

except Exception as e:
    print("Error {}".format(e))

class MyDb(object):

    def __init__(self, Table_Name='3DGeoposition'):
        self.Table_Name = Table_Name
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(Table_Name)
        self.client = boto3.client('dynamodb')

    @property
    def get(self):
        response = self.table.get_item(
            Key={
                'SensorRead_ID': "1"
            }
        )

        return response

    def put(self, SensorRead_ID='', Snodeposition='', Droneposition='', Obsposition='', Distance=''):
        self.table.put_item(
            Item={
                'SensorRead_ID': SensorRead_ID,
                'SensorNode_Position': Snodeposition,
                'Drone_Position': Droneposition,
                'Obstacle_Position': Obsposition,
                'Distance between Drone and Obstacle': Distance
            }
        )

    def delete(self, SensorRead_ID=''):
        self.table.delete_item(
            Key={
                'SensorRead_ID': SensorRead_ID
            }
        )

    def describe_table(self):
        response = self.client.describe_table(
            TableName='3DGeoposition'
        )
        return response

def snodeposition():
    lat0 = -33.88894  # deg
    lon0 = 151.12768  # deg
    alt0 = 1  # meters
    snodepos=[lat0, lon0,alt0]
    return snodepos

def droneposition():
    lat1 = -33.88891  # deg
    lon1 = 151.12768  # deg
    alt1 = 1  # meters
    dronepos=[lat1, lon1, alt1]
    return dronepos

def obstacleposition():
    sensor = DistanceSensor(echo=18, trigger=17)
    while True:
    # Object position detected by Radar
        Dist = sensor.distance * 100
        angle = 90
        x1 = Dist * math.cos(math.radians(90 - angle))
        z1 = Dist * math.sin(math.radians(90 - angle))
        y1 = Dist * math.sin(math.radians(0))
        sleep(1)
        obspos=[x1, y1, z1]
        return obspos
    
def geoposition():
    print("Start")
    # The local coordinate origin(Point where Ultrasonic radar is placed)
    lat0 = -33.88894  # deg
    lon0 = 151.12768  # deg
    alt0 = 1  # meters
    # Drone Position
    lat1 = -33.88891  # deg
    lon1 = 151.12768  # deg
    alt1 = 1  # meters

    # Drone Local Position with relative to Sensor Node
    x = pm.geodetic2enu(lat1, lon1, alt1, lat0, lon0, alt0)
    sleep(1)
    sensor = DistanceSensor(echo=18, trigger=17)
    while True:
        # Object position detected by Radar
        Dist = sensor.distance * 100
        angle = 90
        X = Dist * math.cos(math.radians(90 - angle))
        Z = Dist * math.sin(math.radians(90 - angle))
        Y = Dist * math.sin(math.radians(0))
        sleep(1)
        # Relative Position and Distance Calculation
        (x1, y1, z1) = x
        dist = math.sqrt((x1 - X) ** 2 + (y1 - Y) ** 2 + (z1 - Z) ** 2)
        sleep(1)
        return dist

def main():
    global counter
    threading.Timer(interval=10, function=main).start()
    obj = MyDb()
    Snodeposition = snodeposition()
    Droneposition = droneposition()
    Obsposition = obstacleposition()
    Distance = geoposition()
    obj.put(SensorRead_ID=str(counter), Snodeposition=str(Snodeposition), Droneposition=str(Droneposition),
            Obsposition=str(Obsposition), Distance=str(Distance))
    counter = counter + 1
    print("Uploaded on Cloud")

if __name__ == "__main__":
    global counter
    counter = 0
    main()
