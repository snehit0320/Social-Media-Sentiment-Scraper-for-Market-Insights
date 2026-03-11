import time
import random
import re
import math
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
import numpy as np

# --- MongoDB Integration ---
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

# --- Playwright Import ---
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Configuration ---
TWITTER_USERNAME = "Twitter_Username"
TWITTER_PASSWORD = "Twitter_pwd"

TARGET_ACCOUNTS_FOR_SEARCH = ["ecb"]
SINCE_DATE = "2025-04-09"
UNTIL_DATE = "2025-06-18"
MAX_POSTS_PER_ACCOUNT = 100

# --- MongoDB Configuration ---
MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
DATABASE_NAME = "twitter_scraper"
COLLECTION_NAME = "tweets"

# --- Bright Data Proxy Configuration ---
USE_BRIGHTDATA_PROXY = False
BRIGHTDATA_PROXY_HOST = "brd.superproxy.io"
BRIGHTDATA_PROXY_PORT = 22225
BRIGHTDATA_USERNAME = "brd-customer-YOUR_CUSTOMER_ID-zone-YOUR_ZONE"
BRIGHTDATA_PASSWORD = "YOUR_ZONE_PASSWORD"

# --- MongoDB Setup ---
def setup_mongodb():
    """Initialize MongoDB connection and setup collections"""
    try:
        client = MongoClient(MONGODB_HOST, MONGODB_PORT)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Create index on post_url to prevent duplicates
        collection.create_index("post_url", unique=True)
        
        print(f"Connected to MongoDB: {DATABASE_NAME}.{COLLECTION_NAME}")
        return collection
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None

def save_to_mongodb(tweet_data_list, collection):
    """Save tweet data to MongoDB"""
    if not tweet_data_list or collection is None:
        return
    
    saved_count = 0
    for tweet in tweet_data_list:
        try:
            # Add timestamp
            tweet['scraped_at'] = datetime.now()
            
            # Insert with duplicate handling
            collection.insert_one(tweet)
            saved_count += 1
        except DuplicateKeyError:
            print(f"Duplicate tweet skipped: {tweet.get('post_url', 'N/A')}")
        except Exception as e:
            print(f"MongoDB Error: {e} for {tweet.get('post_url', 'N/A')}")
    
    print(f"Attempted {len(tweet_data_list)} tweets. {saved_count} new added to MongoDB.")

# --- Enhanced Human-Like Behavior Functions ---
def human_like_sleep(base_time=1.0, variance=0.5, distribution='normal'):
    """Generate human-like sleep patterns with various distributions"""
    if distribution == 'normal':
        sleep_time = max(0.1, np.random.normal(base_time, variance))
    elif distribution == 'exponential':
        sleep_time = np.random.exponential(base_time)
    elif distribution == 'uniform':
        sleep_time = random.uniform(base_time - variance, base_time + variance)
    else:
        sleep_time = base_time + random.uniform(-variance, variance)
    
    time.sleep(max(0.1, sleep_time))

def random_micro_pause():
    """Add random micro-pauses to simulate human hesitation"""
    if random.random() < 0.3:  # 30% chance of micro-pause
        time.sleep(random.uniform(0.05, 0.2))

