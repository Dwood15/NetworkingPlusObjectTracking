''' Part of Dason Woodhouse's ECEN 361 project
	-- Part of the goal of this was to do object
	tracking, and upon finding a lackluster quality
	in the solutions available (Kinect, LeapMotion, etc)
	I chose to implement my own.
	
	--This requires OPENCV 3.1, and was built with
	Python 3 in mind. For the Raspberry Pi you will need
	to build your own copy of OpenCV, as there isn't one
	available from pip. This takes approx. 10 hours on a
	Pi 2b.
	
	--The first thing you're going to want to do is disable
	the networking or implement your own. That part is left
	in for reference if you're curious.
	
	--This comes with No Warranty, express or implied.
	
	--You'll find that the Python bindings available are 
	NOT 1 - to - 1, and I could find only the generally
	available tutorials and StackOverflow as help with some
	of my problems.
	
	--If you use this code, let me know! I'm interested in
	seeing if others find it useful.
'''


import numpy as np
import picamera.array
import picamera
import cv2
import time 
import socket


'''Utility Functions'''
def getLowArray():

	#just some defaults
	low_h = 0
	low_s = 0
	low_v = 0
	
	#All but blue
	tissue_low_h = 75
	tissue_low_s = 0
	tissue_low_v = 66
	
	#Red
	red_low_h = 57
	red_low_s = 129
	red_low_v = 105

	return np.array([red_low_h, red_low_s, red_low_v])

	'''
		-Todo: Get a more dynamic approach going. Wasn't needed, so just have some stuff
	'''
def getHiArray():
	high_h = 255
	high_s = 255
	high_v = 255

	#All but blue
	tissue_high_h = 141
	tissue_high_s = 14
	tissue_high_v = 258

	#All but a specific RED object.
	red_high_h = 270
	red_high_s = 216
	red_high_v = 258

	return np.array([red_high_h, red_high_s, red_high_v])
	
	'''Utility function for determining the current filtered range of colors'''
def printData(low_h, low_s, low_v, high_h, high_s, high_v):
	print(str.format('low h: {0} high h: {1}', low_h, high_h))
	print(str.format('low s: {0} high s: {1}', low_s, high_s))
	print(str.format('low v: {0} high v: {1}\n', low_v, high_v))

'''Utility Camera Functions
	- These were for getting 3-Dimensional depth from the camera.
	- Turns out object tracking is hard.
	'''
def getMaxCamWidth(distFromCamera):
	si = np.sin(31.1 * np.pi / 180) #Get it in radians
	return 2 * (si * distFromCamera)

def getMaxCamHeight(distFromCamera):
	si = np.sin(24.4 * np.pi / 180)
	return 2 * (si * distFromCamera)

	'''Knowing the number of pixels an object takes up and the number of inches it 
		actually IS, we approximate distance from camera.
	'''
def getPixPerInch(inch, pix):	
	return inch / pix
	
'''Uses 6 feet as baseline distance, or 72 inches'''
def getExpectedPixelsOfObject(objDimInches):
	pass
	
'''Just passing the total height of the resolution and object in pix is what is expected'''
def getPercentageObjectIsTakingUp(resolution, objectPixDim):
	xPercent = objectPixDim[0] / resolution[0]
	yPercent = objectPixDim[1] / resolution[1]
	return (xPercent, yPercent)

def getObjectDistanceFromCamera(knownObjectDims, resolution, detectedObjPix):
	percDetected = getPercentageObjectIsTakingUp(resolution, detectedObjPix)
	#Todo: Based on the percentage of pixels taken up from the object, we can get
	#its approximate distance from the camera, knowing how large the object already is
	#And how many pixels it should take up from an arbitrary distance.
	
