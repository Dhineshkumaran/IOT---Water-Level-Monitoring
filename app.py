import time
import RPi.GPIO as GPIO
import blynklib
import boto3
from datetime import datetime

# Blynk Auth Token
BLYNK_AUTH = 'RB-RS1bdjEvjdh65iL6qJGkpyGKGOxyu'  # Replace with your Blynk Auth Token

# AWS DynamoDB Config
DYNAMODB_TABLE = 'SensorData'  # Table Name in DynamoDB
AWS_REGION = 'ap-southeast-2'  # Specify your AWS region

# Initialize Blynk
blynk = blynklib.Blynk(BLYNK_AUTH)

# Set up AWS DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

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
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
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
    
    return distance

def store_reading(level):
    """Store water level readings in DynamoDB."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tank_id = 'tank_1'  # Customize tank_id if needed
    
    # Store reading in DynamoDB
    response = table.put_item(
        Item={
            'tank_id': tank_id,
            'timestamp': current_time,
            'level': level
        }
    )
    print(f"Stored in DynamoDB: {current_time}, Level: {level:.1f} cm")

try:
    while True:
        # Measure the distance (water level)
        level = distance()
        print(f"Measured Distance = {level:.1f} cm")
        
        # Store the water level in DynamoDB
        store_reading(level)
        
        # Send data to Blynk
        blynk.virtual_write(1, level)  # Virtual Pin V1 is used to display the water level in Blynk
        
        # Run Blynk to handle connection and communication
        blynk.run()
        
        # Wait before the next measurement
        time.sleep(2)

# Reset GPIO on user interrupt
except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()
