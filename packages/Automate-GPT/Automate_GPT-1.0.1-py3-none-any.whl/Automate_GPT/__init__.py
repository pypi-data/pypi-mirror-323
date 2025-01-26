from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
from pyperclip import paste

class ChatGPTAutomation:
    def __init__(self,driver:Chrome):
        self.driver:Chrome = driver
        self.actions:ActionChains = ActionChains(driver)
        self.driver.minimize_window()
    def prompt(self,prompt: str):
        self.driver.maximize_window()
        sleep(1)
        previous_text = ""
        textarea = self.driver.find_element(By.ID,"prompt-textarea")
        self.actions.send_keys_to_element(textarea,prompt).perform()
        textarea.submit()
        sleep(2)
        reselem = None
        try:
            reselem = self.driver.find_elements(By.CLASS_NAME,"markdown")[-1]
        except:
            sleep(1.5)
            reselem = self.driver.find_elements(By.CLASS_NAME,"markdown")[-1]
        sleep(1.5)
        while True:
            current_text = reselem.text
            if current_text != previous_text:
                previous_text = current_text
                sleep(2)
            else:
                sleep(1)
                self.actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys('c').key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
                sleep(0.5)
                self.driver.minimize_window()
                break
        return paste()
