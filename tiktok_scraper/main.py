from playwright.sync_api import sync_playwright, Playwright, Page
import os
from finicapi import Finic
from dotenv import load_dotenv

def main():
    profile_url = input.profile_url
    num_videos = input.num_videos

    print("Running the Playwright script")

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # Navigate to the website and login
        page.goto(profile_url)
        page.wait_for_load_state("networkidle", timeout=10000)
        import pdb; pdb.set_trace()

        # Get profile metadata
        follower_count = page.query_selector("strong[data-e2e='followers-count']").inner_text()
        following_count = page.query_selector("strong[data-e2e='following-count']").inner_text()
        likes_count = page.query_selector("strong[data-e2e='likes-count']").inner_text()
        profile_description = page.query_selector("h2[data-e2e='user-bio']").inner_text()
        profile_name = page.query_selector("h2[data-e2e='user-subtitle']").inner_text()
        profile_id = page.query_selector("h1[data-e2e='user-title']").inner_text()

        # Get videos data
        videos_list_section = page.query_selector("div[data-e2e='user-post-item-list']")
        processing_queue = videos_list_section.query_selector_all("a[href]")
        processed_videos = []

        while len(processing_queue) < num_videos:
            #scroll down in the videos list section
            videos_list_section.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_load_state("networkidle")
            processing_queue = page.query_selector_all("a[href]")
            

        browser.close()
