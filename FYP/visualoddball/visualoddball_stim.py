"""
Generate Visual
=============

Face vs. house paradigm stimulus presentation for evoking present.

"""
import sys
from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3

from time import time
from optparse import OptionParser
import os
from glob import glob
import random

import numpy as np
from pandas import DataFrame, read_csv
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet
import pygame
import random
from pygame.locals import *
from eegnb import stimuli, experiments

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


def present(duration=120):
    print("start printing", file=sys.stderr)
    # Create markers stream outlet
    info = StreamInfo("Visual_Markers", "Markers", 1, 0, "int32", "source_visual2000")
    outlet = StreamOutlet(info)


    #---------Initialize pygame
    pygame.init()
    show_instructions()
    # Set screen size and caption
    size = (1900, 1000)
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Oddball Experiment")

    # markernames = [1, 2]
    start = time()

    # Set up trial parameters
    # n_trials = 2010
    iti = 5#0.8
    soa = 0.2
    jitter = 0.2
    record_duration = np.float32(duration)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    black = (255,255,255)

    # Run the experiment for 10 seconds
    print("Run visual experiement")
    end_time = pygame.time.get_ticks() + (duration*1000)

    # Create a list of circles
    new_blue = 1
    circles = []
    x = size[0]/2
    y = size[1]/2
    radius = 200
    samples = []
    n = 0
    color = random.choice([red, blue])
    circles.append((x, y, radius, color))
    move = pygame.USEREVENT+1
    pygame.time.set_timer(move, 500)
    if(color == blue):
        samples.append(pygame.time.get_ticks())
        outlet.push_sample([new_blue], pygame.time.get_ticks())
        n = n+1
        #print("New blue circle, number ", n)

    #-----------loop
    running = True
    while running:
        # print("old colour, new run", color)        
        #     # Intertrial interval
        #     core.wait(iti + np.random.rand() * jitter)
        for event in pygame.event.get():
            if event.type == move:
                color1 = random.choice([red, blue])
                if color == red: 
                    if color1 == blue: 
                        samples.append(pygame.time.get_ticks())
                        outlet.push_sample([new_blue], pygame.time.get_ticks())
                        n = n+1
                        # print("New blue circle, number ", n)
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


# def main():
#     parser = OptionParser()

#     parser.add_option(
#         "-d",
#         "--duration",
#         dest="duration",
#         type="int",
#         default=120,
#         help="duration of the recording in seconds.",
#     )

#     (options, args) = parser.parse_args()
#     present(options.duration)


# if __name__ == "__main__":
#     main()


    # #-----------pyshopy game 

    # win = visual.Window([1600, 900], monitor="testMonitor", units="deg", winType="pygame", fullscr=True, color=black)
    # running = True
    # n = 0
    # prev_color = red

    # while running:
    #     running = True
    #     # trialnum, filename, facehouse, girlboy = trial.values
    #     # filename = os.path.join(stim_dir, filename)
    #     new_blue = 1
    #     # Intertrial interval
    #     core.wait(iti + np.random.rand() * jitter)

    #     # Select circle to display
    #     color = random.choice([red, blue])
    #     circle = visual.Circle(win=win,units="pix",radius=150,fillColor=color,lineColor=[-1, -1, -1])
    #     circle.draw()

    #     if prev_color == red:
    #         if color == blue:
    #             # Send marker
    #             timestamp = time()
    #             # outlet.push_sample([markernames[label]], timestamp)
    #             outlet.push_sample([new_blue], timestamp)
    #             n = n+1
    #             print("New blue circl, number ", n)

    #     prev_color = color

    #     win.flip()

    #     # offset
    #     core.wait(soa)
    #     win.flip()
    #     if len(event.getKeys()) > 0 or (time() - start) > record_duration:
    #         running=False
    #event.clearEvents()

    # # Cleanup
    # win.close()