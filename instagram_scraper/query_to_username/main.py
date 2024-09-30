from playwright.sync_api import sync_playwright, Page
import json

results = {}
processing = False

def handle_response(response: str, tag: str):
    global processing
    processing = True
    if "/api/v1/fbsearch/web/top_serp/" in response.url:
        response_data = response.text()
        if response_data:
            try:
                data = json.loads(response.body())
                # Navigate through the JSON structure to find all 'user' fields
                if 'media_grid' in data and 'sections' in data['media_grid']:
                    for section in data['media_grid']['sections']:
                        if 'layout_content' in section:
                            layout_content = section['layout_content']
                            if 'medias' in layout_content:
                                for media_item in layout_content['medias']:
                                    if 'media' in media_item and 'user' in media_item['media']:
                                        user = media_item['media']['user']
                                        if user['username'] not in results[tag]:
                                            results[tag].append(user['username'])
                            elif 'two_by_two_item' in layout_content:
                                two_by_two_item = layout_content['two_by_two_item']
                                if 'channel' in two_by_two_item and 'media' in two_by_two_item['channel']:
                                    media = two_by_two_item['channel']['media']
                                    if 'user' in media:
                                        user = media['user']
                                        if user['username'] not in results[tag]:
                                            results[tag].append(user['username'])
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for tag {tag}")
        else:
            print(f"No JSON data found for tag {tag}")
    processing = False

def main():
    """
    Instagram Hashtag to Username Scraper

    This script takes a list of hashtags, performs a search on Instagram for each tag,
    and extracts the username for each account that has videos in the search results.

    Note: This script requires authentication, which means it must run in headful mode.
    """
    with open('input.json', 'r') as f:
        input_data = json.load(f)
    
    # Extract necessary information from input data
    tags = input_data['tags']
    num_results = input_data['num_results']
    # Initialize results dictionary with empty arrays for each tag
    global results
    results = {tag: [] for tag in tags}

    print("Running the Playwright script")

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, slow_mo=500)
    
    # Load cookies from cookies.json
    cookies = []
    try:
        with open('cookies.json', 'r') as f:
            cookies = json.load(f)
        cookies = [{"name": k, "value": v, "domain": ".instagram.com", "path": "/"} for k, v in cookies.items()]
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto("https://www.instagram.com/")
    except FileNotFoundError:
        print("No cookies file found. Please log in to Instagram manually in the opened browser window.")
        page = browser.new_page()
        page.goto("https://www.instagram.com/")
        page.wait_for_load_state("networkidle")
        print("Press Enter once you have successfully logged in.")
        input()
        cookies = context.cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies if cookie['domain'] == '.instagram.com'}
        with open('cookies.json', 'w') as f:
            json.dump(cookie_dict, f, indent=4)
        
        print("Cookies have been saved to cookies.json")
        print("Continuing with the script...")

    for tag in tags:
        handler = lambda response: handle_response(response, tag)
        page.on("response", handler)
        page.goto(f"https://www.instagram.com/explore/search/keyword/?q=%23{tag}")
        # Keep scrolling to the bottom of the page until we have enough results
        while len(results[tag]) < num_results and not processing:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            # Wait for network to be idle after scrolling
            page.wait_for_load_state("networkidle", timeout=10000)

        page.remove_listener("response", handler)

    # Write results to a file
    output_file = 'usernames.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results have been written to {output_file}")

    browser.close()
