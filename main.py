#import statements
import numpy.core.multiarray #idk why you have to do this, its a bug ( https://github.com/opencv/opencv/issues/8139 )
import pygame, cv2, sys, os, time, serial

#set that it is not in pitft mode
PITFTMode = False
#if the argument "--pitft" is supplied then switch to pitft mode
if ('--pitft' in sys.argv):
    #pitft mode is where it sets up the screen and environment for running on a pitft screen, dont use the "-pitft" option for use on a normal display
    PITFTMode = True

#set that it is not in graphical mode
graphicalMode = False
#if the argument "--gui" is supplied then switch to graphical mode
if ('--gui' in sys.argv):
    graphicalMode = True

#set that large image mode is false
largeImageMode = False
#if the argument "--large-image" is supplied then switch to large image mode
if ('--large-image' in sys.argv):
    largeImageMode = True

#initialize a serial connection with the arduino
arduinoSerial = serial.Serial(sys.argv[-1], 9600)

if (PITFTMode):
    initializeCommands = [
        'gpio -g mode 18 pwm', #initialize the screen brightness drivers
        'gpio pwmc 1000', #set the brightness to the max value
        'sudo sh -c \'echo "0" > /sys/class/backlight/soc\:backlight/brightness\'', #to be honest I dont know what this does I just know that without it the program wont work
    ]

    #iterate through all the startup commands and do each of them in the shell
    for each in initializeCommands:
        os.system(each) 

    #overwrite the environment variables to switch to make it support a pitft screen
    os.putenv('SDL_VIDEODRIVER', 'fbcon')
    os.putenv('SDL_FBDEV', '/dev/fb1')
    os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
    os.putenv('SDL_MOUSEDRV', 'TSLIB')

#initialize the opencv camera and set up the camera image path
camera = cv2.VideoCapture(int(sys.argv[-2]))
cameraViewPath = './camera-view.jpg'


#set the camera dimensions to 1024x768 if large image mode is on
if (largeImageMode):
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)


#create a variable to control the while loop
running = True

#set up pygame stuff if graphical mode is in
if (graphicalMode):
    #initialize pygame
    pygame.display.init()

    #get the size of the screen
    screenSize = [pygame.display.Info().current_w, pygame.display.Info().current_h]

    #initialize the pygame screen and clock
    screen = pygame.display.set_mode(screenSize, pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    #set up the variables to be used for the draw loop
    wantedFPS = 30
    pygame.mouse.set_visible(False)

#print out the system information
print('''
INFO:
The program {} running in PITFT mode. (--pitft)
The program {} running in graphical mode. (--gui)
Doing serial with board at port {}{}
'''.format(str('is' if PITFTMode else 'isnt'), str('is' if graphicalMode else 'isnt'), str(sys.argv[-1]), str('\nPress the escape key to exit.' if graphicalMode else '')))

#set up the face cascade
currentPath = os.getcwd()
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

#go through the main while loop if the program is still supposed to be running
while (running):
    #fill the background as solid black if graphical mode is on
    if (graphicalMode):
        screen.fill([0, 0, 0])

    #if the camera image is available then show it on screen
    status, image = camera.read()
    if (status):
        #do facial recognition stuff and save final image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 3, minSize = (35, 35))
        faces = faces[0:1] #select the first face that is found (not the best solution but its better than having the camera chase multiple faces at a time)
        
        '''
        for [x, y, w, h] in faces:
            #cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            #draw a green menacing cross on the targets face'''
        
        #if more than one face has been detected then draw a crosshair on the first face
        if (len(faces) >= 1):
            x, y, w, h = faces[0]
            cv2.rectangle(image, (int(x + (w / 2)), y), (int(x + (w / 2)), y + h), (0, 255, 0), 2)
            cv2.rectangle(image, (x, int(y + (h / 2))), (x + w, int(y + (h / 2))), (0, 255, 0), 2)

            #calculate the adjustments that are needed to be made by serial connection
            adjustments = ['-', '-']
            centerOfFace = [x + (w // 2), y + (h // 2)]
            oneThirdOfScreen = [image.shape[1] // 3, image.shape[0] // 3]

            #send the signals to move the camera via serial
            if (centerOfFace[0] < oneThirdOfScreen[0]):
                adjustments[0] = '4'
            if (centerOfFace[0] > oneThirdOfScreen[0] * 2):
                adjustments[0] = '3'
            if (centerOfFace[1] < oneThirdOfScreen[1]):
                adjustments[1] = '1'
            if (centerOfFace[1] > oneThirdOfScreen[1] * 2):
                adjustments[1] = '2'
            
            cv2.imwrite(cameraViewPath, image)

            #send adjustments over serial
            for adjustment in adjustments:
                if (adjustment != '-'):
                    arduinoSerial.write(adjustment.encode())

        #draw the image to the screen and center it if graphical mode is on
        if (graphicalMode):
            cameraViewImagePygame = pygame.image.load(cameraViewPath)
            imageSize = cameraViewImagePygame.get_size()
            if (imageSize[0] > screenSize[0]):
                aspectRatio = imageSize[1] / imageSize[0]
                imageSize = [screenSize[0], int(screenSize[0] * aspectRatio)]
                cameraViewImagePygame = pygame.transform.scale(cameraViewImagePygame, imageSize)
            imageCoords = [int((screenSize[0] - imageSize[0]) / 2), int((screenSize[1] - imageSize[1]) / 2)]
            screen.blit(cameraViewImagePygame, imageCoords)

    #if it is in graphical mode then do graphical stuff
    if (graphicalMode):
        #get the keydown events
        events = pygame.event.get()

        #check if the escape key has been pressed, and if it has then close the window
        for event in events:
            if (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_ESCAPE):
                    running = False

        #update the screen and set the fps
        pygame.display.update()
        clock.tick(wantedFPS)