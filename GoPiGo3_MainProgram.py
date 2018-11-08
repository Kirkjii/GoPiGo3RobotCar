import easygopigo3 as easy
from di_sensors.distance_sensor import DistanceSensor as distance
from di_sensors.light_color_sensor import LightColorSensor
from time import sleep
from random import randint
import MySQLdb
import serial
import syslog
import sys
import _thread
import threading as t
import os
import psutil
import logging

running = False
light_sensor = LightColorSensor()
dist = distance()
gpg = easy.EasyGoPiGo3()
gpg.stop()
servo = gpg.init_servo("SERVO1")
globalcounter = 0


#Database structure

#Robot1
#|game|
#|____| 
#|id  |
#|____|

#Robot2
#|game2|
#|_____|
#|id2  |
#|_____|

# Establish a connection to database
db = MySQLdb.connect("localhost", "monitor", "password", "robot")
curs = db.cursor()

# Remote control
remote = gpg.init_remote("AD2")

#^ = 1
#<- = 2
#ok = 3
#-> = 4
#v = 5

#1-9 = 6-14
#0 = 16

#* = 15
# = 17

# Serial communication (python <-> Arduino) configuration
port = '/dev/ttyACM0'
ard = serial.Serial(port, 9600, timeout=5)
sleep(2)


# Function to read sensor values from arduino and turn the robot accordingly
def readValues():
    value = "0"
    try:
        while True:
            value = str(ard.readline()).replace("b'", "").replace("\\r\\n'", "")
            if value == "1":
                gpg.turn_degrees(3)
                print(value)
            elif value == "2":
                gpg.turn_degrees(-3)
                print(value)
            elif value == "3":
                print(value)
                return False
    except:
        readValues()
        

# Measures the ambient light percentage
def measureLightPercentage():
    roundLight = light_sensor.get_raw_colors(delay=True)[3] * 100
    return roundLight

baseLightValue = measureLightPercentage()

# Returns the remote controller input
def remoteControl():
    try:
        value = remote.read()
        return value
    except:
        remoteControl()


# Checks if user has pressed the key "0" on remote controller
def checkRemote():
    while True:
        if remoteControl() == 16:
            global running
            running = False 
            print("running {}".format(running))
            servo.reset_servo()
            
# Function for manual driving with remote controller
def manualDrive():      
    while True:
        if remoteControl() == 1:
            gpg.forward()
        if remoteControl() == 2:
            gpg.left()
        if remoteControl() == 4:
            gpg.right()
        if remoteControl() == 5:
            gpg.backward()
        if remoteControl() == 17:
            break
        if remoteControl() == 0:
            gpg.stop()
        
# Checks if the light exceeds a certain threshold
def checkLight():
    if measureLightPercentage() > baseLightValue + 100:
        print(measureLightPercentage())
        curs.execute("INSERT INTO game VALUES(1)")
        db.commit()

# Polls the database for changes
def databaseQuery():
    value1 = curs.execute("SELECT id FROM game")
    db.commit()
    if value1 != 0:
        return True
    else:
        return False
        print("Liikaa valoa")

# Checks if possible to turn right
def measureRight():
    servo.rotate_servo(0)
    sleep(0.6)
    rightDistance = dist.read_range_single()
    print("right:" + str(rightDistance))
    
    if rightDistance >= 350:
        return True
    else:
        return False

# Checks if possible to go forward
def measureForward():
    servo.rotate_servo(90)
    sleep(0.2)
    forwardDistance = dist.read_range_single()
    print("forward:" + str(forwardDistance))
    
    if forwardDistance >= 350:
        return True
    else:
        if forwardDistance <= 50:
            gpg.stop()
            gpg.drive_cm(-35)
        return False

# Checks if possible to turn left
def measureLeft():
    servo.rotate_servo(177)
    sleep(0.2)
    LeftDistance = dist.read_range_single()
    
    if LeftDistance >= 350:
        return True
    else:
        return False

# Function for right turns and straightening
def turnRight():
    print("Turning right")
    servo.rotate_servo(2)
    gpg.drive_cm(20)    
    rightDistance = dist.read_range_single()
    print(rightDistance)
    
    if rightDistance > 100:    
        gpg.turn_degrees(90)
        gpg.drive_cm(40)    
        sleep(0.5)

        
        readValues()    #Straighten the robot

       
# Function for left turns and straightening
def turnLeft():
    print("turning left")
    gpg.drive_cm(20)
    servo.rotate_servo(177)
    leftDistance = dist.read_range_single()
    
    if leftDistance > 100:
        gpg.turn_degrees(-90)
        gpg.drive_cm(40)
        sleep(0.5)
        
        
        readValues()    #Straighten the robot

   

# directionIndication:
# [0] = right
# [1] = forward
# [2] = left

