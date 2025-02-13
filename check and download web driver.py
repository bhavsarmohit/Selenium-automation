import subprocess
import platform
import re
import requests
import zipfile
import os
import winreg
import shutil

GOOGLE_API_URL = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"

# Set ChromeDriver filename based on OS
SYSTEM_OS = platform.system()
CHROMEDRIVER_FILENAME = "chromedriver.exe" if SYSTEM_OS == "Windows" else "chromedriver"
CHROMEDRIVER_PATH = os.path.abspath(CHROMEDRIVER_FILENAME)


def get_chrome_version():
    """ Get full Chrome version from registry (Windows) or subprocess (Linux/macOS). """
    try:
        if SYSTEM_OS == "Windows":
            reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                version, _ = winreg.QueryValueEx(key, "version")
                return version  # Full version e.g., 133.0.6943.60
        elif SYSTEM_OS == "Linux":
            output = subprocess.check_output(["google-chrome", "--version"]).decode()
        elif SYSTEM_OS == "Darwin":  # macOS
            output = subprocess.check_output(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"]
            ).decode()
        else:
            print("Unsupported OS.")
            return None

        version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)  # Full version
        return version.group(1) if version else None

    except Exception as e:
        print(f"Error fetching Chrome version: {e}")
        return None


def get_chromedriver_version():
    """ Get installed ChromeDriver version, if available. """
    if not os.path.exists(CHROMEDRIVER_PATH):
        return None

    try:
        output = subprocess.check_output([CHROMEDRIVER_PATH, "--version"]).decode()
        version = re.search(r"(\d+\.\d+\.\d+\.\d+)", output)
        return version.group(1) if version else None
    except Exception as e:
        print(f"Error fetching ChromeDriver version: {e}")
        return None


def get_latest_chromedriver_url(chrome_version):
    """ Fetch ChromeDriver URL for the major Chrome version using Google's API. """
    response = requests.get(GOOGLE_API_URL)
    if response.status_code == 200:
        data = response.json()
        if "versions" not in data:
            print("Error: 'versions' key not found in API response.")
            return None

        major_version = ".".join(chrome_version.split(".")[:3])  # Keep only major.minor.patch
        print(f"Looking for ChromeDriver matching: {major_version}...")

        for version_data in data["versions"]:
            if version_data.get("version", "").startswith(major_version):
                for download in version_data.get("downloads", {}).get("chromedriver", []):
                    if SYSTEM_OS == "Windows" and "win64" in download["url"]:
                        return download["url"]
                    elif SYSTEM_OS == "Linux" and "linux64" in download["url"]:
                        return download["url"]
                    elif SYSTEM_OS == "Darwin" and "mac-x64" in download["url"]:
                        return download["url"]

    print(f"No ChromeDriver found for Chrome version {chrome_version}.")
    return None


def download_chromedriver(download_url):
    """ Download and extract ChromeDriver correctly based on OS. """
    if not download_url:
        print("No valid download URL found.")
        return

    zip_path = "chromedriver.zip"
    response = requests.get(download_url, stream=True)

    if response.status_code == 200:
        with open(zip_path, "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")  # Extract everything in the current directory

        # Move chromedriver.exe to correct location on Windows
        extracted_folder = "chromedriver-" + download_url.split("/")[-2]  # Extracted folder name
        extracted_driver_path = os.path.join(extracted_folder, CHROMEDRIVER_FILENAME)

        if os.path.exists(extracted_driver_path):
            shutil.move(extracted_driver_path, CHROMEDRIVER_FILENAME)
            shutil.rmtree(extracted_folder)  # Cleanup extracted folder
        os.remove(zip_path)

        print("Downloaded and extracted the correct ChromeDriver.")
    else:
        print("Failed to download ChromeDriver.")


def ensure_chromedriver():
    """ Ensure ChromeDriver matches the major Chrome version. """
    chrome_version = get_chrome_version()

    if not chrome_version:
        print("Chrome is not installed or not found.")
        return

    print(f"Installed Chrome Version: {chrome_version}")

    chromedriver_version = get_chromedriver_version()
    if chromedriver_version:
        print(f"Installed ChromeDriver Version: {chromedriver_version}")

    if chromedriver_version and ".".join(chromedriver_version.split(".")[:3]) == ".".join(chrome_version.split(".")[:3]):
        print("ChromeDriver is already up to date.")
        return

    print("Updating ChromeDriver...")
    latest_version_url = get_latest_chromedriver_url(chrome_version)
    if latest_version_url:
        download_chromedriver(latest_version_url)
    else:
        print("Could not find a matching ChromeDriver version.")


# Run the check
ensure_chromedriver()