'''Useful for finding good range of values for HSV filtering '''
def checkKeys(key, current_low, current_high):
		low_h = current_low[0]
		low_s = current_low[1]
		low_v = current_low[2]
		
		high_h = current_high[0]
		high_s = current_high[1]
		high_v = current_high[2]

		if(key == ord('p')):
			if(low_h < (high_h - 1)):
				low_h += 3
		elif(key == ord('o')):
				low_h -= 3
				
		elif(key == ord('l')):
			if(low_h < (high_h - 1)):
				high_h -= 3
		elif(key == ord('k')):
			high_h += 3
			
		elif(key == ord('i')):
			if(low_s < (high_s - 1)):
				low_s += 3
		elif(key == ord('u')):
				low_s -= 3
				
		elif(key == ord('j')):
			if(low_s < (high_s - 1)):
				high_s -= 3
		elif(key == ord('h')):
			high_s += 3

		elif(key == ord('r')):
			if(low_v < (high_v - 1)):
				low_v += 3
		elif(key == ord('e')):
			if(low_v > 0):
				low_v -= 3
		elif(key == ord('f')):
			if(low_v < (high_v - 1)):
				high_v -= 3
		elif(key == ord('d')):
			high_v += 3
			
		return (np.array([low_h, low_s, low_v]), np.array([high_h, high_s, high_v]))

#This script can be converted to UDP very easily!
TCP_IP = '169.254.185.157'
TCP_PORT = 8890
BUFFER_SIZE = 20  # Normally 1024, but we want fast times

print(str.format("connecting on {0}:{1} ", TCP_IP, TCP_PORT))
print("Connecting to socket!")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))
print("Socket connected! Initializing camera!")

#Beginning picamera stuff
with picamera.PiCamera() as camera:
	chgHSV = True
	camera.resolution = (320, 240)
	rawCapture = picamera.array.PiRGBArray(camera, size=camera.resolution)

	time.sleep(.2)

	camera.framerate = 30
	camera.shutter_speed = 18000
	
	threshold = 0.02
	current_low = getLowArray()
	current_high = getHiArray()
	
	erodeElement = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
	dilateElement = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
	iterat = 2
	cx = 0
	cy = 0
	
	circleCenter = None
	circleRadius = 0.0
	
	show_image_count = 0
	max_image_count = 5
	
	activeTracking = False
	
	#Specific to my setup and its limitations... (One monitor, one set of mouse + keyboard, etc)
	print("Camera initialized, giving some breathing time (45 seconds)")
	time.sleep(45)
	print("ready or not, here I come!")

	for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
		image = frame.array
		hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
		
		mask = cv2.inRange(hsv, current_low, current_high)
		font = cv2.FONT_HERSHEY_SIMPLEX

		eroded = cv2.erode(mask, erodeElement, iterations=1)
		dilated = cv2.dilate(eroded, dilateElement, iterations=iterat)

		ret, thresh = cv2.threshold(dilated, 0, 255, 0)
		cted, contours, hier = cv2.findContours(dilated, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
		try:
			circleCenter, circleRadius = cv2.minEnclosingCircle(contours[0])
			cx = int(circleCenter[0])
			cy = int(circleCenter[1])
			if(not activeTracking):
				print("Acquired tracking")
				activeTracking = True
		except IndexError:
			if(activeTracking):
				print("Lost Tracking")
				activeTracking = False
			
		if(show_image_count > 3):
			cv2.imshow("mask", mask)
		if(show_image_count > 2):
			cv2.imshow("eroded", eroded)
		if(show_image_count > 1):
			cv2.imshow("dilated + contour", dilated)
		if(show_image_count > 0):
			if(circleRadius is not None and circleCenter is not None):
				cv2.circle(image, (cx, cy), int(circleRadius), (0, 0, 255), -1) 
			cv2.imshow("image", image)
		
		#There is an issue here, where I force the program to slow down so we don't send too many byes to the connected object.
		sock.send(bytes(str.format("{0},{1}",cx,cy), 'UTF-8'))
		time.sleep(.065)
		printData(current_low[0], current_low[1], current_low[2], current_high[0], current_high[1], current_high[2])
		
		#Todo: clean up, make pretty
		key = cv2.waitKey(1) & 0xFF
		if(key == ord('q')):
			break
		elif(key == ord('=')):
			iterat += 1
		elif(key == ord('-')):
			iterat -= 1
		elif(key == ord('1')):
			if(show_image_count > 0):
				show_image_count -= 1
		elif(key == ord('2')):
			if(show_image_count < max_image_count):
				show_image_count += 1
		
		#For tuning HSV filtering settings
		elif(chgHSV == True):
			tup = checkKeys(key, current_low, current_high)
			current_low = tup[0]
			current_high = tup[1]
			
		rawCapture.truncate(0)
		#normalize the shutter speed.
		camera.shutter_speed = camera.exposure_speed
