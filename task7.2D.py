import os
import RPi.GPIO as GPIO
import pyaudio
from vosk import Model, KaldiRecognizer

# Initialize the LED pin (Assume GPIO pin 18 is connected to the LED)
LED_PIN = 18

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# Initialize the Vosk model (Make sure to point to the correct directory)
model_path = "/home/pi/vosk-model"  # Change this to the correct model path
if not os.path.exists(model_path):
    print("Please download the Vosk model and unpack as 'model' in the current folder.")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Initialize PyAudio
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
stream.start_stream()

print("Listening for 'ON' or 'OFF' commands...")

try:
    while True:
        # Read the audio data
        data = stream.read(4096)
        if len(data) == 0:
            continue

        # Perform speech recognition
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            print(f"Recognized: {result}")

            # Extract the recognized text
            text = result.lower()

            # Check for "on" and "off" commands
            if "on" in text:
                print("Turning LED ON")
                GPIO.output(LED_PIN, GPIO.HIGH)  # Turn the LED ON
            elif "off" in text:
                print("Turning LED OFF")
                GPIO.output(LED_PIN, GPIO.LOW)  # Turn the LED OFF
        else:
            partial_result = recognizer.PartialResult()
            print(f"Partial: {partial_result}")

except KeyboardInterrupt:
    print("Stopping the program...")
finally:
    # Cleanup resources
    GPIO.cleanup()
    stream.stop_stream()
    stream.close()
    p.terminate()