def enhanced_human_like_mouse_move(driver, num_moves=None, complexity='medium'):
    """Enhanced mouse movement with more realistic patterns"""
    if num_moves is None:
        num_moves = random.randint(2, 7)
    
    actions = ActionChains(driver)
    
    try:
        body_element = driver.find_element(By.TAG_NAME, "body")
        viewport_width = body_element.size['width']
        viewport_height = body_element.size['height']
        
        # Starting position
        current_x = random.randint(0, viewport_width // 2)
        current_y = random.randint(0, viewport_height // 2)
        
        for i in range(num_moves):
            if complexity == 'high':
                # Bezier-like curved movements
                control_x = random.randint(0, viewport_width)
                control_y = random.randint(0, viewport_height)
                
                # Multiple small movements to create curve
                steps = random.randint(3, 8)
                for step in range(steps):
                    t = step / steps
                    # Quadratic bezier calculation
                    next_x = int((1-t)**2 * current_x + 2*(1-t)*t * control_x + t**2 * (current_x + random.randint(-100, 100)))
                    next_y = int((1-t)**2 * current_y + 2*(1-t)*t * control_y + t**2 * (current_y + random.randint(-100, 100)))
                    
                    actions.move_to_element_with_offset(body_element, 
                                                       max(0, min(next_x, viewport_width-1)), 
                                                       max(0, min(next_y, viewport_height-1)))
                    actions.pause(random.uniform(0.02, 0.05))
                    current_x, current_y = next_x, next_y
            else:
                # Standard movement with human-like variation
                move_x = random.randint(-200, 200)
                move_y = random.randint(-150, 150)
                
                actions.move_to_element_with_offset(body_element,
                                                   max(0, min(current_x + move_x, viewport_width-1)),
                                                   max(0, min(current_y + move_y, viewport_height-1)))
                actions.pause(random.uniform(0.1, 0.4))
                current_x += move_x
                current_y += move_y
            
            # Random chance for additional actions
            if random.random() < 0.2:  # 20% chance
                actions.pause(random.uniform(0.5, 1.5))  # Longer pause as if reading
            
            random_micro_pause()
        
        actions.perform()
        
    except Exception as e:
        print(f"Mouse movement error: {e}")

def human_like_scroll(driver, scroll_amount=None, scroll_type='smooth'):
    """Enhanced scrolling with human-like patterns"""
    if scroll_amount is None:
        scroll_amount = random.randint(300, 800)
    
    if scroll_type == 'smooth':
        # Smooth scrolling in small increments
        total_scrolled = 0
        while total_scrolled < scroll_amount:
            increment = random.randint(50, 150)
            driver.execute_script(f"window.scrollBy(0, {increment});")
            total_scrolled += increment
            
            # Variable pause between increments
            human_like_sleep(0.1, 0.05, 'exponential')
            
            # Occasional reverse scroll (human correction)
            if random.random() < 0.05:  # 5% chance
                driver.execute_script(f"window.scrollBy(0, -{random.randint(20, 50)});")
                human_like_sleep(0.2, 0.1)
    
    elif scroll_type == 'reading':
        # Simulate reading pattern with pauses
        segments = random.randint(3, 6)
        segment_size = scroll_amount // segments
        
        for i in range(segments):
            driver.execute_script(f"window.scrollBy(0, {segment_size + random.randint(-50, 50)});")
            
            # Reading pause - longer at beginning, shorter as we go
            reading_time = random.uniform(1.5, 3.0) * (1.2 - (i * 0.2))
            human_like_sleep(reading_time, 0.5, 'normal')
            
            # Random mouse movement while "reading"
            if random.random() < 0.6:
                enhanced_human_like_mouse_move(driver, num_moves=random.randint(1, 3), complexity='medium')
    
    else:
        # Standard scroll with variation
        actual_scroll = scroll_amount + random.randint(-100, 100)
        driver.execute_script(f"window.scrollBy(0, {actual_scroll});")

def random_interaction_pause():
    """Random pause as if user is thinking or reading"""
    pause_types = ['micro', 'short', 'medium', 'long']
    pause_type = random.choices(pause_types, weights=[40, 35, 20, 5])[0]
    
    if pause_type == 'micro':
        human_like_sleep(0.1, 0.05, 'exponential')
    elif pause_type == 'short':
        human_like_sleep(0.5, 0.2, 'normal')
    elif pause_type == 'medium':
        human_like_sleep(1.5, 0.5, 'normal')
    else:  # long
        human_like_sleep(3.0, 1.0, 'uniform')

# --- Keep all original helper functions unchanged ---
def get_brightdata_proxy_string():
    if USE_BRIGHTDATA_PROXY:
        return f"http://{BRIGHTDATA_USERNAME}:{BRIGHTDATA_PASSWORD}@{BRIGHTDATA_PROXY_HOST}:{BRIGHTDATA_PROXY_PORT}"
    return None

def get_playwright_proxy_config():
    if USE_BRIGHTDATA_PROXY:
        return {
            "server": f"http://{BRIGHTDATA_PROXY_HOST}:{BRIGHTDATA_PROXY_PORT}",
            "username": BRIGHTDATA_USERNAME,
            "password": BRIGHTDATA_PASSWORD
        }
    return None

# --- Original Playwright login function (unchanged) ---
def login_with_playwright(username, password, headless_mode=False):
    print("Attempting login with Playwright...")
    playwright_proxy_config = get_playwright_proxy_config()

    with sync_playwright() as p:
        browser_options = {"headless": headless_mode}
        if playwright_proxy_config:
            browser_options["proxy"] = playwright_proxy_config
            print(f"Playwright using proxy: {playwright_proxy_config['server']}")
        
        browser = None
        try:
            browser = p.chromium.launch(**browser_options)
            ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.uniform(530, 540):.2f} (KHTML, like Gecko) Chrome/{random.uniform(100, 110):.2f}.0.{random.randint(5000,6000)}.{random.randint(100,200)} Safari/{random.uniform(530, 540):.2f}"
            context_args = {
                "user_agent": ua,
                "viewport": {"width": 1280 + random.randint(0,100), "height": 720 + random.randint(0,100)},
                "device_scale_factor": random.choice([1, 1.5, 2]),
                "locale": random.choice(["en-US", "en-GB"]),
                "timezone_id": random.choice(["America/New_York", "Europe/London", "America/Los_Angeles"])
            }
            context = browser.new_context(**context_args)
            page = context.new_page()
            
            print("Playwright: Starting automated login steps...")
            page.goto("https://twitter.com/login", timeout=90000)
            page.wait_for_timeout(random.uniform(3000, 5000))

            username_field = page.locator("input[name='text']").first
            if not username_field.is_visible(timeout=15000): 
                raise Exception("Playwright: Username field not found.")
            username_field.hover()
            username_field.click(delay=random.uniform(30,100))
            username_field.type(username, delay=random.uniform(100, 250))
            page.wait_for_timeout(random.uniform(500, 1000))
            
            next_button = page.locator("//div[@role='button'][.//span[contains(text(),'Next')]] | //button[.//span[contains(text(),'Next')]]").first
            if next_button.is_visible(timeout=7000): 
                next_button.hover()
                next_button.click(delay=random.uniform(50,150))
            else: 
                username_field.press("Enter")
            print("Playwright: Username submitted.")
            page.wait_for_timeout(random.uniform(3000, 5000))
            
            inter_input = page.locator("input[data-testid='ocfEnterTextTextInput'] | //input[@name='text' and @type='text' and not(@autocomplete='username')]").first
            try:
                if inter_input.is_visible(timeout=5000):
                    label_text = inter_input.get_attribute("aria-label") or ""
                    if "username" in label_text.lower() or "phone" in label_text.lower() or "challenge" in label_text.lower():
                        print("Playwright: Potential verification step found.")
                        inter_input.hover()
                        inter_input.type(username, delay=random.uniform(100,200))
                        page.wait_for_timeout(random.uniform(500, 1000))
                        inter_next_button = page.locator("//div[@role='button'][.//span[contains(text(),'Next')]] | //button[.//span[contains(text(),'Next')]]").first
                        if inter_next_button.is_visible(timeout=3000): 
                            inter_next_button.hover()
                            inter_next_button.click(delay=random.uniform(50,150))
                        else: 
                            inter_input.press("Enter")
                        print("Playwright: Verification info submitted.")
                        page.wait_for_timeout(random.uniform(2500, 4000))
            except PlaywrightTimeoutError: 
                pass
                
            password_field = page.locator("input[name='password']").first
            if not password_field.is_visible(timeout=15000): 
                raise Exception("Playwright: Password field not found.")
            password_field.hover()
            password_field.type(password, delay=random.uniform(100, 250))
            page.wait_for_timeout(random.uniform(500, 1000))
            
            login_button = page.locator("//div[@data-testid='LoginForm_Login_Button'] | //div[@role='button'][.//span[contains(text(),'Log in')]] | //button[.//span[contains(text(),'Log in')]]").first
            if login_button.is_visible(timeout=7000): 
                login_button.hover()
                login_button.click(delay=random.uniform(50,150))
            else: 
                password_field.press("Enter")
            print("Playwright: Password submitted. Automated steps complete.")
            
            print("\nPlaywright: Waiting for navigation to Twitter home page (https://x.com/home)...")
            print("IMPORTANT: If login stuck, complete MANUALLY in Playwright browser. Waiting up to 5 mins.\n")
            try:
                page.wait_for_url("https://x.com/home", timeout=300000)
                print("Playwright: Successfully navigated to /home.")
            except PlaywrightTimeoutError:
                print("Playwright: Timed out waiting for /home.")
                print("Current URL:", page.url)
                if "login" in page.url or "checkpoint" in page.url or "challenge" in page.url:
                    print("Login incomplete. Complete manually in Playwright browser.")
                    input("If NOW done, press Enter to extract cookies. Else, Ctrl+C...")
                    if "home" not in page.url.lower(): 
                        print("Still not on /home. Failed.")
                        browser.close()
                        return None
                    print("Playwright: Proceeding after manual prompt.")
                else:
                    print("Ambiguous state. Check Playwright browser.")
                    input("If logged in, Enter. Else, Ctrl+C...")
                    if "home" not in page.url.lower(): 
                        print("Still not on /home. Failed.")
                        browser.close()
                        return None
                        
            cookies = context.cookies()
            print("Playwright: Login successful, cookies extracted.")
            if browser.is_connected(): 
                browser.close()
            return cookies
            
        except Exception as e:
            print(f"Playwright: Critical error during login: {e}")
            if page:
                print("\nIMPORTANT: Attempt to complete login MANUALLY in Playwright browser. Waiting up to 5 mins for /home.\n")
                try:
                    page.wait_for_url("https://x.com/home", timeout=300000)
                    print("Playwright: Navigated to /home after manual intervention.")
                    cookies = context.cookies()
                    if browser.is_connected(): 
                        browser.close()
                    return cookies
                except PlaywrightTimeoutError: 
                    print("Timed out for /home after error + manual intervention.")
                except Exception as e_manual: 
                    print(f"Error during manual wait: {e_manual}")
            if browser and browser.is_connected(): 
                browser.close()
            return None
        finally:
            if browser and browser.is_connected():
                try: 
                    browser.close()
                except Exception: 
                    pass

def get_selenium_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.uniform(530, 540):.2f} (KHTML, like Gecko) Chrome/{random.uniform(95, 105):.2f}.0.{random.randint(4000,5000)}.{random.randint(100,200)} Safari/{random.uniform(530, 540):.2f}")
    
    proxy_string = get_brightdata_proxy_string()
    if proxy_string:
        chrome_options.add_argument(f'--proxy-server={proxy_string}')
        print(f"Selenium using proxy: {proxy_string.split('@')[1] if '@' in proxy_string else proxy_string}")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(random.uniform(8, 12))
    return driver

