import cv2
import os
import functools
from matplotlib import gridspec
import matplotlib.pylab as plt
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

location= input("Enter the location of the file ( example : video-data/file.mp4 ) : ")  # Location of the video
style_image_url = input("Enter the location of the style image ( example : vincent2.jpg ) : ")  # Location of the style image
save_as= input("Enter the location of converted file ( example : callmeby.mp4 ) : ")    # Name of the converted video

cam = cv2.VideoCapture(location) 
try:
	if not os.path.exists('tmp'):
		os.makedirs('tmp')
except OSError:
	print ('Error: Creating directory of data')
currentframe = 0

while(True):
	ret,frame = cam.read()
	if ret:
		name = 'tmp/'+ str(currentframe) + '.jpg'
		cv2.imwrite(name, frame)
		currentframe += 1
	else:
		break
cam.release()
cv2.destroyAllWindows()

def crop_center(image):
  shape = image.shape
  new_shape = min(shape[1], shape[2])
  offset_y = max(shape[1] - shape[2], 0) // 2
  offset_x = max(shape[2] - shape[1], 0) // 2
  image = tf.image.crop_to_bounding_box(
      image, offset_y, offset_x, new_shape, new_shape)
  return image

@functools.lru_cache(maxsize=None)
def load_image_system(image_path, image_size=(256, 256), preserve_aspect_ratio=True):
  img = tf.io.decode_image(
      tf.io.read_file(image_path),
      channels=3, dtype=tf.float32)[tf.newaxis, ...]
  img = crop_center(img)
  img = tf.image.resize(img, image_size, preserve_aspect_ratio=True)
  return img

def save_n(images,address):
  n = len(images)
  image_sizes = [image.shape[1] for image in images]
  w = (image_sizes[0] * 6) // 320
  plt.figure(figsize=(w * n, w))
  gs = gridspec.GridSpec(1, n, width_ratios=image_sizes)
  for i in range(n):
    plt.subplot(gs[i])
    plt.imshow(images[i][0], aspect='equal')
    plt.axis('off')
  plt.savefig(address)
  plt.close()

output_image_size = 480
content_img_size = (640, 480)
style_img_size = (256, 256)  
style_image = load_image_system(style_image_url, style_img_size)
style_image = tf.nn.avg_pool(style_image, ksize=[3,3], strides=[1,1], padding='SAME')

hub_handle = 'https://tfhub.dev/google/magenta/arbitrary-image-stylization-v1-256/2'
hub_module = hub.load(hub_handle)
import os
directory = 'tmp'
for filename in sorted(os.listdir(directory)):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        content_image = load_image_system(f, content_img_size)
        outputs = hub_module(tf.constant(content_image), tf.constant(style_image))
        stylized_image = outputs[0]
        save_n([stylized_image],f)

img_array = []
dir_len=len([name for name in os.listdir('tmp') if os.path.isfile(os.path.join('data', name))])
for i in range(0,dir_len):
    img = cv2.imread('tmp/'+str(i)+'.jpg')
    height, width, layers = img.shape
    size = (width,height)
    img_array.append(img)
out = cv2.VideoWriter(save_as,cv2.VideoWriter_fourcc(*'MP4V'), 30, size )
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()