def mainProgram():
    measureLightPercentage()
    curs.execute("TRUNCATE game")       # Clears the game-table
    db.commit()
    servo.reset_servo()
    gpg.set_speed(130)
    directionIndication = [True, True, True]

    while True:
        if remoteControl() == 15:
            manualDrive()
        if remoteControl() == 17:
            global running
            running = True
            break

    while running == True:
        
        
        readValues()            # Align the robot with left-side wall
        databaseQuery()
        
        while databaseQuery() == True: #Checks if robot has been hit. If yes, then stop.    
            gpg.stop()
            databaseQuery()
        
        while databaseQuery() == False:
            while running == True:
                checkLight()


                # Check each direction and store the result into an array
                directionIndication[0] = measureRight()
                print("right: " + str(directionIndication[0]))
                directionIndication[1] = measureForward()
                print("forward: " + str(directionIndication[1]))
                directionIndication[2] = measureLeft()
                print("left: " + str(directionIndication[2]))
                distanceValue = dist.read_range_single()
                databaseQuery()
                
                 
                # If left and forward is blocked turn 90 degrees right        
                if directionIndication == [True, False, False]:
                    checkLight()
                    turnRight()
                    
                
                # if right and forward is blocked turn 90 degrees left
                if directionIndication == [False, False, True]:
                    checkLight()
                    turnLeft()
                  
                # If the way is blocked turn 180 degrees
              # if directionIndication == [False, False, False]:
               #     gpg.turn_degrees(180)
                
                # If left is blocked, but forward and right are open, randomize turn
                if directionIndication == [True, True, False]:         
                    randomTurn = randint(0,1)
                    print(randomTurn)
                    if randomTurn == 1:
                        print("Random right")
                        checkLight()
                        turnRight()
                    elif randomTurn == 0:
                        servo.rotate_servo(0)
                        sleep(0.3)
                        leftDirection = dist.read_range_single()
                        sleep(0.1)
                        
                        while leftDirection > 300:
                            checkLight()                        
                            servo.rotate_servo(90)
                            sleep(0.2)
                            forwardDirection = dist.read_range_single()
                            if forwardDirection < 350:
                                randomTurn = randint(0,1)
                                if randomTurn == 0:
                                    checkLight()
                                    gpg.turn_degrees(90.5)
                                    sleep(1)
                                    readValues()   #Straighten the robot
                                    checkLight()                                    
                                elif randomTurn == 1:
                                    gpg.turn_degrees(-90.5)
                                    sleep(1)
                                    readValues()    #Straighten the robot
                                   
                            servo.rotate_servo(0)
                            sleep(0.2)
                            leftDirection = dist.read_range_single()
                            checkLight()
                            gpg.forward()

                        
                # If right is blocked, but forward and left are open, randomize turn
                if directionIndication == [False, True, True]:
                    randomTurn = randint(0,1)
                    if randomTurn == 1:
                        print("Random Left")
                        turnLeft()
                    elif randomTurn == 0:
                        servo.rotate_servo(177)
                        sleep(0.2)
                        rightDirection = dist.read_range_single()
                        sleep(0.1)
                        while rightDirection > 350:
                            checkLight()
                            servo.rotate_servo(90)
                            sleep(0.2)
                            forwardDirection = dist.read_range_single()
                            servo.rotate_servo(177)   
                            if forwardDirection < 350:
                                randomTurn = randint(0,1)
                                if randomTurn == 0:
                                    checkLight()
                                    gpg.turn_degrees(90.5)                 
                                    readValues()    #Straighten the robot
                                    checkLight()
                                                                       
                                elif randomTurn == 1:
                                    gpg.turn_degrees(-90.5)
                                    readValues()    #Straighten the robot
                                    checkLight()
                            sleep(0.2)
                            rightDirection = dist.read_range_single()
                            gpg.forward()

                # If the robot faces a T-junction, randomize left or right turn
                if directionIndication == [True, False, True]:
                    randomTurn = randint(0,1)
                    if randomTurn == 1:
                        checkLight()
                        turnRight()
                    elif randomTurn == 0:
                        checkLight()
                        turnLeft()
                
                #If every direction is open, randomize turn
                if directionIndication == [True, True, True]:
                    randomTurn = randint(0,2)
                    if randomTurn == 0:
                        turnLeft()
                    if randomTurn == 1:
                        print("Go straight")
                        servo.rotate_servo(90)
                        sleep(0.2)
                        forwardDirection = dist.read_range_single()
                        #if running == False:
                            #mainProgram()
                            #break
                            
                        while forwardDirection > 400:
                            forwardDirection = dist.read_range_single()
                            print(forwardDirection)
                            gpg.forward()
                    if randomTurn == 2:
                        turnRight()
                checkLight()
                gpg.forward()
                
                if running == False:
                    gpg.stop()
                    print("Running false, ajetaan mp")
                    mainProgram()

print("asdadasasdasda2")
try:
    if __name__ == '__main__':
        
   
        remoteThread = t.Thread(target=checkRemote, name = "remoteThread", daemon = True).start()
        print("remoteThread kÃ¤ynnistetty")
        mainProgram()
        print("ajettu mainprogram")

except KeyboardInterrupt:
    
    servo.reset_servo()
    print("KBinterrupt")
    gpg.stop()

