#!/usr/bin/python
from dronekit import connect, Vehicle, VehicleMode, LocationGlobalRelative
import math
import time

IP_ADDR = '143.189.114.165'
DRONE_P1 = '5912'
DRONE_P2 = '5922'
DRONE_P3 = '5932'
DRONE_P4 = '5942'
DRONE_P5 = '5952'

TARGET_LAT = 35.806627
TARGET_LON = 139.085252

TARGET_LAT_S = 35.8065
TARGET_LON_S = 139.0852

TARGET_LAT_L = 35.8067
TARGET_LON_L = 139.0853

def SelectDrone():
    drones = [DRONE_P1, DRONE_P2, DRONE_P3, DRONE_P4, DRONE_P5]
    v_distances = {}

    for d in drones:
        vehicle = connect('tcp:' + IP_ADDR + ':' + d, wait_ready=True, timeout=60)
        while not vehicle.home_location:
            cmds = vehicle.commands
            cmds.download()
            cmds.wait_ready()

            if not vehicle.home_location:
                print("ホームロケーションを待っています…")
        
        v_lat = vehicle.home_location.lat
        v_lon = vehicle.home_location.lon

        print(d, ':', v_lat, ', ', v_lon)

        v_distance = math.sqrt((v_lat - TARGET_LAT)**2 + (v_lon - TARGET_LON)**2)
        #print(d, ':', v_distance)

        v_distances[d] = v_distance
        #print(v_distances)

        vehicle.close()

    v_distances = sorted(v_distances.items())

    print(v_distances[0])
    #print(v_distances)

    return(v_distances[0])

def flight(port):
    vehicle = connect('tcp:' + IP_ADDR + ':' + port, wait_ready=True, timeout=60)

    while not vehicle.is_armable:
        print("初期化中です")
        time.sleep(1)

    print("アームします")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("アームを待ってます")
        time.sleep(1)

    targetAltude = 300

    print("離陸！")
    vehicle.simple_takeoff(targetAltude)

    while True:
        print("高度:",vehicle.location.global_relative_frame.alt)

        if vehicle.location.global_relative_frame.alt >= targetAltude * 0.95:
            print("目標高度に到達しました")
            break

    time.sleep(1)

    ###############################################

    print("スピードを3に設定")
    vehicle.airspeed = 3

    print("Going towards first point for 30 seconds ...")
    point1 = LocationGlobalRelative(TARGET_LAT, TARGET_LON, targetAltude)
    vehicle.simple_goto(point1)

    # sleep so we can see the change in map
    # time.sleep(60)
    flight_flg = True

    # リスナー
    def location_callback(self, attr_name, value):
        print("Location (Global):", value)
        if ((value.lat >= TARGET_LAT_S and value.lat <= TARGET_LAT_L) and 
            (value.lon >= TARGET_LON_S and value.lon <= TARGET_LON_L)):
            flight_flg = False


    # コールバック関数「location_callback」を「global_frame」変更通知用に登録する
    vehicle.add_attribute_listener('location.global_frame', location_callback)

    while flight_flg:
        pass
    
    #print(vehicle.location.global_frame)
    vehicle.add_attribute_listener('location.global_frame', location_callback)
    print('到着!!:', vehicle.location.global_frame)

    time.sleep(10)

    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

# main
if __name__ == '__main__':
    d_p, d_d = SelectDrone()
    print(d_p)
    flight(d_p)