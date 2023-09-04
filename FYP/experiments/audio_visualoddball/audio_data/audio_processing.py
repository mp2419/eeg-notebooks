from pydub import AudioSegment

# Load the audio file
audio = AudioSegment.from_file("FYP\\audio_visualoddball\\beep-05.wav", format="wav")

# Set the panning to left only (0% right, 100% left)
left_only = audio.pan(-1.0)

# Save the modified audio to a new file
left_only.export("FYP\\audio_visualoddball\\left_only_beep.wav", format="wav")

# Set the panning to right only (100% right, 0% left)
right_only = audio.pan(1.0)

# Save the modified audio to a new file
right_only.export("FYP\\audio_visualoddball\\right_only_beep.wav", format="wav")