# --- Keep all original parsing functions unchanged ---
def parse_engagement_number(s_num):
    s_num = str(s_num).strip().replace(',', '')
    multiplier = 1
    original_s_num = s_num
    if not s_num: 
        return 0
    if 'K' in s_num.upper(): 
        multiplier = 1000
        s_num = s_num.upper().replace('K', '')
    elif 'M' in s_num.upper(): 
        multiplier = 1000000
        s_num = s_num.upper().replace('M', '')
    try:
        if not s_num or (not s_num[0].isdigit() and s_num[0] != '.'):
            if original_s_num.isalpha(): 
                return 0
            if not s_num or not s_num.replace('.', '', 1).isdigit(): 
                return 0
        return int(float(s_num) * multiplier)
    except ValueError: 
        return 0

def get_engagement_via_aria(article_soup, keyword):
    pattern = re.compile(rf"\b{keyword}(s)?\b", re.IGNORECASE)
    for el in article_soup.find_all(True, attrs={'aria-label': lambda x: x and pattern.search(x)}):
        aria_text = el.get('aria-label', '')
        if count_match := re.search(r"([\d,.\sKM]+)\s+\b" + f"{keyword}(s)?\\b", aria_text, re.IGNORECASE):
            if (parsed_val := parse_engagement_number(count_match.group(1).strip().replace(" ", ""))) >= 0: 
                return parsed_val
        el_testid = el.get('data-testid', '').lower()
        keyword_lower = keyword.lower()
        if el_testid == keyword_lower or el_testid == f"un{keyword_lower}" or (keyword_lower == "reply" and el_testid == "reply"):
            if count_container := el.find('div', attrs={'data-testid': 'app-text-transition-container'}):
                if text_content := count_container.get_text(strip=True): 
                    return parse_engagement_number(text_content)
    return 0

