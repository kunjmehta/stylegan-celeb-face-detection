import random
from selenium import webdriver
import urllib.request
import time


"""Main function"""
def main():
	browser = webdriver.Firefox()
	search_url = "http://www.google.com/search?site=&tbm=isch&source=hp&biw=1873&bih=990&q=margot+robbie+face"
	images_url = []
	scroll_pause_time = 1
	screen_height = browser.execute_script("return window.screen.height;") 
	i = 1

	browser.get(search_url)

	while True:
		browser.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
		i += 1
		time.sleep(scroll_pause_time)
		# update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
		scroll_height = browser.execute_script("return document.body.scrollHeight;")  
		# Break the loop when the height we need to scroll to is larger than the total scroll height
		if (screen_height) * i > scroll_height:
			break 

	elements = browser.find_elements_by_class_name('rg_i')

	count = 0
	for e in elements:
        # get images source url
		e.click()
		time.sleep(random.randint(0,3))
		element = browser.find_elements_by_class_name('v4dQwb')

        # Google image web site logic
		if count == 0:
			big_img = element[0].find_element_by_class_name('n3VNCb')
		else:
			big_img = element[1].find_element_by_class_name('n3VNCb')

		src = str(big_img.get_attribute("src"))
		images_url.append(src)
		
		try:
			urllib.request.urlretrieve(src, str(count)+'.jpg')
		except:
			continue

		count += 1

		if count == 1000:
			break

	return images_url

if __name__ == "__main__":
	main()
