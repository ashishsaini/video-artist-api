import time
from playwright.sync_api import sync_playwright

def record_video(url, duration=10, video_dir='videos/'):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir=video_dir)
        page = context.new_page()
        
        print("loading page..")
        page.goto(url, wait_until='load')
        print("page loaded, sleeping for ", duration)
        # Wait for 10 seconds after the page is fully loaded
        time.sleep(duration)

        print("closing page")
        context.close()
        browser.close()

        print("page closed")

if __name__ == "__main__":
    target_url = "https://www.google.com"  # replace with your desired URL
    record_video(target_url)
