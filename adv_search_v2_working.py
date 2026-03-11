import time
import random
import sqlite3
import re
from urllib.parse import quote # For URL encoding query parameters
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

# --- Playwright Import ---
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Configuration ---
TWITTER_USERNAME = "Twitter_Username"  # Replace with your Twitter username/email
TWITTER_PASSWORD = "Twitter_pwd"  # Replace with your Twitter password

TARGET_ACCOUNTS_FOR_SEARCH = ["ecb"] # Accounts to search for
# --- Date Range for Advanced Search ---
# Format: "YYYY-MM-DD"
SINCE_DATE = "2025-04-09"
UNTIL_DATE = "2025-06-09"
# --- End Date Range ---

MAX_POSTS_PER_ACCOUNT = 1 # Max posts per account *within the date range*
DATABASE_NAME = "ecb_1.db"

# --- Bright Data Proxy Configuration ---
# Replace with your actual Bright Data credentials and Proxy Manager/Super Proxy details
USE_BRIGHTDATA_PROXY = False # Set to False to disable proxy usage for testing
BRIGHTDATA_PROXY_HOST = "brd.superproxy.io" # Or your Proxy Manager host e.g., "127.0.0.1"
BRIGHTDATA_PROXY_PORT = 22225 # Or your Proxy Manager port e.g., 24000
BRIGHTDATA_USERNAME = "brd-customer-YOUR_CUSTOMER_ID-zone-YOUR_ZONE" # Replace!
BRIGHTDATA_PASSWORD = "YOUR_ZONE_PASSWORD" # Replace!

# --- Helper to construct Bright Data proxy URL for Selenium ---
def get_brightdata_proxy_string():
    if USE_BRIGHTDATA_PROXY:
        return f"http://{BRIGHTDATA_USERNAME}:{BRIGHTDATA_PASSWORD}@{BRIGHTDATA_PROXY_HOST}:{BRIGHTDATA_PROXY_PORT}"
    return None

# --- Helper to construct Bright Data proxy dict for Playwright ---
def get_playwright_proxy_config():
    if USE_BRIGHTDATA_PROXY:
        return {
            "server": f"http://{BRIGHTDATA_PROXY_HOST}:{BRIGHTDATA_PROXY_PORT}",
            "username": BRIGHTDATA_USERNAME,
            "password": BRIGHTDATA_PASSWORD
        }
    return None

