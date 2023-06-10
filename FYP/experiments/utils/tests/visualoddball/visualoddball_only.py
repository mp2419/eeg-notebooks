#-------------------------
#VISUAL ODDBALL simple interface
#-------------------------
import pygame
import random
from pygame.locals import *
import numpy as np
from pandas import DataFrame, read_csv
#from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet
import pygame
import random
from pygame.locals import *
#from eegnb import stimuli, experiments

def show_instructions():
    instruction_text = "Welcome! You will see displayed circles of different colours, please count the blue ones. Occasionally, you will hear a left or right indicator. Please press the appropriate arrow key to continue the test. Stay still, focus on the centre of the screen, and try not to blink. This test will run for 10 seconds. Press spacebar to continue."
    white = (255, 255, 255)
    #green = (0, 150, 0)
    blue = (0, 0, 128)
    X = 1900
    Y = 1000
    pygame.display_surface = pygame.display.set_mode((X, Y))
    pygame.display.set_caption('Instructions')
    font = pygame.font.Font('freesansbold.ttf', 32)
    text = font.render(instruction_text, True, white, blue)
    pygame.textRect = text.get_rect()
    pygame.textRect.center = (X // 2, Y // 2)
    event = pygame.event.wait()
 
    # infinite loop
    while True:
        pygame.display_surface.fill(blue)
        pygame.display_surface.blit(text, pygame.textRect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return
        pygame.display.update()



#Create markers stream outlet
#info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
info = StreamInfo("Visual_Markers", "Markers", 1, 0, "int32", "source_visual2000")
outlet = StreamOutlet(info)

#---------Initialize pygame
pygame.init()
show_instructions()
# Set screen size and caption
size = (1900, 1000)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Oddball Experiment")

# Define colors
red = (255, 0, 0)
blue = (0, 0, 255)

#--------instructions--------



#-------start recording

# Run the experiment for 10 seconds
end_time = pygame.time.get_ticks() + 10000

# Create a list of circles
circles = []
x = size[0]/2
y = size[1]/2
radius = 200
samples = []
color = random.choice([red, blue])
circles.append((x, y, radius, color))
move = pygame.USEREVENT+1
pygame.time.set_timer(move, 500)
if(color == blue): samples.append(pygame.time.get_ticks())

#-----------loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == move:
            color1 = random.choice([red, blue])
            if color == red: 
                if color1 == blue: 
                    samples.append(pygame.time.get_ticks())
                    outlet.push_sample([1], pygame.time.get_ticks())
            color = color1
        if event.type == pygame.QUIT:
            running = False

    # Draw the circles
    pygame.draw.circle(screen, color, (x, y), radius)

    # Update the screen
    pygame.display.flip()

    # End the experiment after 10 seconds
    if pygame.time.get_ticks() > end_time:
        print(samples, len(samples))
        running = False
#uella
# Exit pygame
pygame.quit()

#------------------------
#MUSE simple interface
#------------------------
# import muse_lsl
# from pylsl import StreamInfo, StreamOutlet

# # Start the Muse connection
# muse = muse_lsl.MuseLSL()

# # Create an LSL outlet to send the EEG data to
# info = StreamInfo('Muse', 'EEG', 4, 256, 'float32', 'muse')
# outlet = StreamOutlet(info)

# # Function to start the recording
# def start_recording():
#     muse.start()
#     while True:
#         sample, timestamp = muse.get_sample()
#         outlet.push_sample(sample, timestamp)

# # Function to stop the recording
# def stop_recording():
#     muse.stop()

# #-------------------
# #muse and oddball combined 
# #-------------------
# import pygame
# import random
# import muse_lsl
# from pylsl import StreamInfo, StreamInlet, resolve_stream

# # Initialize pygame
# pygame.init()

# # Set screen size and caption
# size = (700, 500)
# screen = pygame.display.set_mode(size)
# pygame.display.set_caption("Oddball Experiment")

# # Define colors
# red = (255, 0, 0)
# blue = (0, 0, 255)

# # Create a list of circles
# circles = []
# for i in range(10):
#     x = random.randint(0, size[0])
#     y = random.randint(0, size[1])
#     radius = random.randint(10, 50)
#     color = random.choice([red, blue])
#     circles.append((x, y, radius, color))

# # Create an LSL inlet to receive the EEG data from the Muse
# streams = resolve_stream('type', 'EEG')
# inlet = StreamInlet(streams[0])

# # Create a timestamp list to store the timestamps of the oddball events
# timestamps = []

# # Run the experiment for 10 seconds
# end_time = pygame.time.get_ticks() + 10000

# # Main loop
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Draw the circles
#     for x, y, radius, color in circles:
#         pygame.draw.circle(screen, color, (x, y), radius)

#     # Update the screen
#     pygame.display.flip()

#     # Get the EEG sample and timestamp from the inlet
#     sample, timestamp = inlet.pull_sample()

#     # If the color of the circle is red, store the timestamp
#     for x, y, radius

