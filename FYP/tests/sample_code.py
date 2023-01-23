#-------------------------
#VISUAL ODDBALL simple interface
#-------------------------
import pygame
import random

# Initialize pygame
pygame.init()

# Set screen size and caption
size = (700, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Oddball Experiment")

# Define colors
red = (255, 0, 0)
blue = (0, 0, 255)

# Run the experiment for 10 seconds
end_time = pygame.time.get_ticks() + 10000

# Create a list of circles
circles = []
for i in range(10):
    x = random.randint(0, size[0])
    y = random.randint(0, size[1])
    radius = random.randint(10, 50)
    color = random.choice([red, blue])
    circles.append((x, y, radius, color))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the circles
    for x, y, radius, color in circles:
        pygame.draw.circle(screen, color, (x, y), radius)

    # Update the screen
    pygame.display.flip()

    # End the experiment after 10 seconds
    if pygame.time.get_ticks() > end_time:
        running = False

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

