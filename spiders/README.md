# Harbor Point Church Web Scrapers

This directory contains scripts for scraping content from the Harbor Point Church website.

## Scripts

### `download_events.py`

This script downloads event pages from the Harbor Point Church website and converts them to Markdown format.

#### Features

- Scrapes event links from the church's events page
- Downloads each event page
- Converts HTML content to Markdown
- Saves event information to individual Markdown files
- Shows progress with a progress bar (using tqdm)

#### Limitations

The current implementation has limitations:

- It uses simple HTTP requests which cannot execute JavaScript
- The Harbor Point Church website heavily relies on JavaScript for content rendering
- Downloaded content will be limited (only static HTML content)

#### Usage

To run the script:

```bash
# Activate the virtualenv
source venv/bin/activate

# Run the script
python spiders/download_events.py
```

Output will be saved to a `tmp_content` directory.

#### Requirements

The script depends on the following packages:
- requests
- beautifulsoup4
- tqdm
- markdownify

These dependencies are listed in the project's `pyproject.toml` file.

## Future Improvements

For better results when scraping JavaScript-heavy websites, consider:

1. Implementing a Selenium or Playwright-based solution
2. Using a headless browser to execute JavaScript
3. Investigating if the site has a public API that can be accessed directly

## Other Scripts

- `get_mp3_url.py`: Extracts MP3 URLs from church sermon pages
- `crawl_all.py`: Crawls the church website for links
- `test.sh`: Test script for the crawlers