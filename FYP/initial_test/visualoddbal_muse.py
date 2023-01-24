#-------------------------
#VISUAL ODDBALL + EEG STREAM
#-------------------------
import pygame
import random
import muselsl

from pylsl import StreamInfo, StreamInlet, resolve_stream

# --------------Start the Muse connection
#muse = muselsl.stream.connect()
muse = muselsl.stream(    address='4107-CKYY-C5D9',
    backend='auto',
    interface=None,
    name='muse2')

# from muselsl import stream, list_muses

# muses = list_muses()
# stream(muses[0]['address'], ppg_enabled=True, acc_enabled=True, gyro_enabled=True)

# Create an LSL outlet to send the EEG data to
info = StreamInfo('Muse', 'EEG', 4, 256, 'float32', 'muse')
outlet = StreamOutlet(info)

# Function to start the recording
def start_recording():
    muse.start()
    while True:
        sample, timestamp = muse.get_sample()
        outlet.push_sample(sample, timestamp)


# -----------Initialize pygame
pygame.init()

# Set screen size and caption
size = (1000, 700)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Oddball Experiment")

# Define colors
red = (255, 0, 0)
blue = (0, 0, 255)

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
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == move:
            color1 = random.choice([red, blue])
            if color == red: 
                if color1 == blue: samples.append(pygame.time.get_ticks())
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

