import argparse
import hashlib
from selenium import webdriver
import urllib.request
import time
from PIL import Image
import os
from crop import __init__

def define_arguments(parser):
	""" CLI Arguments Definition
		--------
		args:
		parser: the argument parser object
	"""

	# URL	
	parser.add_argument("--url", 
						dest = "search_url",
						help = "URL to be scrapped from")

	# Scrapping destination
	parser.add_argument("--dest-img", 
						dest = "dest_path_img",
						help = "Path to store scrapped images in")

	# Cropping source
	parser.add_argument("--src-crop", 
						dest = "src_path_crop",
						help = "Path to pickup images to crop from")

	# Cropping destination
	parser.add_argument("--dest-crop", 
						dest = "dest_path_crop",
						help = "Path to store cropped images in")

	# Resize source
	parser.add_argument("--src-resize", 
						dest = "src_path_resize",
						help = "Path to pickup images to resize")

	# Resize destination
	parser.add_argument("--dest-resize", 
						dest = "dest_path_resize",
						help = "Path to store resize images in")

	# Remove duplicates source
	parser.add_argument("--src-dup", 
						dest = "src_path_dup",
						help = "Path to remove duplicates from")

	# Webdriver	
	parser.add_argument("--driver", 
						dest = "driver",
						help = "Path to webdriver")

	# Image Count	
	parser.add_argument("--count", 
						dest = "count",
						default = 0,
						help = "Image count. Defaults to 0")

def scrape(search_url, dest_path, driver_path, img_count):
	""" Scrapping function
		---------
		args:
		search_url: URL for scrapping
		dest_path: path to folder where images have to be saved
	"""

	# path to chrome driver. Chrome is suggested. Change path here.
	browser = webdriver.Chrome(executable_path = driver_path)

	# Robbie
	# Image count -  1338
	# Page count - from pg. 40
	count = img_count	
	page_count = 0

	# scroll trackers (if needed)
	scroll_pause_time = 1.5
	screen_height = browser.execute_script("return window.screen.height;")
	
	# start scrapping
	browser.get(search_url)
	#time.sleep(1)

	# 500 pages at a time (can change)
	while page_count <= 500:

		# Getty classes change every day. Please change
		elements = browser.find_elements_by_class_name("MosaicAsset-module__thumb___epLhd")
		main_window = browser.window_handles[0]

		for e in elements:
			handles = []
			time.sleep(0.5)

			try:
				e.click()
				time.sleep(0.5)

				# clicking on image leads to new window. Tracking the window IDs
				handles = browser.window_handles
				browser.switch_to.window(handles[1])

				# waiting for new window to load
				
				# element = WebDriverWait(driver, 10).until( EC.presence_of_element_located((By.Class, "asset-card__image")))
				time.sleep(1)
 
				# save image (not thumbnail)
				image = browser.find_element_by_class_name("asset-card__image")
				src = str(image.get_attribute("src"))
				count += 1
				urllib.request.urlretrieve(src, dest_path + str(count) + '.jpg')
				
				# switch back to main window
				browser.close()
				#time.sleep(1)
				browser.switch_to.window(main_window)

			except Exception as e:
				print(e)
				browser.switch_to.window(main_window)
				continue
		
		# pagination logic
		browser.switch_to.window(main_window)
		nextbutton = browser.find_element_by_class_name("PaginationRow-module__nextButton___PYo5w")
		page_count += 1
		nextbutton.click() 
		print(page_count, count)


def resize(source, destination):
	""" Resizing function
		---------
		args:
		source: source directory for images that need to be resized
		destination: destination directory for images that need to be resized
	"""
	counter = 0

	for root, directories, files in os.walk(source):
		for file in files:
			if(file.endswith(".jpg")):
				counter += 1
				try:
					img = Image.open(source+file)
					img1 = img.resize((128,128))
					# img1.show()
					img1.save(destination + str(counter) + ".jpg")
				except Exception as exc:
					print(exc)
					print("Error while resizing", os.path.join(root, file), exc)
					continue


def crop(source, destination):
	""" Cropping function
		---------
		args:
		source: source directory for images that need to be cropped
		destination: destination directory for images that need to be cropped
	"""
	for root, directories, files in os.walk(source):
		counter = 1
		for file in files:
			# print(file)
			if(file.endswith(".jpg")):
				try:
					return_val = __init__(source + file, counter, destination)
					if return_val is not None:
						counter += 1
				except Exception as exc:
					print("Error while cropping", os.path.join(root, file), exc)
					continue

def calc_checksum(file_name):
	"""
	Function to calculate the checksum of a file
	file_name: path to file
	"""
	with open(file=file_name, encoding='ISO-8859-1') as f:
		return str(hashlib.blake2b(f.read().encode('utf-8')).hexdigest())
	
def remove_duplicates(source):
	"""
	Function to remove duplicate copies of a file from a directory
	source: source directory
	"""
	checksum_set = set()
	with os.scandir(source) as iterator:
		for entry in iterator:
			if entry.name.endswith(".jpg") and entry.is_file():
				checksum = calc_checksum(entry.path)
				if checksum in checksum_set:
					os.remove(entry.path)
				checksum_set.add(checksum)
				
if __name__ == "__main__":
	"""Main function"""

	# define and build a argument parser
	parser = argparse.ArgumentParser()
	define_arguments(parser)
	args = parser.parse_args()

	# access search URL to scrape and path to store results in
	search_url = args.search_url
	dest_path_img = args.dest_path_img
	driver_path = args.driver
	img_count = int(args.count)

	# scrape if destination path is given in args
	if args.dest_path_img is not None:
		dest_path_img = args.dest_path_img
		if not os.path.exists(dest_path_img):
			os.makedirs(dest_path_img)
		scrape(search_url, dest_path_img, driver_path, img_count)
	
	# Remove duplicates if source path is given in args
	if args.src_path_dup:
		src_path_dup = args.src_path_dup
		remove_duplicates(src_path_dup)

	# crop if cropping source directory and destination directory is given in args
	if args.src_path_crop is not None and args.dest_path_crop is not None:
		src_path_crop = args.src_path_crop
		dest_path_crop = args.dest_path_crop
		if not os.path.exists(dest_path_crop):
			os.makedirs(dest_path_crop)
		crop(src_path_crop, dest_path_crop)
	
	# crop if resize source directory and destination directory is given in args
	if args.src_path_resize is not None and args.dest_path_resize is not None:
		src_path_resize = args.src_path_resize
		dest_path_resize = args.dest_path_resize
		if not os.path.exists(dest_path_resize):
			os.makedirs(dest_path_resize)
		resize(src_path_resize, dest_path_resize)
