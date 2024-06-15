from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time

firefox_options = FirefoxOptions()
# config
# firefox_options.add_argument("--headless")

# Initialize the Firefox WebDriver
service = FirefoxService(
    executable_path='/home/leo/.local/bin/geckodriver')
driver = webdriver.Firefox(service=service, options=firefox_options)

try:
    # Open a webpage
    driver.get("http://127.0.0.1:5000")
    imput_field = driver.find_element(By.NAME, "query")
    submit_button = driver.find_element(
        By.XPATH, '//input[@type="submit" and @value="Search"]')

    imput_field.send_keys("star wars")
    submit_button.click()

    # Find and click on the movie button for Star Wars
    movie_div = driver.find_element(
        By.XPATH, '//div[@class="movie"]/h3[text()="Star Wars"]/parent::div')
    movie_button = movie_div.find_element(By.TAG_NAME, "button")
    movie_button.click()

    time.sleep(1)
    assert driver.current_url == "http://127.0.0.1:5000/login"
    print("Redirect logic is working")

finally:
    # Close the browser
    print("done")
    driver.quit()