# --- Selenium: Humane Touch Helper (same as your last version) ---
def selenium_human_like_mouse_move(driver, num_moves=None, move_range=None):
    if num_moves is None: num_moves = random.randint(2, 5)
    if move_range is None: move_range = random.randint(30, 80)
    actions = ActionChains(driver)
    try:
        body_element = driver.find_element(By.TAG_NAME, "body")
        for _ in range(num_moves):
            actions.move_to_element_with_offset(body_element,
                                                random.randint(0, body_element.size['width'] // 2),
                                                random.randint(0, body_element.size['height'] // 2))
            actions.pause(random.uniform(0.1, 0.3))
        actions.move_by_offset(random.randint(-move_range, move_range),
                               random.randint(-move_range, move_range))
        actions.perform()
    except Exception: pass

# --- Playwright: Login Function with Manual Intervention & Proxy ---
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
            # ... (rest of Playwright context and page setup - same as your v6) ...
            ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.uniform(530, 540):.2f} (KHTML, like Gecko) Chrome/{random.uniform(100, 110):.2f}.0.{random.randint(5000,6000)}.{random.randint(100,200)} Safari/{random.uniform(530, 540):.2f}"
            context_args = {
                "user_agent": ua,
                "viewport": {"width": 1280 + random.randint(0,100), "height": 720 + random.randint(0,100)},
                "device_scale_factor": random.choice([1, 1.5, 2]),
                "locale": random.choice(["en-US", "en-GB"]),
                "timezone_id": random.choice(["America/New_York", "Europe/London", "America/Los_Angeles"])
            }
            # No need to pass proxy to new_context if passed to launch options for the browser
            context = browser.new_context(**context_args)
            page = context.new_page()
            
            print("Playwright: Starting automated login steps...")
            page.goto("https://twitter.com/login", timeout=90000) # Increased timeout for proxy
            page.wait_for_timeout(random.uniform(3000, 5000))

            # ... (Automated login steps - username, next, intermediate, password, login click - same as your v6) ...
            username_field = page.locator("input[name='text']").first
            if not username_field.is_visible(timeout=15000): raise Exception("Playwright: Username field not found.")
            username_field.hover(); username_field.click(delay=random.uniform(30,100)); username_field.type(username, delay=random.uniform(100, 250))
            page.wait_for_timeout(random.uniform(500, 1000))
            next_button = page.locator("//div[@role='button'][.//span[contains(text(),'Next')]] | //button[.//span[contains(text(),'Next')]]").first
            if next_button.is_visible(timeout=7000): next_button.hover(); next_button.click(delay=random.uniform(50,150))
            else: username_field.press("Enter")
            print("Playwright: Username submitted.")
            page.wait_for_timeout(random.uniform(3000, 5000))
            inter_input = page.locator("input[data-testid='ocfEnterTextTextInput'] | //input[@name='text' and @type='text' and not(@autocomplete='username')]").first
            try:
                if inter_input.is_visible(timeout=5000):
                    label_text = inter_input.get_attribute("aria-label") or ""
                    if "username" in label_text.lower() or "phone" in label_text.lower() or "challenge" in label_text.lower():
                        print("Playwright: Potential verification step found.")
                        inter_input.hover(); inter_input.type(username, delay=random.uniform(100,200))
                        page.wait_for_timeout(random.uniform(500, 1000))
                        inter_next_button = page.locator("//div[@role='button'][.//span[contains(text(),'Next')]] | //button[.//span[contains(text(),'Next')]]").first
                        if inter_next_button.is_visible(timeout=3000): inter_next_button.hover(); inter_next_button.click(delay=random.uniform(50,150))
                        else: inter_input.press("Enter")
                        print("Playwright: Verification info submitted.")
                        page.wait_for_timeout(random.uniform(2500, 4000))
            except PlaywrightTimeoutError: pass
            password_field = page.locator("input[name='password']").first
            if not password_field.is_visible(timeout=15000): raise Exception("Playwright: Password field not found.")
            password_field.hover(); password_field.type(password, delay=random.uniform(100, 250))
            page.wait_for_timeout(random.uniform(500, 1000))
            login_button = page.locator("//div[@data-testid='LoginForm_Login_Button'] | //div[@role='button'][.//span[contains(text(),'Log in')]] | //button[.//span[contains(text(),'Log in')]]").first
            if login_button.is_visible(timeout=7000): login_button.hover(); login_button.click(delay=random.uniform(50,150))
            else: password_field.press("Enter")
            print("Playwright: Password submitted. Automated steps complete.")

            # ... (Wait for Home Page / Manual Intervention logic - same as your v6) ...
            print("\nPlaywright: Waiting for navigation to Twitter home page (https://x.com/home)...") # x.com now
            print("IMPORTANT: If login stuck, complete MANUALLY in Playwright browser. Waiting up to 5 mins.\n")
            try:
                page.wait_for_url("https://x.com/home", timeout=300000)
                print("Playwright: Successfully navigated to /home.")
            except PlaywrightTimeoutError:
                print("Playwright: Timed out waiting for /home."); print("Current URL:", page.url)
                if "login" in page.url or "checkpoint" in page.url or "challenge" in page.url:
                    print("Login incomplete. Complete manually in Playwright browser.")
                    input("If NOW done, press Enter to extract cookies. Else, Ctrl+C...")
                    if "home" not in page.url.lower(): print("Still not on /home. Failed."); browser.close(); return None
                    print("Playwright: Proceeding after manual prompt.")
                else:
                    print("Ambiguous state. Check Playwright browser."); input("If logged in, Enter. Else, Ctrl+C...");
                    if "home" not in page.url.lower(): print("Still not on /home. Failed."); browser.close(); return None
            cookies = context.cookies(); print("Playwright: Login successful, cookies extracted.")
            if browser.is_connected(): browser.close()
            return cookies
        except Exception as e:
            print(f"Playwright: Critical error during login: {e}")
            # ... (Manual intervention after error - same as your v6) ...
            if page:
                print("\nIMPORTANT: Attempt to complete login MANUALLY in Playwright browser. Waiting up to 5 mins for /home.\n")
                try:
                    page.wait_for_url("https://x.com/home", timeout=300000)
                    print("Playwright: Navigated to /home after manual intervention."); cookies = context.cookies()
                    if browser.is_connected(): browser.close(); return cookies
                except PlaywrightTimeoutError: print("Timed out for /home after error + manual intervention.");
                except Exception as e_manual: print(f"Error during manual wait: {e_manual}")
            if browser and browser.is_connected(): browser.close()
            return None
        finally:
            if browser and browser.is_connected():
                try: browser.close()
                except Exception: pass

# --- Selenium: WebDriver Setup with Proxy ---
def get_selenium_webdriver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu"); chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.uniform(530, 540):.2f} (KHTML, like Gecko) Chrome/{random.uniform(95, 105):.2f}.0.{random.randint(4000,5000)}.{random.randint(100,200)} Safari/{random.uniform(530, 540):.2f}")
    
    proxy_string = get_brightdata_proxy_string()
    if proxy_string:
        chrome_options.add_argument(f'--proxy-server={proxy_string}')
        print(f"Selenium using proxy: {proxy_string.split('@')[1] if '@' in proxy_string else proxy_string}") # Avoid printing creds

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(random.uniform(8, 12))
    return driver

# --- Database, Save Data, Parse Engagement, Get Engagement (All same as previous) ---
def setup_database():
    conn = sqlite3.connect(DATABASE_NAME); cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tweets (id INTEGER PRIMARY KEY AUTOINCREMENT, author_name TEXT, tweet_text TEXT, post_url TEXT UNIQUE, post_time TEXT, likes INTEGER, replies INTEGER, reposts INTEGER, views INTEGER, engagement DECIMAL(12,8) DEFAULT 0.0, scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit(); conn.close()

def save_to_database(tweet_data_list): # Same as your V6
    if not tweet_data_list: return
    conn = sqlite3.connect(DATABASE_NAME); cursor = conn.cursor(); saved_count = 0
    for tweet in tweet_data_list:
        try:
            cursor.execute('''INSERT OR IGNORE INTO tweets (author_name, tweet_text, post_url, post_time, likes, replies, reposts, views, engagement) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (tweet['author'], tweet['text'], tweet['url'], tweet['time'], tweet['likes'], tweet['replies'], tweet['reposts'], tweet['views'], tweet.get('engagement', 0.0)))
            if cursor.rowcount > 0: saved_count +=1
        except sqlite3.Error as e: print(f"DB Error: {e} for {tweet.get('url', 'N/A')}")
    conn.commit(); conn.close()
    print(f"Attempted {len(tweet_data_list)} tweets. {saved_count} new added.")

def parse_engagement_number(s_num): # Same as your V6
    s_num = str(s_num).strip().replace(',', ''); multiplier = 1; original_s_num = s_num
    if not s_num: return 0
    if 'K' in s_num.upper(): multiplier = 1000; s_num = s_num.upper().replace('K', '')
    elif 'M' in s_num.upper(): multiplier = 1000000; s_num = s_num.upper().replace('M', '')
    try:
        if not s_num or (not s_num[0].isdigit() and s_num[0] != '.'):
            if original_s_num.isalpha(): return 0
            if not s_num or not s_num.replace('.', '', 1).isdigit(): return 0
        return int(float(s_num) * multiplier)
    except ValueError: return 0

def get_engagement_via_aria(article_soup, keyword): # Same as your V6, ensure keyword "Replies" is "Reply" in call
    pattern = re.compile(rf"\b{keyword}(s)?\b", re.IGNORECASE)
    for el in article_soup.find_all(True, attrs={'aria-label': lambda x: x and pattern.search(x)}):
        aria_text = el.get('aria-label', '')
        if count_match := re.search(r"([\d,.\sKM]+)\s+\b" + f"{keyword}(s)?\\b", aria_text, re.IGNORECASE):
            if (parsed_val := parse_engagement_number(count_match.group(1).strip().replace(" ", ""))) >= 0: return parsed_val
        el_testid = el.get('data-testid', '').lower(); keyword_lower = keyword.lower()
        if el_testid == keyword_lower or el_testid == f"un{keyword_lower}" or (keyword_lower == "reply" and el_testid == "reply"):
            if count_container := el.find('div', attrs={'data-testid': 'app-text-transition-container'}):
                if text_content := count_container.get_text(strip=True): return parse_engagement_number(text_content)
    return 0

# --- Function to Construct Advanced Search URL ---
def construct_advanced_search_url(account_name, since_date, until_date):
    """Constructs a Twitter advanced search URL."""
    # Base URL for search
    base_url = "https://x.com/search"
    # Query parts
    query_parts = []
    if account_name:
        query_parts.append(f"(from%3A{account_name})")
    if until_date:
        query_parts.append(f"until%3A{until_date}")
    if since_date:
        query_parts.append(f"since%3A{since_date}")
    
    # Join query parts with spaces (which will be URL encoded)
    query_string = "%20".join(query_parts)
    
    # URL encode the query string and add ?q=
    # Also add &f=live to get the "Latest" tweets tab
    # Twitter now uses x.com, but twitter.com for search still often redirects or works
    # Using src=typed_query seems to be a common parameter now too.
    # The `f=live` is important for chronological order.
    # Sometimes it's `f=tweets` or `vertical=tweets` or `src= reciente` (spanish for recent)
    # Testing shows `f=live` usually works for "Latest"
    if query_string:
        return f"{base_url}?q={query_string}&src=typed_query&f=live"
    return None # Or raise an error if no query parts

# --- Selenium: Twitter Scraping Logic for Advanced Search ---
def scrape_twitter_account_advanced_search(driver, account_to_search, since_date_str, until_date_str):
    search_url = construct_advanced_search_url(account_to_search, since_date_str, until_date_str)
    if not search_url:
        print(f"Could not construct search URL for {account_to_search}. Skipping.")
        return []

    print(f"\n--- Selenium: Advanced Searching for @{account_to_search} from {since_date_str} to {until_date_str} ---")
    print(f"Using URL: {search_url}")
    driver.get(search_url)
    time.sleep(random.uniform(6, 10)); selenium_human_like_mouse_move(driver) # Longer wait for search results
    
    tweets_collected, session_tweet_urls = [], set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts, MAX_SCROLL_ATTEMPTS = 0, 100 # Increased from your previous code
    consecutive_scrolls_no_new, CONSECUTIVE_NO_NEW_LIMIT = 0, random.randint(5, 8) # Slightly more patient for search
    consecutive_no_height_change, CONSECUTIVE_NO_HEIGHT_LIMIT = 0, random.randint(3, 5)

    # Note: The scrolling and content loading on search pages can be different
    # from profile pages. It might load tweets in chunks as you scroll.
    while len(tweets_collected) < MAX_POSTS_PER_ACCOUNT and scroll_attempts < MAX_SCROLL_ATTEMPTS:
        scroll_attempts += 1
        print(f"\nScroll attempt #{scroll_attempts} for search results. Collected: {len(tweets_collected)}/{MAX_POSTS_PER_ACCOUNT}")
        
        current_scroll_before = driver.execute_script("return window.scrollY;")
        # Using the scroll logic from your latest provided code (the one with the JS error)
        # but with the JS error fixed
        driver.execute_script(f"window.scrollBy(0, window.innerHeight * {random.uniform(2, 4)});")
        if random.random() < 0.25: selenium_human_like_mouse_move(driver, num_moves=random.randint(1,3))
        time.sleep(random.uniform(3.5, 5.5) + (scroll_attempts * random.uniform(0.05, 0.15))) # Slightly longer base sleep
        
        current_scroll_after = driver.execute_script("return window.scrollY;")
        if current_scroll_after <= current_scroll_before: # If no scroll or scrolled up
            print(f"  Scroll #{scroll_attempts}: No scroll change detected, attempting corrective scroll...")
            time.sleep(random.uniform(1.0, 2.0)); 
            target_scroll_retry = current_scroll_before + int(driver.execute_script("return window.innerHeight;") * random.uniform(0.7, 1.2)) 
            driver.execute_script(f"window.scrollTo(0, {target_scroll_retry});") # f-string for variable injection
            print(f"  Retried scroll to y={target_scroll_retry}")
            time.sleep(random.uniform(2.0, 3.0))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        newly_found_this_scroll_count = 0
        # Data extraction logic (same as before, but ensure author is correctly handled if not explicitly account_to_search)
        for article_idx, article in enumerate(soup.find_all('article', attrs={'data-testid': 'tweet'})):
            if len(tweets_collected) >= MAX_POSTS_PER_ACCOUNT: break
            tweet_data = {}
            try:
                # Author might not always be `account_to_search` if retweets appear despite `from:`
                # but `(from:...)` should be quite effective. We'll still parse it.
                user_name_div = article.find('div', attrs={'data-testid': 'User-Name'})
                parsed_author = None
                if user_name_div:
                    name_span = user_name_div.find('span', string=True)
                    if name_span: parsed_author = name_span.get_text(strip=True)
                    else:
                        parts = [s.get_text(strip=True) for s in user_name_div.find_all('span') if s.get_text(strip=True)]
                        if parts: parsed_author = parts[0]
                tweet_data['author'] = parsed_author if parsed_author else account_to_search # Default to searched account if not found
                tweet_data['text'] = (text_div.get_text(separator=' ', strip=True) if (text_div := article.find('div', attrs={'data-testid': 'tweetText'})) else "No text")
                tweet_data['time'] = (time_tag['datetime'] if (time_tag := article.find('time', attrs={'datetime': True})) else "Unknown Time")
                url_tag = (parent_a if (parent_a := (time_tag.find_parent('a', href=re.compile(r"/[^/]+/status/\d+")) if time_tag else None)) else (plausible_links[0] if (plausible_links := [l for l in article.find_all('a', href=re.compile(r"/[^/]+/status/\d+")) if 'analytics' not in l.get('href','').lower() and not l.find_parent('div',attrs={'data-testid':re.compile(r"tweetPhoto|tweetVideo",re.I)})]) else None))
                tweet_data['url'] = ("https://twitter.com" + url_tag['href'] if url_tag and url_tag.has_attr('href') else f"https://twitter.com/{account_to_search}/status/NO_URL_{int(time.time())}_{len(tweets_collected)}_{article_idx}")
                if "NO_URL" in tweet_data['url'] or tweet_data['url'] in session_tweet_urls: continue
                session_tweet_urls.add(tweet_data['url'])
                tweet_data['likes'] = get_engagement_via_aria(article, "Like")
                tweet_data['replies'] = get_engagement_via_aria(article, "Replies") 
                tweet_data['reposts'] = get_engagement_via_aria(article, "Repost")
                tweet_data['views'] = get_engagement_via_aria(article, "View")
                tweet_data['engagement'] = (( (tweet_data.get('likes',0) or 0) + (tweet_data.get('replies',0) or 0) + (tweet_data.get('reposts',0) or 0) ) / float(tweet_data['views'])) if tweet_data['views'] and tweet_data['views'] > 0 else 0.0
                tweets_collected.append(tweet_data); newly_found_this_scroll_count += 1
                print(f"  Collected ({len(tweets_collected)}/{MAX_POSTS_PER_ACCOUNT}): @{tweet_data.get('author','N/A')}... L:{tweet_data['likes']} Rep:{tweet_data['replies']} RP:{tweet_data['reposts']} V:{tweet_data['views']} E:{tweet_data['engagement']:.4f}")
            except Exception: pass
        
        print(f"  Scroll #{scroll_attempts}: Processed {len(soup.find_all('article', attrs={'data-testid': 'tweet'}))} articles, found {newly_found_this_scroll_count} new (matching author).")
        if newly_found_this_scroll_count == 0: consecutive_scrolls_no_new += 1
        else: consecutive_scrolls_no_new = 0
        current_page_height = driver.execute_script("return document.body.scrollHeight")
        if current_page_height == last_height: # Check total page height
            if newly_found_this_scroll_count == 0: consecutive_no_height_change += 1
        else: consecutive_no_height_change = 0 
        last_height = current_page_height
        if consecutive_scrolls_no_new >= CONSECUTIVE_NO_NEW_LIMIT or \
           consecutive_no_height_change >= CONSECUTIVE_NO_HEIGHT_LIMIT or \
           len(tweets_collected) >= MAX_POSTS_PER_ACCOUNT or \
           scroll_attempts >= MAX_SCROLL_ATTEMPTS:
            print(f"  Exiting scroll loop for @{account_to_search} search due to conditions."); break
    
    print(f"Finished scraping for @{account_to_search} between {since_date_str} and {until_date_str}. Collected {len(tweets_collected)} tweets.")
    return tweets_collected

# --- Main Execution ---
if __name__ == "__main__":
    if "YOUR_TWITTER" in TWITTER_USERNAME or "YOUR_TWITTER" in TWITTER_PASSWORD:
        print("!!! Please update TWITTER_USERNAME and TWITTER_PASSWORD in the script !!!"); exit()
    if USE_BRIGHTDATA_PROXY and ("YOUR_CUSTOMER_ID" in BRIGHTDATA_USERNAME or "YOUR_ZONE_PASSWORD" in BRIGHTDATA_PASSWORD):
        print("!!! Proxy is enabled but Bright Data credentials are placeholders. Update them or set USE_BRIGHTDATA_PROXY to False. !!!"); exit()

    print("Starting Twitter Advanced Search Scraper (Playwright Login + Selenium Scrape)...")
    print("WARNING: Scraping Twitter is against their ToS.")
    setup_database(); selenium_driver = None
    try:
        login_cookies = login_with_playwright(TWITTER_USERNAME, TWITTER_PASSWORD, headless_mode=False) 
        if not login_cookies: print("Failed to log in with Playwright. Exiting."); exit()
        
        print("Initializing Selenium WebDriver and loading cookies...")
        selenium_driver = get_selenium_webdriver()
        # It's crucial to go to the domain you want to set cookies for *before* adding them.
        selenium_driver.get("https://twitter.com/") # Base domain
        time.sleep(random.uniform(1.5, 3.0))

        for cookie in login_cookies:
            sel_cookie = {'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain'], 
                          'path': cookie['path'], 'secure': cookie['secure'], 'httpOnly': cookie['httpOnly']}
            if 'expires' in cookie and cookie['expires'] != -1 : sel_cookie['expiry'] = int(cookie['expires']) # Selenium uses 'expiry'
            # Handle SameSite carefully
            if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']:
                 if cookie['sameSite'] == 'None' and not cookie['secure']:
                     # print(f"Skipping SameSite=None for non-secure cookie: {cookie['name']}")
                     pass # Selenium might reject SameSite=None if cookie is not Secure
                 else:
                     sel_cookie['sameSite'] = cookie['sameSite']
            try: selenium_driver.add_cookie(sel_cookie)
            except Exception as e_cookie: print(f"Selenium: Error adding cookie {cookie['name']}: {e_cookie}")
        
        print("Cookies loaded. Navigating to a generic Twitter page to confirm session...")
        selenium_driver.get("https://x.com/home") # Use x.com for navigation now
        time.sleep(random.uniform(4, 7)); selenium_human_like_mouse_move(selenium_driver)

        if "login" in selenium_driver.current_url.lower() or "Login" in selenium_driver.title:
            print("Selenium: Still on login page or redirected. Login transfer might have failed.")
            print("Current URL for Selenium:", selenium_driver.current_url)
            print("Current Title for Selenium:", selenium_driver.title)
            input("Press Enter to attempt scraping anyway or Ctrl+C to abort...")
        else: print("Selenium: Successfully on a logged-in page (e.g., /home).")
        
        # Loop through target accounts for advanced search
        for account_name_to_search in TARGET_ACCOUNTS_FOR_SEARCH:
            account_tweets = scrape_twitter_account_advanced_search(
                selenium_driver, 
                account_name_to_search,
                SINCE_DATE,
                UNTIL_DATE
            )
            if account_tweets: save_to_database(account_tweets)
            
            print(f"Waiting before next account search or finishing..."); 
            time.sleep(random.uniform(15.0, 30.0 + (MAX_POSTS_PER_ACCOUNT * 0.1))) # Shorter multiplier as posts are already limited
            selenium_human_like_mouse_move(selenium_driver)

        print("\n--- Scraping Finished ---")
    except Exception as e:
        print(f"\nAn OVERALL SCRIPT ERROR: {e}"); import traceback; traceback.print_exc()
    finally:
        if selenium_driver: print("Closing Selenium WebDriver."); selenium_driver.quit()
