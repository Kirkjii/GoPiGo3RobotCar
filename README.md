# GoPiGo3RobotCar

For more information, see https://www.dexterindustries.com/gopigo3

![](https://user-images.githubusercontent.com/32328856/48061913-2332ad80-e1c9-11e8-929d-c55cc6a1d26d.jpg)

# Introduction 
A functioning GoPiGo3 robot that can navigate in certain environment on its own and react to changes in brightness. The robot also has two different driving-modes that can be altered via a remote controller.

# How does it work?

The robot consists of three main parts: GoPiGo3 board, Raspberry Pi3 and Arduino. GoPiGo3 board and Arduino Uno are attached to Raspberry Pi3. 
At the start you are able to choose the driving-mode. By pressing the “#” key on the remote controller the automatic mode is set. By pressing the “*” key manual mode is chosen.

**Manual drive**

After manual mode is chosen, the robot is drivable via arrow keys and speed can be decreased or increased with keys 1 and 2. Speed can be reset by pressing key 3. 

**Automatic drive**

By rotating the servo motor on front which has a distance sensor attached to it the robot collects a Boolean value into an array for every direction (left, right and forward) while simultaneously moving forward. For every index of the array True or False is stored, depending on the distance between the sensor and walls around it. For every combination of Boolean values there is a certain maneuver it can execute. Every corner and junction is noticed, as well as if every direction is open. 
The robot is constantly polling the input from the remote controller. This is done in another thread which allows real-time reaction to the input. By pressing the “0” key the main program stops its execution after finishing its current task and starts to wait for RC input.
After every turn the robot has the ability to straighten itself by aligning with the left-side wall. This is done by two ultrasonic sensors which are located on the rear-left and front-left. Both sensors measure the distance between the wall and the sensor. The robot is rotated to a direction depending on the values from the sensors. When the values are even straightening is done and the robot is ready to continue.

The robot also has light sensor attached to it. Once the sensor detects a change in brightness that exceeds a certain threshold, execution of the main program stops, and the robot starts to wait for RC input.
Automatic driving works best on a grid-shaped “play arena”. Example of the play arena below.

![](https://user-images.githubusercontent.com/32328856/48061915-2332ad80-e1c9-11e8-8425-e96517db8725.png)

# Hardware configuration
**Arduino Uno**

![](https://user-images.githubusercontent.com/32328856/48061918-23cb4400-e1c9-11e8-9b62-d5480382bc35.png)

**RaspBerry Pi3**
![](https://www.raspberrypi.org/app/uploads/2017/05/Raspberry-Pi-3-1-1619x1080.jpg)

**GoPiGo3 Board**
![](https://user-images.githubusercontent.com/32328856/48061911-229a1700-e1c9-11e8-8e11-e712ee7641e2.png)

# Flowchart
![](https://user-images.githubusercontent.com/32328856/48061916-2332ad80-e1c9-11e8-9046-b6c13d0377a6.png)

