import pygame
import subprocess as sp
from PIL import Image
import pygame
import time
import scipy.misc
import threading

pygame.init()
size=(320,240)
ssize=(640,480)
mssize=(1280,480)
screen = pygame.display.set_mode(mssize)
im1_1= pygame.Surface(size)
im1_2= pygame.Surface(size)

command1 = [ 'ffmpeg',
            '-i', 'rtsp://admin:20160404@192.168.2.22/onvif2',
            '-vf', 'fps=15',
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo', '-']
command2 = [ 'ffmpeg',
            '-i', 'rtsp://admin:20160404@192.168.2.21/onvif2',
            '-vf', 'fps=15',
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo', '-']
pipe1 = sp.Popen(command1, stdout = sp.PIPE, bufsize=10**8)
pipe2 = sp.Popen(command2, stdout = sp.PIPE, bufsize=10**8)

import numpy
# read 420*360*3 bytes (= 1 frame)
running = True
# threads = []
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    raw_image1 = pipe1.stdout.read(320*240*3)
    raw_image2 = pipe2.stdout.read(320*240*3)
    # transform the byte read into a numpy array
    image1 =  numpy.fromstring(raw_image1, dtype='uint8')
    image1 = image1.reshape((240,320,3))
    image2 =  numpy.fromstring(raw_image2, dtype='uint8')
    image2 = image2.reshape((240,320,3))
    # throw away the data in the pipe's buffer.
    # img = Image.fromarray(image,'RGB')
    # print "im1", im1.get_size()
    # print "image", image.size
    # pygame.surfarray.map_array(im1,image)
    image_cp1 = image1
    image_cp2 = image2
    image1 = numpy.swapaxes(image1, 0, 1)
    image2 = numpy.swapaxes(image2, 0, 1)
    pygame.pixelcopy.array_to_surface(im1_1, image1)
    pygame.pixelcopy.array_to_surface(im1_2, image2)
    im2_1 = pygame.transform.scale(im1_1,ssize)
    im2_2 = pygame.transform.scale(im1_2,ssize)
    screen.blit(im2_1,(0,0))
    screen.blit(im2_2,(ssize[0],0))
    pygame.display.flip()
    # scipy.misc.imsave('test.bmp', image_cp)
    # t = threading.Thread(target=scipy.misc.imsave, args=('test.bmp',image_cp))
    # threads.append(t)
    # t.start()
# for t in threads:
#     t.join()
pipe1.stdout.flush()
# pipe2.stdout.flush()
pygame.quit()