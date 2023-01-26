
def present(duration=120):

    # Create markers stream outlet
    # info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
    info = StreamInfo("Visual_Markers", "Markers", 1, 0, "int32", "source_visual2000")
    outlet = StreamOutlet(info)

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

    #-----------pyshopy game 

    win = visual.Window([1600, 900], monitor="testMonitor", units="deg", winType="pygame", fullscr=True, color=black)
    running = True
    n = 0
    prev_color = red

    while running:
        running = True
        # trialnum, filename, facehouse, girlboy = trial.values
        # filename = os.path.join(stim_dir, filename)
        new_blue = 1
        # Intertrial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select circle to display
        color = random.choice([red, blue])
        circle = visual.Circle(win=win,units="pix",radius=150,fillColor=color,lineColor=[-1, -1, -1])
        circle.draw()

        if prev_color == red:
            if color == blue:
                # Send marker
                timestamp = time()
                # outlet.push_sample([markernames[label]], timestamp)
                outlet.push_sample([new_blue], timestamp)
                n = n+1
                print("New blue circl, number ", n)

        prev_color = color

        win.flip()

        # offset
        core.wait(soa)
        win.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            running=False
        # event.clearEvents()

    # Cleanup
    win.close()

