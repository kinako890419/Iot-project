#cd /home/pi/iot/converted_tflite_quantized
#python3 TM2_tflite.py --model model.tflite --labels labels.txt

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import io
import time
import numpy as np
#import picamera
import cv2

#import tensorflow as tf

from PIL import Image
from tflite_runtime.interpreter import Interpreter

def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}


def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image


def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]]

import RPi.GPIO as gpio
w1=17
w2=22
w3=23
w4=24

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)
gpio.setup(w1, gpio.OUT)
gpio.setup(w2, gpio.OUT)
gpio.setup(w3, gpio.OUT)
gpio.setup(w4, gpio.OUT)
pwm1 = gpio.PWM(w2, 100)
pwm2 = gpio.PWM(w4, 100)

def init():
 gpio.setmode(gpio.BCM)
 gpio.setup(w1, gpio.OUT)
 gpio.setup(w2, gpio.OUT)
 gpio.setup(w3, gpio.OUT)
 gpio.setup(w4, gpio.OUT)
def f():
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1,True)
 gpio.output(w2, False)
 gpio.output(w3, True) 
 gpio.output(w4, False)
def s():
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1, True)
 gpio.output(w3, True)
 gpio.cleanup()
 pwm1.stop()
 pwm2.stop()
def cs():
 init()
 gpio.output(w1, True)
 pwm1.start(0)
 pwm1.ChangeDutyCycle(70)
 pwm2.start(0)
 pwm2.ChangeDutyCycle(70)
 gpio.output(w3, True)
def l(t):
 gpio.cleanup()
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1, True)
 gpio.output(w2, False)
 gpio.output(w3, True)
 gpio.output(w4, True)
 time.sleep(t)
def r(t):
 gpio.cleanup()
 init()
 gpio.setmode(gpio.BCM)
 gpio.output(w1, True)
 gpio.output(w2, True) 
 gpio.output(w3,True)
 gpio.output(w4, False)
 time.sleep(t)
def main():
  parser = argparse.ArgumentParser(
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
      '--model', help='File path of .tflite file.', required=True)
  parser.add_argument(
      '--labels', help='File path of labels file.', required=True)
  args = parser.parse_args()

  labels = load_labels(args.labels)

  #interpreter = tf.lite.Interpreter(args.model)
  interpreter = Interpreter(args.model)

  interpreter.allocate_tensors()
  _, height, width, _ = interpreter.get_input_details()[0]['shape']

  #with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
    #camera.start_preview()

  cap = cv2.VideoCapture(0)
  #擷取畫面 寬度 設定為640
  cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
  #擷取畫面 高度 設定為480
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

  key_detect = 0
  times=1
  while (key_detect==0):
    ret,image_src =cap.read()

    frame_width=image_src.shape[1]
    frame_height=image_src.shape[0]

    cut_d=int((frame_width-frame_height)/2)
    crop_img=image_src[0:frame_height,cut_d:(cut_d+frame_height)]

    image=cv2.resize(crop_img,(224,224),interpolation=cv2.INTER_AREA)

    start_time = time.time()
    if (times==1):
      results = classify_image(interpreter, image)
      elapsed_ms = (time.time() - start_time) * 1000
      label_id, prob = results[0]
      
      while True:
        if labels[label_id] == "0 Class 1":
         f()
         print("1")   
         time.sleep(1)         
        if labels[label_id] == "1 Class 2":
         s()
         print("2")
        if labels[label_id] == "2 Class 3":
          
         print("3")     
        if labels[label_id] == "3 Class 4":
         cs()
         print("4")
         time.sleep(1)
        if labels[label_id] == "4 Class 5":
         l(3)
         f()
         print("5")
         time.sleep(1)
        if labels[label_id] == "5 Class 6":
         r(3)
         f()
         print("6")
         time.sleep(1)
        break
    print(labels[label_id],prob)
    cv2.putText(crop_img,labels[label_id] + " " + str(round(prob,3)), (5,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1, cv2.LINE_AA)

    times=times+1
    if (times>1):
      times=1

    cv2.imshow('Detecting....',crop_img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      key_detect = 1

  cap.release()
  cv2.destroyAllWindows()

if __name__ == '__main__':
  main()