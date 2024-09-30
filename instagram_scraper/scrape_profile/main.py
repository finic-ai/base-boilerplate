from playwright.sync_api import sync_playwright, Page
import json
import time

results = []
processing = False

def handle_response(response: str):
    global processing
    processing = True
    if "instagram.com/graphql/query" in response.url:
        response_data = response.text()
        if response_data:
            try:
                data = json.loads(response.body())
                if "data" in data:
                    data = data["data"]
                    if "user" in data:
                        user = data["user"]
                        username = user["username"]
                        profile = {}
                        profile["username"] = username
                        print("Scraping profile", username)
                        if "biography" in user:
                            profile["biography"] = user["biography"]
                        if "follower_count" in user:
                            profile["follower_count"] = user["follower_count"]
                        if "following_count" in user:
                            profile["following_count"] = user["following_count"]
                        if "media_count" in user:
                            profile["media_count"] = user["media_count"]
                        if "bio_links" in user:
                            profile["bio_links"] = user["bio_links"]["url"]
                        if "full_name" in user:
                            profile["full_name"] = user["full_name"]
                        if "is_private" in user:
                            profile["is_private"] = user["is_private"]
                        if "profile_pic_url" in user:
                            profile["profile_pic_url"] = user["profile_pic_url"]
                        if "category" in user:
                            profile["category"] = user["category"]
                        if "external_url" in user:
                            profile["external_url"] = user["external_url"]
                        if "is_verified" in user:
                            profile["is_verified"] = user["is_verified"]
                        if "is_business" in user:
                            profile["is_business"] = user["is_business"]
                        results.append(profile)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON for profile {username}")
        else:
            print(f"No JSON data found for profile {username}")
    processing = False

def main():
    """
    Instagram Profile Scraper

    This script takes a list of usernames organized by tags, visits their profiles, and extracts their profile details.

    Note: This script requires authentication, which means it must run in headful mode.
    """
    with open('usernames.json', 'r') as f:
        input_data = json.load(f)

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

    page.on("response", handle_response)
    for tag in input_data.keys():
        usernames = input_data[tag]
        for username in usernames:
            page.goto(f"https://www.instagram.com/{username}")
            page.wait_for_load_state("networkidle", timeout=10000)


    # Write results to a file
    output_file = 'profiles.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results have been written to {output_file}")

    browser.close()