def construct_advanced_search_url(account_name, since_date, until_date):
    base_url = "https://x.com/search"
    query_parts = []
    if account_name:
        query_parts.append(f"(from%3A{account_name})")
    if until_date:
        query_parts.append(f"until%3A{until_date}")
    if since_date:
        query_parts.append(f"since%3A{since_date}")
    
    query_string = "%20".join(query_parts)
    
    if query_string:
        return f"{base_url}?q={query_string}&src=typed_query&f=live"
    return None

# --- Enhanced Scraping Function with Human-Like Behavior ---
def scrape_twitter_account_advanced_search(driver, account_to_search, since_date_str, until_date_str):
    search_url = construct_advanced_search_url(account_to_search, since_date_str, until_date_str)
    if not search_url:
        print(f"Could not construct search URL for {account_to_search}. Skipping.")
        return []

    print(f"\n--- Enhanced Selenium Scraping for @{account_to_search} from {since_date_str} to {until_date_str} ---")
    print(f"Using URL: {search_url}")
    
    driver.get(search_url)
    
    # Initial page load behavior
    human_like_sleep(6, 2, 'normal')  # Longer initial wait
    enhanced_human_like_mouse_move(driver, num_moves=random.randint(2, 4), complexity='medium')
    random_interaction_pause()
    
    tweets_collected, session_tweet_urls = [], set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts, MAX_SCROLL_ATTEMPTS = 0, 100
    consecutive_scrolls_no_new, CONSECUTIVE_NO_NEW_LIMIT = 0, random.randint(5, 8)
    consecutive_no_height_change, CONSECUTIVE_NO_HEIGHT_LIMIT = 0, random.randint(3, 5)

    while len(tweets_collected) < MAX_POSTS_PER_ACCOUNT and scroll_attempts < MAX_SCROLL_ATTEMPTS:
        scroll_attempts += 1
        print(f"\nEnhanced scroll attempt #{scroll_attempts}. Collected: {len(tweets_collected)}/{MAX_POSTS_PER_ACCOUNT}")
        
        # Random pre-scroll behavior
        if random.random() < 0.3:  # 30% chance
            enhanced_human_like_mouse_move(driver, num_moves=random.randint(1, 3), complexity='high')
        
        # Vary scrolling patterns
        scroll_patterns = ['smooth', 'reading', 'standard']
        scroll_pattern = random.choices(scroll_patterns, weights=[50, 30, 20])[0]
        
        currentscroll = driver.execute_script("return window.scrollY")
        if scroll_pattern == 'smooth':
            human_like_scroll(driver, 
                            scroll_amount=random.randint(400, 800), 
                            scroll_type='smooth')
        elif scroll_pattern == 'reading':
            human_like_scroll(driver, 
                            scroll_amount=random.randint(600, 1000), 
                            scroll_type='reading')
        else:
            # Standard scroll with human variation
            scroll_amount = random.randint(300, 700)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        currentscroll2 = driver.execute_script("return window.scrollY")
        if currentscroll2 < currentscroll:
            print(f"  Enhanced scroll #{scroll_attempts}: Scrolled back to {currentscroll2} from {currentscroll}.")
            window_height = driver.execute_script("return window.innerHeight")
            variation = random.randint(int(window_height * 0.5), int(window_height * 1))
            new_scroll_pos = max(0, currentscroll + variation)
            driver.execute_script(f"window.scrollTo(0, {new_scroll_pos});")

        # Post-scroll behavior
        random_interaction_pause()
        
        # Occasional mouse movement after scrolling
        if random.random() < 0.4:  # 40% chance
            enhanced_human_like_mouse_move(driver, num_moves=random.randint(1, 2), complexity='medium')
        
        # Enhanced sleep pattern after scrolling
        base_sleep = 3.5 + (scroll_attempts * random.uniform(0.05, 0.15))
        variance = random.uniform(1.5, 2.5)
        human_like_sleep(base_sleep, variance, 'normal')
        
        # Data extraction (keep original logic)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        newly_found_this_scroll_count = 0
        
        for article_idx, article in enumerate(soup.find_all('article', attrs={'data-testid': 'tweet'})):
            if len(tweets_collected) >= MAX_POSTS_PER_ACCOUNT: 
                break
            tweet_data = {}
            try:
                user_name_div = article.find('div', attrs={'data-testid': 'User-Name'})
                parsed_author = None
                if user_name_div:
                    name_span = user_name_div.find('span', string=True)
                    if name_span: 
                        parsed_author = name_span.get_text(strip=True)
                    else:
                        parts = [s.get_text(strip=True) for s in user_name_div.find_all('span') if s.get_text(strip=True)]
                        if parts: 
                            parsed_author = parts[0]
                            
                tweet_data['author'] = parsed_author if parsed_author else account_to_search
                tweet_data['text'] = (text_div.get_text(separator=' ', strip=True) if (text_div := article.find('div', attrs={'data-testid': 'tweetText'})) else "No text")
                tweet_data['time'] = (time_tag['datetime'] if (time_tag := article.find('time', attrs={'datetime': True})) else "Unknown Time")
                
                url_tag = (parent_a if (parent_a := (time_tag.find_parent('a', href=re.compile(r"/[^/]+/status/\d+")) if time_tag else None)) else (plausible_links[0] if (plausible_links := [l for l in article.find_all('a', href=re.compile(r"/[^/]+/status/\d+")) if 'analytics' not in l.get('href','').lower() and not l.find_parent('div',attrs={'data-testid':re.compile(r"tweetPhoto|tweetVideo",re.I)})]) else None))
                tweet_data['post_url'] = ("https://twitter.com" + url_tag['href'] if url_tag and url_tag.has_attr('href') else f"https://twitter.com/{account_to_search}/status/NO_URL_{int(time.time())}_{len(tweets_collected)}_{article_idx}")
                
                if "NO_URL" in tweet_data['post_url'] or tweet_data['post_url'] in session_tweet_urls: 
                    continue
                session_tweet_urls.add(tweet_data['post_url'])
                
                tweet_data['likes'] = get_engagement_via_aria(article, "Like")
                tweet_data['replies'] = get_engagement_via_aria(article, "Replies") 
                tweet_data['reposts'] = get_engagement_via_aria(article, "Repost")
                tweet_data['views'] = get_engagement_via_aria(article, "View")
                tweet_data['engagement'] = (((tweet_data.get('likes',0) or 0) + (tweet_data.get('replies',0) or 0) + (tweet_data.get('reposts',0) or 0)) / float(tweet_data['views'])) if tweet_data['views'] and tweet_data['views'] > 0 else 0.0
                
                tweets_collected.append(tweet_data)
                newly_found_this_scroll_count += 1
                print(f"  Collected ({len(tweets_collected)}/{MAX_POSTS_PER_ACCOUNT}): @{tweet_data.get('author','N/A')}... L:{tweet_data['likes']} Rep:{tweet_data['replies']} RP:{tweet_data['reposts']} V:{tweet_data['views']} E:{tweet_data['engagement']:.4f}")
                
            except Exception: 
                pass
        
        print(f"  Enhanced scroll #{scroll_attempts}: Processed {len(soup.find_all('article', attrs={'data-testid': 'tweet'}))} articles, found {newly_found_this_scroll_count} new.")
        
        if newly_found_this_scroll_count == 0: 
            consecutive_scrolls_no_new += 1
        else: 
            consecutive_scrolls_no_new = 0
            
        current_page_height = driver.execute_script("return document.body.scrollHeight")
        if current_page_height == last_height:
            if newly_found_this_scroll_count == 0: 
                consecutive_no_height_change += 1
        else: 
            consecutive_no_height_change = 0 
        last_height = current_page_height
        
        # Exit conditions
        if consecutive_scrolls_no_new >= CONSECUTIVE_NO_NEW_LIMIT or \
           consecutive_no_height_change >= CONSECUTIVE_NO_HEIGHT_LIMIT or \
           len(tweets_collected) >= MAX_POSTS_PER_ACCOUNT or \
           scroll_attempts >= MAX_SCROLL_ATTEMPTS:
            print(f"  Exiting enhanced scroll loop for @{account_to_search} search due to conditions.")
            break
    
    print(f"Finished enhanced scraping for @{account_to_search} between {since_date_str} and {until_date_str}. Collected {len(tweets_collected)} tweets.")
    return tweets_collected

