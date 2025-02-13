
import subprocess
import os
import re
import zipfile
import requests
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_chrome_version():
    """ Get the installed Chrome browser version. """
    try:
        output = subprocess.check_output(['google-chrome', '--version']).decode().strip()
        version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        if version:
            return version.group(1)
    except Exception:
        try:
            output = subprocess.check_output(['chromium-browser', '--version']).decode().strip()
            version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
            if version:
                return version.group(1)
        except Exception:
            print("Chrome browser not found.")
    return None

def get_chromedriver_version():
    """ Get the installed ChromeDriver version. """
    try:
        output = subprocess.check_output(['chromedriver', '--version']).decode().strip()
        version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        if version:
            return version.group(1)
    except Exception:
        print("ChromeDriver not found.")
    return None

def download_chromedriver(version):
    """ Download and extract the appropriate ChromeDriver version. """
    platform = "linux64" if os.name != 'nt' else "win32"
    url = f"https://storage.googleapis.com/chrome-for-testing-public/{version}/chromedriver/{platform}/chromedriver.zip"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        zip_path = "chromedriver.zip"
        with open(zip_path, "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove(zip_path)
        print(f"Downloaded and extracted ChromeDriver {version}.")
    else:
        print(f"Failed to download ChromeDriver for version {version}.")

def ensure_chromedriver():
    """ Ensure that ChromeDriver matches Chrome version. """
    chrome_version = get_chrome_version()
    chromedriver_version = get_chromedriver_version()

    if not chrome_version:
        print("Chrome is not installed or not found.")
        return

    print(f"Chrome Version: {chrome_version}")

    if not chromedriver_version:
        print("ChromeDriver not found. Downloading...")
        download_chromedriver(chrome_version)
    elif chrome_version.split('.')[0] != chromedriver_version.split('.')[0]:
        print("ChromeDriver version mismatch. Updating ChromeDriver...")
        download_chromedriver(chrome_version)
    else:
        print("ChromeDriver is up to date.")

# Run the check
ensure_chromedriver()
