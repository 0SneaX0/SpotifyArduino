import pyautogui
import time
import serial
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Set environment variable for Werkzeug server
os.environ['WERKZEUG_SERVER'] = 'localhost:5000'

# Set up Spotify credentials
SPOTIPY_CLIENT_ID = '98059ca753a343fca3263f1ba6bda777'
SPOTIPY_CLIENT_SECRET = 'bcfe0ab7ae024155b777dd8095be5535'  
SPOTIPY_REDIRECT_URI = 'http://localhost:5050'

# Create a Spotify object
scope = 'user-read-playback-state'
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='98059ca753a343fca3263f1ba6bda777',
                                                   client_secret='bcfe0ab7ae024155b777dd8095be5535',
                                                   redirect_uri='http://localhost:5050',
                                                   scope=scope))
    print("Spotify authenticated successfully")
except Exception as e:
    print(f"Error authenticating with Spotify: {e}")
    exit(1)

# List of available ports
available_ports = ['com6']  # Add more ports if needed

# Attempt to connect to Arduino
def connect_arduino(ports):
    for port in ports:
        try:
            arduino = serial.Serial(port, 9600)
            print(f"Arduino connected to {port}")
            return arduino
        except serial.SerialException:
            print(f"Error opening serial port {port}")
    print("Error: Arduino not found on any available ports")
    exit(1)

arduino_uno = connect_arduino(available_ports)
previous_song = None

def read_signal() -> str:
    """Read signal from Arduino Uno"""
    try:
        signal = arduino_uno.readline().decode().strip()
        print(f"Received signal: '{signal}'")
        return signal
    except serial.SerialTimeoutException:
        print("Timeout waiting for Arduino data")
        return ""

def handle_signal(signal: str) -> None:
    """Handle signal from Arduino Uno"""
    if signal.startswith("IR:"):
        ir_code = signal[3:]  # Remove the "IR:" prefix
        print(f"Handling IR code: {ir_code}")
        if ir_code == "BF40FF00":  # Replace with actual code for play/pause
            pyautogui.typewrite(['playpause'], 0.2)
        elif ir_code == "BB44FF00":  # Replace with actual code for previous
            pyautogui.hotkey('prevtrack')
        elif ir_code == "BC43FF00":  # Replace with actual code for next
            pyautogui.hotkey('nexttrack')
        elif ir_code == "B946FF00":  # Replace with actual code for volume up
            pyautogui.press('volumeup')
        elif ir_code == "EA15FF00":  # Replace with actual code for volume down
            pyautogui.press('volumedown')
        else:
            print(f"Unknown IR code: {ir_code}")
    else:
        print(f"Unknown signal format: {signal}")

def get_current_song() -> str:
    """Get current song from Spotify"""
    current_playback = sp.current_playback()
    if current_playback and current_playback['item']:
        return current_playback['item']['name']
    return None

def update_song(previous_song: str) -> str:
    """Update song on Arduino Uno and return the current song"""
    current_song = get_current_song()
    if current_song and current_song != previous_song:
        arduino_uno.write((current_song + '\n').encode())
        print(f"Updated song: {current_song}")
    return current_song

try:
    while True:
        signal = read_signal()
        if signal:
            handle_signal(signal)
        current_song = update_song(previous_song)
        previous_song = current_song
        time.sleep(0.1)  # Add a small delay to prevent CPU overuse
except KeyboardInterrupt:
    print("Exiting...")
finally:
    arduino_uno.close()