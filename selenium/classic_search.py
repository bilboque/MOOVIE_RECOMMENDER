from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
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

    # wait for api response
    time.sleep(2)
    movie_titles = ["Star Wars",
                    "Star Wars: Episode I - The Phantom Menace",
                    "Star Wars: Episode II - Attack of the Clones",
                    "Star Wars: The Last Jedi"]
    for movie_title in movie_titles:
        try:
            movie_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[@class="movie"]/h3[text()="{movie_title}"]'))
            )
            print(f"Found the expected movie: {movie_title}")
        except:
            print("Timeout waiting for movie element to appear")

finally:
    # Close the browser
    print("done")
    driver.quit()
