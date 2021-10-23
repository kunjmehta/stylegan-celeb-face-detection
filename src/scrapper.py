import random
import argparse
from selenium import webdriver
import urllib.request
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
from autocrop import Cropper
import os

MAX_COUNT = 300


def define_arguments(parser):
	parser.add_argument("--query",
						"-q",
						nargs="+",
						dest="query",
						help="Specify search query")
	parser.add_argument("--webdriver",
						"-w",
						dest="webdriver",
						help="Path to webdriver executable")


def main(query):
	"""Main function"""
	browser = webdriver.Firefox(
		executable_path=r'D:\Code\Python\geckodriver.exe')
	query_arg = "+".join(word for word in query)
	search_url = "http://www.google.com/search?tbm=isch&q=" + query_arg
	image_urls = set()
	scroll_pause_time = 0.5
	screen_height = browser.execute_script("return window.screen.height;")
	i = 1

	browser.get(search_url)
	count = 0
	while True:
		browser.execute_script(
			"window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
		i += 1
		# time.sleep(scroll_pause_time)
		# update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
		scroll_height = browser.execute_script(
			"return document.body.scrollHeight;")
		# Break the loop when the height we need to scroll to is larger than the total scroll height
		if (screen_height) * i > scroll_height:
			break

		elements = browser.find_elements_by_class_name('rg_i')
		print(len(elements))

		for e in elements:
			try:
				# get images source url
				e.click()
				# time.sleep(random.randint(0, 1))
				element = browser.find_elements_by_class_name('v4dQwb')

				# Google image web site logic
				if count == 0:
					big_img = element[0].find_element_by_class_name('n3VNCb')
				else:
					big_img = element[1].find_element_by_class_name('n3VNCb')
				count += 1
				src = str(big_img.get_attribute("src"))
				image_urls.add(src)
			except Exception as e:
				print("Error: ", e)
				continue

			if count >= MAX_COUNT:
				break
			print(count)
		if count >= MAX_COUNT:
			break
	return image_urls


def download_image(index, url):
	try:
		urllib.request.urlretrieve(url, str(index) + '.jpg')
	except Exception as e:
		print("Error: ", e)
		return e
	return True


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	define_arguments(parser)
	args = parser.parse_args()
	urls = main(args.query)
	with ThreadPoolExecutor() as executor:
		future_to_url = {executor.submit(download_image, index, url): (
			index, url) for index, url in enumerate(urls)}
		for future in as_completed(future_to_url):
			res = future_to_url[future]
			try:
				data = future.result()
			except Exception as exc:
				print('%r generated an exception: %s' % (res, exc))
	print(len(urls))

	cropper = Cropper()
	path = "./"
	for root, directories, files in os.walk(path):
		for file in files:
			if(file.endswith(".jpg")):
				try:
					print(os.path.join(root, file))
					# Get a Numpy array of the cropped image
					cropped_array = cropper.crop(os.path.join(root, file))
					# Save the cropped image with PIL if a face was detected:
					if cropped_array is not None:
						cropped_image = Image.fromarray(cropped_array)
						cropped_image.save(os.path.join(root, file))
				except Exception as exc:
					print("Error while cropping", os.path.join(root, file), exc)
					continue
