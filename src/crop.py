import dlib
from PIL import Image
from skimage import io
import matplotlib.pyplot as plt


def detect_faces(image):
	"""Use dlib to detect faces and bounding boxes
		---------
		args:
		image: the image (in pixels) in which the faces are to be detected
		---------
		returns: 
		face_frames: the bounding boxes around the detected faces
		len(detected_faces): the number of faces detected

	"""

	# Create a face detector
	face_detector = dlib.get_frontal_face_detector()

	# Run detector and get bounding boxes of the faces on image.
	detected_faces = face_detector(image, 1)
	face_frames = [(x.left(), x.top(),
					x.right(), x.bottom()) for x in detected_faces]

	return face_frames, len(detected_faces)


def __init__(img_path, counter, destination):
	"""Initialize the detect and crop function
		---------
		args:
		img_path: the path to the image file that has to be cropped
		counter: counter for counting the number of images cropped
		destination: the path to the directory to save the cropped images
		---------
		returns: 
		a boolean value indicating whether the crop happened or not
	"""

	image = io.imread(img_path)

	# call the face detection dlib function
	detected_faces, number = detect_faces(image)
	
	# check for number of faces detected
	if number == 1:
		for n, face_rect in enumerate(detected_faces):
			face = Image.fromarray(image).crop(face_rect)
			
			plt.imshow(face)
			face.save(destination +  str(counter) + ".jpg")
			# plt.show()
			return 1
	else:
		return None


# def crop_image(detected_faces, destination, image):
#     # Crop faces and plot
#     for n, face_rect in enumerate(detected_faces):
#         counter = 1
#         face = Image.fromarray(image).crop(face_rect)
#         plt.plot(face)
#         plt.imshow(face)
#         plt.imsave(destination +  str(counter) + ".jpeg"  , face)
#         counter += 1