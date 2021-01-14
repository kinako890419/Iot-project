import RPi.GPIO as gpio
import time
from flask import Flask, render_template, Response, request
from camera_pi import Camera
from picamera import PiCamera
gpio.setwarnings(False)

w1=17
w2=22
w3=23
w4=24
TRIG=26
ECHO=3

gpio.setmode(gpio.BCM)
gpio.setup(w1, gpio.OUT)
gpio.setup(w2, gpio.OUT)
gpio.setup(w3, gpio.OUT)
gpio.setup(w4, gpio.OUT)
gpio.setup(TRIG, gpio.OUT)
gpio.setup(ECHO, gpio.IN)
pwm1 = gpio.PWM(w2, 100)
pwm2 = gpio.PWM(w4, 100)

pin = [5, 6, 13, 19]
for i in range(4):
    gpio.setup(pin[i], gpio.OUT)
  
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('test.html')
    
def init():
 gpio.setmode(gpio.BCM)
 gpio.setup(w1, gpio.OUT)
 gpio.setup(w2, gpio.OUT)
 gpio.setup(w3, gpio.OUT)
 gpio.setup(w4, gpio.OUT)
 gpio.setup(TRIG, gpio.OUT)
 gpio.setup(ECHO, gpio.IN)

forward_sq = ['0011', '1001', '1100', '0110']
reverse_sq = ['0110', '1100', '1001', '0011']
 
def mforward(steps, delay):
    for i in range(steps):
        for step in forward_sq:
            
            set_motor(step)
            time.sleep(delay)
 
def mreverse(steps, delay):
    for i in range(steps):
        for step in reverse_sq:
            
            set_motor(step)
            time.sleep(delay)
 
def set_motor(step):
    gpio.setmode(gpio.BCM)
    for i in range(4):
        gpio.setup(pin[i], gpio.OUT)
        gpio.output(pin[i], step[i] == '1') 

@app.route('/camleft', methods=['GET', 'POST'])
def camleft():
 gpio.setmode(gpio.BCM)
 set_motor('0000')
 mreverse(30,0.005)
 return render_template('test.html')

@app.route('/camright', methods=['GET', 'POST'])
def camright():
 gpio.setmode(gpio.BCM)
 set_motor('0000')
 mforward(30,0.005)
 return render_template('test.html')

@app.route('/forward', methods=['GET', 'POST'])
def forward():
 init()
 gpio.setmode(gpio.BCM)
 while(distance() > 25):
  gpio.output(w1,True)
  gpio.output(w2, False)
  gpio.output(w3, True) 
  gpio.output(w4, False)
  time.sleep(0.5)
 stop()
 autoBack(0.5)
 
 return render_template('test.html')

@app.route('/back', methods=['GET', 'POST'])
def backward(): 
 gpio.cleanup()
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1, False)
 gpio.output(w2, True)
 gpio.output(w3, False) 
 gpio.output(w4, True)
 return render_template('test.html')

@app.route("/left", methods=['GET', 'POST'])
def left():
 gpio.cleanup()
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1, True)
 gpio.output(w2, False)
 gpio.output(w3, True)
 gpio.output(w4, True)
 return render_template('test.html')
 
@app.route("/right", methods=['GET', 'POST'])
def right():
 gpio.cleanup()
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1, True)
 gpio.output(w2, True) 
 gpio.output(w3,True)
 gpio.output(w4, False)
 return render_template('test.html')
@app.route("/backleft", methods=['GET', 'POST'])
def backleft():
 gpio.cleanup()
 init()
 gpio.output(w1, False)
 gpio.output(w2, True)
 gpio.output(w3, False)
 gpio.output(w4, False)
 return render_template('test.html')
@app.route("/backright", methods=['GET', 'POST']) 
def backright():
 gpio.cleanup()
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1, False)
 gpio.output(w2, False)
 gpio.output(w3, False)
 gpio.output(w4, True)
 return render_template('test.html')
 
@app.route("/stop", methods=['GET', 'POST'])
def stop():

    init()
    gpio.setmode(gpio.BCM)
    gpio.output(w1, False)
    gpio.output(w3, False)
    gpio.cleanup()
    pwm1.stop()
    pwm2.stop()
    return render_template('test.html')
    
def autoBack(t):
    init()
    gpio.setmode(gpio.BCM)
    gpio.output(w1, False)
    gpio.output(w2, True)
    gpio.output(w3, False) 
    gpio.output(w4, True)
    time.sleep(t)
    gpio.cleanup()
    
def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
def speed():
    value = request.form['speed']
    speed = int(value)*15
    
    init()
    gpio.setmode(gpio.BCM)

    while(distance() > 25):
        gpio.output(w1, True)
        pwm1.start(0)
        pwm1.ChangeDutyCycle(speed)
        pwm2.start(0)
        pwm2.ChangeDutyCycle(speed)
        gpio.output(w3, True)
        time.sleep(0.5)

    stop()
    autoBack(0.5)
    return render_template('test.html')

@app.route('/speedControl',methods=['POST'])
def speedControl():
    value = request.form['speed']
    speed = int(value)*10

    init()
    while(distance() > 25):
        gpio.setmode(gpio.BCM)
        gpio.output(w1, True)
        pwm1.start(0)
        pwm1.ChangeDutyCycle(speed)
        pwm2.start(0)
        pwm2.ChangeDutyCycle(speed)
        gpio.output(w3, True)
        time.sleep(0.5)

    stop()
    autoBack(0.5)
    return render_template('test.html')


def distance():
    gpio.setmode(gpio.BCM)
    gpio.output(TRIG, True)
    time.sleep(0.00001)
    gpio.output(TRIG, False)

    start = time.time()
    stop = time.time()

    while gpio.input(ECHO) == 0:
        start = time.time()
    while gpio.input(ECHO) == 1:
        stop = time.time()

    timeElapsed = stop - start
    distance = (timeElapsed*34300)/2
    print(distance)
    return distance


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)