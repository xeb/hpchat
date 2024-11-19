import time
import re
import fire
import email
import mimetypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_mp3_url(html_content):
    match = re.search(r'<source\s+src="([^"]+\.mp3)"\s+type="audio/mp3"\s*>', html_content)
    if match:
        return match.group(1)
    return None

def get_sub_urls(html_content):
    raw_urls = re.findall(r'https://[^\s\'"<>]+watch-past[^\s\'"<>]+', html_content)
    clean_urls = {url.rstrip('";>') for url in raw_urls}
    return clean_urls

def extract_html_from_mhtml(mhtml_data):
    msg = email.message_from_bytes(mhtml_data.encode('utf-8'))
    all_html_parts = ""
    for part in msg.walk():
        if part.get_content_type() == 'multipart/related':
            continue

        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            filename = f"part_{msg.get_boundary()}_{part.get_content_type().replace('/', '_')}{ext}"
        
        if filename.endswith('.html'):
            all_html_parts += part.get_payload(decode=True).decode('utf-8')

    return all_html_parts

def fetch_mhtml_from_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--save-page-as-mhtml")
    service = Service('/usr/local/bin/chromedriver')  # Update this path if necessary
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Open the webpage and save as MHTML using DevTools Protocol
        driver.get(url)

        # Wait until a specific element or condition indicates the page is loaded
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "ember138"))  # Example condition
        # )
        print("waiting for a redirect...")
        WebDriverWait(driver, 10).until(lambda driver: driver.current_url == driver.execute_script("return document.location.href"))
        
        print("Waiting for 10 seconds...")
        time.sleep(10)
        mhtml_data = driver.execute_cdp_cmd("Page.captureSnapshot", {"format": "mhtml"})
        return mhtml_data['data']
    finally:
        driver.quit()

def main(url, type='mp3'):
    mhtml_data = fetch_mhtml_from_url(url)
    html_content = extract_html_from_mhtml(mhtml_data)
    
    if type == 'sub_urls':
        sub_urls = get_sub_urls(html_content)
        print("\n".join(sub_urls))
        return
    elif type == 'mp3':
        mp3_url = find_mp3_url(html_content)
        print(mp3_url if mp3_url else "No MP3 URL found.")

if __name__ == "__main__":
    fire.Fire(main)
