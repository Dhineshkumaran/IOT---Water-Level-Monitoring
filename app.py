import time
import RPi.GPIO as GPIO

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    """Measure distance using the ultrasonic sensor."""
    try:
        # Set Trigger to HIGH
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)

        # Record StartTime and StopTime
        StartTime = time.time()
        StopTime = time.time()

        # Save StartTime
        while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time.time()

        # Save StopTime
        while GPIO.input(GPIO_ECHO) == 1:
            StopTime = time.time()

        # Time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # Multiply with the sonic speed (34300 cm/s) and divide by 2
        distance = (TimeElapsed * 34300) / 2

        # Limit the range for the sensor
        if distance > 400:  # Assuming sensor's max range is 4 meters
            return None

        return distance

    except Exception as e:
        print(f"Error measuring distance: {e}")
        return None

try:
    print("Water Level Monitoring Started...")
    while True:
        # Measure the distance (water level)
        level = distance()
        if level is not None:
            print(f"Measured Distance: {level:.1f} cm")
        else:
            print("Out of range or error in measurement")

        # Wait before the next measurement
        time.sleep(2)

# Reset GPIO on user interrupt
except KeyboardInterrupt:
    print("Measurement stopped by User")

# Reset GPIO pins on exit
finally:
    GPIO.cleanup()
