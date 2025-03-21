#\!/usr/bin/env python3
import os
import sys
import time
# import markdownify (no longer needed)
import logging
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbose output
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("church_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ChurchScraper")

def create_directory(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_event_pages():
    """Download event pages from Harbor Point Church website using Chrome."""
    try:
        # Import required libraries
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Log key information about the environment
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Selenium version: {webdriver.__version__}")
        
        # Try to import undetected-chromedriver which is better at evading detection
        try:
            # Try to import but handle potential import errors
            import undetected_chromedriver as uc
            logger.info(f"Successfully imported undetected_chromedriver version: {uc.__version__}")
            
            # Check if we're in an environment where undetected_chromedriver can run
            import os
            if os.environ.get('DISPLAY'):
                logger.info(f"DISPLAY environment variable is set: {os.environ.get('DISPLAY')}")
                use_undetected = True
            else:
                logger.warning("No DISPLAY environment variable found. Cannot use undetected_chromedriver in headless environment")
                use_undetected = False
        except (ImportError, AttributeError) as e:
            logger.warning(f"undetected_chromedriver not available or has issues: {e}")
            use_undetected = False
            
    except ImportError as e:
        logger.error(f"Failed to import required libraries: {e}")
        sys.stderr.write("ERROR: Required packages not installed. Run: pip install selenium webdriver-manager markdownify beautifulsoup4 tqdm\n")
        sys.exit(1)

    # Check if Chrome is installed
    chrome_installed = os.system("which google-chrome >/dev/null 2>&1") == 0
    if not chrome_installed:
        sys.stderr.write("ERROR: Google Chrome is not installed. Install with: sudo apt install ./google-chrome-stable_current_amd64.deb\n")
        sys.exit(1)

    # Create directory for downloaded content
    output_dir = "tmp_content"
    create_directory(output_dir)
    
    # URL of the events page
    events_url = "https://harborpoint.church/events"
    
    # We'll get the event URLs from the events page using Selenium
    event_urls = []
    
    logger.info("Setting up Chrome WebDriver...")
    
    try:
        # Simplifying to use regular Selenium with non-headless Chrome
        # This is the most reliable approach for websites that require JavaScript
        logger.info("Using standard Selenium with visible Chrome for JavaScript support")
        
        chrome_options = Options()
        
        # Try with headless since we're likely in a headless environment
        logger.info("Setting up Chrome with headless=new which supports JavaScript better")
        chrome_options.add_argument("--headless=new")
        
        # Basic Chrome options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        
        # Create a unique user data directory
        import tempfile
        user_data_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        logger.info(f"Created temporary user data directory: {user_data_dir}")
        
        # Use a realistic user agent that matches installed Chrome version
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.88 Safari/537.36")
        logger.info("Using user agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.88 Safari/537.36")
        
        # Anti-bot detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Explicitly enable JavaScript
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.javascript": 1,
            "profile.cookie_controls_mode": 0,
            "profile.block_third_party_cookies": False,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        
        # Initialize Chrome driver with detailed logging
        logger.info("Installing ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        logger.info(f"ChromeDriver installed at {driver_path}")
        
        service = Service(driver_path)
        logger.info("Creating Chrome driver instance...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Chrome driver instance created successfully")
        
        # Set page load timeout (in seconds)
        logger.info("Setting page load timeout to 90 seconds")
        driver.set_page_load_timeout(90)
        
        # Print capabilities for debugging
        logger.debug(f"Browser capabilities: {driver.capabilities}")
        
        # Navigate to the events page
        print(f"Fetching event list from {events_url}...")
        driver.get(events_url)
        
        # Wait for the page to load and event links to be visible with extensive logging
        try:
            logger.info("Waiting for event links to be visible...")
            
            # Wait up to 40 seconds for the elements to be present
            WebDriverWait(driver, 40).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "figure.has-clickthrough a[href]"))
            )
            logger.info("Event links found!")
            
            # Take a screenshot of the events page for debugging
            events_screenshot = os.path.join("tmp_content", "events_page.png")
            driver.save_screenshot(events_screenshot)
            logger.info(f"Saved events page screenshot to {events_screenshot}")
            
            # Log the page title and URL
            logger.info(f"Page title: {driver.title}")
            logger.info(f"Current URL: {driver.current_url}")
            
            # Allow additional time for JavaScript to render
            logger.info("Waiting additional time for JavaScript rendering...")
            logger.info("Wait completed")
            
        except TimeoutException:
            logger.error("Timeout waiting for event links to load")
            # Try with a different selector as a fallback
            try:
                logger.info("Trying alternate selector for event links...")
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/events/']"))
                )
                logger.info("Found event links with alternate selector!")
            except TimeoutException:
                logger.error("All attempts to find event links failed")
                driver.quit()
                sys.exit(1)
        
        # Robust event link extraction with fallbacks
        logger.info("Extracting event links after JavaScript rendering...")
        
        # Try primary selector
        event_elements = driver.find_elements(By.CSS_SELECTOR, "figure.has-clickthrough a[href]")
        
        # If primary selector fails, try alternatives
        if not event_elements:
            logger.warning("Primary CSS selector failed, trying alternates...")
            # Try various alternative selectors that might match event links
            alternative_selectors = [
                "a[href*='/events/']",
                "a[href*='churchcenter.com/registrations/events']",
                "div.event a[href]",
                ".events-list a[href]"
            ]
            
            for selector in alternative_selectors:
                logger.info(f"Trying selector: {selector}")
                event_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if event_elements:
                    logger.info(f"Found {len(event_elements)} elements with selector: {selector}")
                    break
        
        # Extract URLs from the found links
        if event_elements:
            for element in event_elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        logger.debug(f"Found event URL: {href}")
                        event_urls.append(href)
                except Exception as e:
                    logger.warning(f"Error extracting href from element: {e}")
            
            logger.info(f"Found {len(event_urls)} event links")
            
            # Log the first few URLs for debugging
            for i, url in enumerate(event_urls[:5]):
                logger.debug(f"Sample URL {i+1}: {url}")
                
        else:
            # Last resort: try to find ANY links on the page
            logger.error("No event links found with any CSS selector - trying to get ALL links as last resort")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    if href and ('event' in href.lower() or 'churchcenter.com' in href.lower()):
                        logger.info(f"Found potential event URL from generic links: {href}")
                        event_urls.append(href)
                except Exception as e:
                    continue
            
            if event_urls:
                logger.info(f"Found {len(event_urls)} potential event links from generic search")
            else:
                # If we still can't find links, raise an error
                logger.error("No event links could be found using any method")
                # Save page source for debugging
                with open("tmp_content/failed_page_source.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.info("Saved page source to tmp_content/failed_page_source.html")
                driver.quit()
                sys.exit(1)
        
        # Final check
        if not event_urls:
            logger.error("No valid event URLs extracted")
            driver.quit()
            sys.exit(1)
        
        print(f"Downloading {len(event_urls)} event pages...")
        
        # Create a user-readable summary of found URLs
        with open("tmp_content/event_urls.txt", "w", encoding="utf-8") as f:
            for url in event_urls:
                f.write(f"{url}\n")
        logger.info("Saved list of event URLs to tmp_content/event_urls.txt")
        
        # Process a test URL first to check if event page scraping works
        if event_urls:
            # We'll just save the URLs for now
            logger.info(f"Found {len(event_urls)} event URLs to process")
            
            # Skip the test URL step as we know headless Chrome works now
        
        # Process each event URL with the browser
        for url in tqdm(event_urls, desc="Downloading events"):
            print(f"Processing {url=}")
            # Generate filename from URL
            event_id = url.split('/')[-1]
            
            try:
                # Navigate to the event page
                driver.get(url)
                
                # Use a simpler anti-bot script that won't cause errors
                try:
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
                    print(f"DEBUG: Executed webdriver property override for {url}")
                except Exception as e:
                    print(f"DEBUG: Failed to execute anti-bot script: {e}")
                
                # Wait for page to load with extensive debugging
                try:
                    print(f"DEBUG: Waiting for body to load for {url}")
                    WebDriverWait(driver, 40).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    print(f"DEBUG: Body loaded for {url}")
                    
                                # Check page title for debugging
                    title = driver.title
                    print(f"DEBUG: Page title: {title}")
                    
                    # Try to evaluate JavaScript
                    try:
                        js_enabled = driver.execute_script("return !!window.navigator")
                        print(f"DEBUG: JavaScript is {'enabled' if js_enabled else 'disabled'}")
                    except Exception as js_error:
                        print(f"DEBUG: Error checking JavaScript: {js_error}")
                    
                        # Check for JavaScript error message
                    if "JavaScript" in driver.page_source:
                        print(f"DEBUG: JavaScript message found in page source")
                
                except TimeoutException:
                    print(f"WARNING: Complete timeout waiting for page {url} to load")
                
                
                # Execute JavaScript to ensure page is fully loaded
                print("DEBUG: scrolling to bottom")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
                
                # Don't execute the problematic JavaScript that was causing errors
                
                # Get the page source after JavaScript has rendered
                html_content = driver.page_source
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                debug_html_path = os.path.join(output_dir, f"debug_html_{event_id}.txt")
                with open(debug_html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"DEBUG: Saved HTML content to {debug_html_path}")

            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue  # Skip this URL and continue with the next one
            
        print(f"Downloaded events to {output_dir}/")
        
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)
    finally:
        # Always close the driver and clean up
        if 'driver' in locals():
            print("Closing Chrome WebDriver...")
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            
        # Clean up temporary user data directory
        try:
            if 'user_data_dir' in locals() and os.path.exists(user_data_dir):
                import shutil
                shutil.rmtree(user_data_dir, ignore_errors=True)
                logger.info(f"Removed temporary user data directory: {user_data_dir}")
        except Exception as e:
            logger.error(f"Error removing temporary directory: {e}")

if __name__ == "__main__":
    download_event_pages()
