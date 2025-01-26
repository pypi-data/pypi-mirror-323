from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import speech_recognition as sr
from pydub import AudioSegment
import io


def solve_recaptcha(url, site_key, headless=True):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")

    if headless:
        chrome_options.add_argument("--headless")

    service = Service("/usr/bin/chromedriver")   
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(2)

        iframe = driver.find_element(By.XPATH, "//iframe[contains(@src,'recaptcha')]")
        driver.switch_to.frame(iframe)
        
        checkbox = driver.find_element(By.ID, "recaptcha-anchor")
        checkbox.click()
        driver.switch_to.default_content()
        time.sleep(3)

        audio_iframe = driver.find_element(By.XPATH, "//iframe[contains(@src,'bframe')]")
        driver.switch_to.frame(audio_iframe)

        audio_button = driver.find_element(By.ID, "recaptcha-audio-button")
        audio_button.click()
        time.sleep(2)

        audio_link = driver.find_element(By.CLASS_NAME, "rc-audiochallenge-tdownload-link").get_attribute("href")
        response = requests.get(audio_link)
        audio_content = response.content

        audio_bytes = io.BytesIO(audio_content)
        audio = AudioSegment.from_mp3(audio_bytes)
        audio = audio.set_frame_rate(16000).set_channels(1)
        wav_bytes = io.BytesIO()
        audio.export(wav_bytes, format="wav")
        wav_bytes.seek(0)

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_bytes) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Kirim jawaban
        response_input = driver.find_element(By.ID, "audio-response")
        response_input.send_keys(text)
        verify_button = driver.find_element(By.ID, "recaptcha-verify-button")
        verify_button.click()

        token = driver.execute_script("return document.getElementById('recaptcha-token').value;")
        return token

    except Exception as e:
        return f"Error: {str(e)}"

    finally:
        driver.quit()