# --- Main Execution ---
if __name__ == "__main__":
    if "YOUR_TWITTER" in TWITTER_USERNAME or "YOUR_TWITTER" in TWITTER_PASSWORD:
        print("!!! Please update TWITTER_USERNAME and TWITTER_PASSWORD in the script !!!")
        exit()
    if USE_BRIGHTDATA_PROXY and ("YOUR_CUSTOMER_ID" in BRIGHTDATA_USERNAME or "YOUR_ZONE_PASSWORD" in BRIGHTDATA_PASSWORD):
        print("!!! Proxy is enabled but Bright Data credentials are placeholders. Update them or set USE_BRIGHTDATA_PROXY to False. !!!")
        exit()

    print("Starting Enhanced Twitter Advanced Search Scraper with MongoDB (Playwright Login + Selenium Scrape)...")
    print("WARNING: Scraping Twitter is against their ToS.")
    
    # Setup MongoDB
    mongodb_collection = setup_mongodb()
    if mongodb_collection is None:
        print("Failed to connect to MongoDB. Exiting.")
        exit()
    
    selenium_driver = None
    try:
        login_cookies = login_with_playwright(TWITTER_USERNAME, TWITTER_PASSWORD, headless_mode=False) 
        if not login_cookies: 
            print("Failed to log in with Playwright. Exiting.")
            exit()
        
        print("Initializing Enhanced Selenium WebDriver and loading cookies...")
        selenium_driver = get_selenium_webdriver()
        selenium_driver.get("https://twitter.com/")
        human_like_sleep(2, 0.5, 'normal')

        for cookie in login_cookies:
            sel_cookie = {'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain'], 
                          'path': cookie['path'], 'secure': cookie['secure'], 'httpOnly': cookie['httpOnly']}
            if 'expires' in cookie and cookie['expires'] != -1 : 
                sel_cookie['expiry'] = int(cookie['expires'])
            if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']:
                 if cookie['sameSite'] == 'None' and not cookie['secure']:
                     pass
                 else:
                     sel_cookie['sameSite'] = cookie['sameSite']
            try: 
                selenium_driver.add_cookie(sel_cookie)
            except Exception as e_cookie: 
                print(f"Selenium: Error adding cookie {cookie['name']}: {e_cookie}")
        
        print("Cookies loaded. Navigating to confirm session with enhanced behavior...")
        selenium_driver.get("https://x.com/home")
        human_like_sleep(4, 2, 'normal')
        enhanced_human_like_mouse_move(selenium_driver, complexity='medium')

        if "login" in selenium_driver.current_url.lower() or "Login" in selenium_driver.title:
            print("Selenium: Still on login page or redirected. Login transfer might have failed.")
            print("Current URL for Selenium:", selenium_driver.current_url)
            print("Current Title for Selenium:", selenium_driver.title)
            input("Press Enter to attempt scraping anyway or Ctrl+C to abort...")
        else: 
            print("Selenium: Successfully on a logged-in page with enhanced behavior simulation.")
        
        # Enhanced scraping loop
        for account_name_to_search in TARGET_ACCOUNTS_FOR_SEARCH:
            account_tweets = scrape_twitter_account_advanced_search(
                selenium_driver, 
                account_name_to_search,
                SINCE_DATE,
                UNTIL_DATE
            )
            if account_tweets: 
                save_to_mongodb(account_tweets, mongodb_collection)
                
            print(f"Enhanced waiting before next account search or finishing...")
            # More realistic inter-account delay
            base_delay = 15.0 + (MAX_POSTS_PER_ACCOUNT * 0.1)
            human_like_sleep(base_delay, base_delay * 0.3, 'exponential')
            enhanced_human_like_mouse_move(selenium_driver, complexity='high')

        print("\n--- Enhanced Scraping with MongoDB Storage Finished ---")
        
    except Exception as e:
        print(f"\nAn OVERALL ENHANCED SCRIPT ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if selenium_driver: 
            print("Closing Enhanced Selenium WebDriver.")
            selenium_driver.quit()
