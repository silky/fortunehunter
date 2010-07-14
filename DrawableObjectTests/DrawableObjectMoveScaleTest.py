#! /usr/bin/env python
from Spritesheet import Spritesheet
from DynamicDrawableObject import DynamicDrawableObject
from Scene import Scene
import pygame
import time
pygame.init()

make=input("How many images would you like to load? ")
img={}
ft="" #filetype
r=0 #frame refreshes
i=1 #cycles images
SIZE = WIDTH, HEIGHT = 600,400 #screen sizes
t=0 #trial number

BACKGROUNDR=152
BACKGROUNDG=0
BACKGROUNDB=152

screen = pygame.display.set_mode(SIZE) #Screen Set 600x400

screen.fill((BACKGROUNDR, BACKGROUNDG, BACKGROUNDB))

switch1 = [
  [pygame.image.load("%sa1/1%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/2%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/3%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/4%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/5%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/6%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/7%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/8%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa1/9%s"%("IndividualFrames/bmp16/",".bmp"))]
]

switch2 = [
  [pygame.image.load("%sa2/1%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/2%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/3%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/4%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/5%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/6%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/7%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/8%s"%("IndividualFrames/bmp16/",".bmp"))],
  [pygame.image.load("%sa2/9%s"%("IndividualFrames/bmp16/",".bmp"))]
]

dynamicObj = DynamicDrawableObject(switch1,'',1,0,0, 2, 2)
secondDynamicObj = DynamicDrawableObject(switch1,'',1,0,100, 2, 2)
staticObj = DynamicDrawableObject(switch2,'',1,40,40, 2, 2)

initialList = [dynamicObj, secondDynamicObj]
secondaryList = [staticObj]

myScene = Scene(initialList)
myScene.addObjects(secondaryList)