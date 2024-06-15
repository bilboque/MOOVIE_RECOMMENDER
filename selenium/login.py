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
    element = driver.find_element(By.XPATH, '//a[@href="/login"]')
    element.click()

    # wait for page login
    time.sleep(1)

    # Locate the username and password fields and the submit button
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    submit_button = driver.find_element(
        By.XPATH, '//input[@type="submit" and @value="Login"]')

    # Enter the username and password
    username_field.send_keys("bilboque")
    password_field.send_keys("Password")
    submit_button.click()

    time.sleep(1)
    assert driver.current_url == "http://127.0.0.1:5000/"

finally:
    # Close the browser
    print("done")
    driver.quit()
