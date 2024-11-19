import sys
import re
import email
import mimetypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def find_mp3_url(html_content):
    # Regular expression to find a source tag with an mp3 URL
    match = re.search(r'<source\s+src="([^"]+\.mp3)"\s+type="audio/mp3"\s*>', html_content)
    if match:
        return match.group(1)
    return None

def extract_html_from_mhtml(mhtml_data):
    # Parse the MHTML content as an email message
    msg = email.message_from_bytes(mhtml_data.encode('utf-8'))
    
    all_html_parts = ""
    
    # Iterate through the MIME parts to extract HTML
    for part in msg.walk():
        # Skip the root part if it's multipart/related
        if part.get_content_type() == 'multipart/related':
            continue

        # Only process HTML parts
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            filename = f"part_{msg.get_boundary()}_{part.get_content_type().replace('/', '_')}{ext}"
        
        if filename.endswith('.html'):
            all_html_parts += part.get_payload(decode=True).decode('utf-8')

    return all_html_parts

def fetch_mhtml_from_url(url):
    # Setup ChromeDriver with headless option
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
        mhtml_data = driver.execute_cdp_cmd("Page.captureSnapshot", {"format": "mhtml"})
        return mhtml_data['data']
    finally:
        driver.quit()

def main():
    # Check if URL is provided
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Fetch MHTML data from the given URL
    mhtml_data = fetch_mhtml_from_url(url)
    
    # Extract HTML content from MHTML
    html_content = extract_html_from_mhtml(mhtml_data)
    
    # Find the MP3 URL
    mp3_url = find_mp3_url(html_content)
    print(mp3_url if mp3_url else "No MP3 URL found.")

if __name__ == "__main__":
    main()
