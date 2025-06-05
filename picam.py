import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2

GPIO.setmode(GPIO.BCM)

TRIG = 2
ECHO = 3
buz = 4

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(buz, GPIO.OUT)

# Initialize camera
picam = Picamera2()
picam.start()

GPIO.output(TRIG, False)
print("Starting.....")
time.sleep(2)

try:
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_stop = time.time()

        pulse_time = pulse_stop - pulse_start
        distance = pulse_time * 17150
        print(f"Distance: {round(distance, 2)} cm")

        time.sleep(1)

        if distance < 100:
            print("Someone at the door")
            GPIO.output(buz, True)
            time.sleep(0.5)
            GPIO.output(buz, False)
            time.sleep(0.5)
            GPIO.output(buz, True)
            time.sleep(0.5)
            GPIO.output(buz, False)
            time.sleep(0.5)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"intruder_{timestamp}.jpg"
            picam.capture_file(filename)
            print(f"Image captured: {filename}")
        else:
            GPIO.output(buz, False)

except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    picam.stop()
    GPIO.cleanup()
    print("Cleanup complete")