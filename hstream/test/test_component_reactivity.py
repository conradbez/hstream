import subprocess
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
PORT = "8000"
tests_params = [
    # "action_element_id,action,script_file",
    ("test-button","click","hstream/test/button_test_page.py"),
    ("test-slider","move arrow","hstream/test/slider_test_page.py"),
    ]

@pytest.mark.parametrize("action_element_id,action,script_file", tests_params)
def test_element(action_element_id, action, script_file):
    # Kill all previous uvicorn instances
    subprocess.run("kill -9 $(lsof -t -i:8000)".split(' '))
    
    # Start the Uvicorn server
    # Assuming the FastAPI app is already defined and saved in a file named `app.py`
    # You can modify this command based on your specific setup
    uvicorn_command = ["python", "-m", "hstream", script_file, "--port", PORT]
    uvicorn_process = subprocess.Popen(uvicorn_command)

    # Start the Uvicorn server in a separate terminal or using subprocess module

    # Set up Selenium WebDriver
    driver = webdriver.Chrome()  # Assuming Chrome WebDriver is installed

    # Open the app in the browser
    driver.get(f"http://localhost:{PORT}")  # Replace with the actual URL of your app

    # Wait for the button to be visible
    wait = WebDriverWait(driver, 2)
    # element is the thing we want to perform an action on - i.e. a button to click
    element = wait.until(EC.visibility_of_element_located((By.ID, action_element_id)))

    if action == 'click':
        # Click the button
        element.click()

    if action == 'move arrow':
        # Move the slider arrow
        
        action = ActionChains(driver)
        action.click_and_hold(element).move_by_offset(50, 0).release().perform()

        # element.send_keys(Keys.ARROW_RIGHT)

    # Wait for the response or confirmation message
    response_message = wait.until(EC.visibility_of_element_located((By.ID, "response-message")))

    # Check if the response message is as expected
    expected_message = "Element response successful"
    if response_message.text == expected_message:
        print("Element is responsive!")
    else:
        raise "Element is not responsive!"


    # Close the browser window
    driver.quit()

    # Terminate the Uvicorn server
    uvicorn_process.terminate()
    # Give some time for the server to shut down
    sleep(2)

if __name__ == '__main__':
    test_element()