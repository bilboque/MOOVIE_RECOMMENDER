from selenium.webdriver.support import expected_conditions as EC
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

    # Go to login
    element = driver.find_element(By.XPATH, '//a[@href="/advancedsearch"]')
    element.click()

    # wait for page login
    time.sleep(1)

    # Locate the username and password fields and the submit button
    imput_field = driver.find_element(By.NAME, "query")
    submit_button = driver.find_element(
        By.XPATH, '//input[@type="submit" and @value="Search"]')

    imput_field.send_keys("a movie about a lazy cat who eats lasagna")
    submit_button.click()

    # wait for api response
    time.sleep(2)
    movie_title = "Garfield"
    movie_element = EC.presence_of_element_located(
        (By.XPATH, f'//div[@class="movie"]/h3[text()="{movie_title}"]'))
    print(f"Found the expected movie: {movie_title}")

finally:
    # Close the browser
    print("done")
    driver.quit()
