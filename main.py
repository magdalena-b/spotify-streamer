# https://tutorial.cytron.io/2020/06/12/face-detection-on-pi-camera-image-using-opencv-python3-on-raspberry-pi/
import os.path
import face_recognition
import picamera
import numpy as np
from os import listdir
from os.path import isfile, join
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

scope = 'user-read-private user-read-playback-state user-modify-playback-state'
spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(open_browser=False, scope=scope))

devices = spotify.devices()
device = None
while device is None:
    for i in devices['devices']:
        if i['name'] == 'raspotify (raspberrypi)':
            device = i
            break
    if device is None:
        print("Raspotify not found, if problem continues try restarting it")
# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you
# enabled your camera in raspi-config and rebooted first.
camera = picamera.PiCamera()
camera.resolution = (320, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

# Load a sample picture and learn how to recognize it.
print("Loading known face image(s)")
files = [join("faces", f) for f in listdir("faces") if isfile(join("faces", f))]

known_face_encodings = []
known_face_names = []

for file in files:
    new_image = face_recognition.load_image_file(file)
    known_face_encodings.append(face_recognition.face_encodings(new_image)[0])
    known_face_names.append(os.path.splitext(file)[0].split('/')[-1])

with open("playlists.json") as playlist_file:
    playlists = json.load(playlist_file)

# Initialize some variables
face_locations = []
face_encodings = []

while True:
    playing = spotify.currently_playing()
    if playing is None or not playing['is_playing']:
        print("Capturing image.")
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(output)
        print("Found {} faces in image.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(output, face_locations)

        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = None

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            if name:
                print(f"I see someone named {name}!")
                spotify.shuffle()
                spotify.start_playback(context_uri=playlists[name], device_id=device['id'])
                print(f"{playlists[name]}")
            else:
                print("I don't know you")
