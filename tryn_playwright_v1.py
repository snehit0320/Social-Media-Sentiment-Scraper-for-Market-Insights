import time
import random
import sqlite3
import re
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
TWITTER_USERNAME = "Twitter_Username"
TWITTER_PASSWORD = "Twitter_pwd"
TARGET_ACCOUNTS = ["Bloomberg"]
MAX_POSTS_PER_ACCOUNT = 125 # Maximum posts to scrape per account
DATABASE_NAME = "twitter_data_bloomberg.db" # New DB name

# --- Selenium: Humane Touch Helper ---
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

# --- Playwright: Login Function with Manual Intervention ---
def login_with_playwright(username, password, headless_mode=False, proxy_server=None):
    print("Attempting login with Playwright...")
    with sync_playwright() as p:
        browser_options = {"headless": headless_mode}
        if proxy_server:
            browser_options["proxy"] = {"server": proxy_server}
        
        browser = None # Initialize browser to None for robust finally block
        try:
            browser = p.chromium.launch(**browser_options)
            ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.uniform(530, 540):.2f} (KHTML, like Gecko) Chrome/{random.uniform(100, 110):.2f}.0.{random.randint(5000,6000)}.{random.randint(100,200)} Safari/{random.uniform(530, 540):.2f}"
            context = browser.new_context(
                user_agent=ua,
                viewport={"width": 1280 + random.randint(0,100), "height": 720 + random.randint(0,100)},
                device_scale_factor=random.choice([1, 1.5, 2]),
                locale=random.choice(["en-US", "en-GB"]),
                timezone_id=random.choice(["America/New_York", "Europe/London", "America/Los_Angeles"])
            )
            page = context.new_page()
            
            # --- Automated Login Steps ---
            print("Playwright: Starting automated login steps...")
            page.goto("https://twitter.com/login", timeout=60000)
            page.wait_for_timeout(random.uniform(2000, 4000))

            username_field = page.locator("input[name='text']").first
            if not username_field.is_visible(timeout=10000):
                raise Exception("Playwright: Username field not found or not visible.")
            username_field.hover()
            username_field.click(delay=random.uniform(30,100))
            username_field.type(username, delay=random.uniform(100, 250))
            page.wait_for_timeout(random.uniform(500, 1000))

            next_button = page.locator("//div[@role='button'][.//span[contains(text(),'Next')]] | //button[.//span[contains(text(),'Next')]]").first
            if next_button.is_visible(timeout=5000):
                next_button.hover(); next_button.click(delay=random.uniform(50,150))
            else: username_field.press("Enter")
            print("Playwright: Username submitted.")
            page.wait_for_timeout(random.uniform(2500, 4000))
            
            # Potential intermediate step (e.g., phone/username verification)
            inter_input = page.locator("input[data-testid='ocfEnterTextTextInput'] | //input[@name='text' and @type='text' and not(@autocomplete='username')]").first
            try:
                if inter_input.is_visible(timeout=3000): # Shorter timeout for optional field
                    label_text = inter_input.get_attribute("aria-label") or ""
                    if "username" in label_text.lower() or "phone" in label_text.lower() or "challenge" in label_text.lower():
                        print("Playwright: Potential verification step found.")
                        inter_input.hover(); inter_input.type(username, delay=random.uniform(100,200))
                        page.wait_for_timeout(random.uniform(500, 1000))
                        inter_next_button = page.locator("//div[@role='button'][.//span[contains(text(),'Next')]] | //button[.//span[contains(text(),'Next')]]").first
                        if inter_next_button.is_visible(timeout=2000):
                            inter_next_button.hover(); inter_next_button.click(delay=random.uniform(50,150))
                        else: inter_input.press("Enter")
                        print("Playwright: Verification info submitted.")
                        page.wait_for_timeout(random.uniform(2000, 3500))
            except PlaywrightTimeoutError: pass # It's okay if this field isn't present

            password_field = page.locator("input[name='password']").first
            if not password_field.is_visible(timeout=10000):
                 raise Exception("Playwright: Password field not found or not visible.")
            password_field.hover(); password_field.type(password, delay=random.uniform(100, 250))
            page.wait_for_timeout(random.uniform(500, 1000))
            
            login_button = page.locator("//div[@data-testid='LoginForm_Login_Button'] | //div[@role='button'][.//span[contains(text(),'Log in')]] | //button[.//span[contains(text(),'Log in')]]").first
            if login_button.is_visible(timeout=5000):
                login_button.hover(); login_button.click(delay=random.uniform(50,150))
            else: password_field.press("Enter")
            print("Playwright: Password submitted. Automated steps complete.")

            # --- Wait for Home Page / Manual Intervention ---
            print("\nPlaywright: Waiting for navigation to Twitter home page (https://twitter.com/home)...")
            print("IMPORTANT: If login seems stuck or requires 2FA, please complete it MANUALLY in the Playwright browser window.")
            print("The script will wait for up to 5 minutes.\n")
            
            try:
                page.wait_for_url("https://x.com/home", timeout=300000) # 5 minutes
                print("Playwright: Successfully navigated to /home.")
            except PlaywrightTimeoutError:
                print("Playwright: Timed out waiting for /home after 5 minutes.")
                print("Current URL:", page.url)
                if "login" in page.url or "checkpoint" in page.url or "challenge" in page.url:
                    print("Login still appears to be incomplete. Please ensure you are logged in fully on the Playwright browser.")
                    input("If you have NOW completed login manually, press Enter to attempt cookie extraction. Otherwise, Ctrl+C to abort...")
                    # Re-check URL after input, just in case manual login finished during input prompt
                    if "home" not in page.url.lower(): # Check again
                        print("Still not on /home after manual prompt. Login likely failed definitively.")
                        if browser.is_connected(): browser.close()
                        return None
                    print("Playwright: Proceeding after manual prompt, assuming /home is now reached.")
                else:
                    # Not on /home, but also not clearly on a login/error page.
                    print("Playwright: Not on /home, and not on a clear login/error page. This is ambiguous.")
                    print("Check the Playwright browser. If logged in, press Enter. Else, Ctrl+C.")
                    input("Press Enter to try extracting cookies, or Ctrl+C to abort...")
                    if "home" not in page.url.lower():
                         print("Still not on /home after second manual prompt. Aborting Playwright login.")
                         if browser.is_connected(): browser.close()
                         return None
            
            # If we reach here, we assume login is successful (either auto or manual)
            cookies = context.cookies()
            print("Playwright: Login successful (or assumed successful after manual step), cookies extracted.")
            if browser.is_connected(): browser.close()
            return cookies

        except Exception as e: # Catch broader exceptions during the automated steps
            print(f"Playwright: An critical error occurred during automated login steps: {e}")
            print("\nIMPORTANT: Please attempt to complete the login MANUALLY in the Playwright browser window.")
            print("The script will wait for up to 5 minutes for you to reach the Twitter home page (https://twitter.com/home).\n")
            if page: # Check if page object exists
                try:
                    page.wait_for_url("https://x.com/home", timeout=300000) # 5 minutes
                    print("Playwright: Successfully navigated to /home after manual intervention.")
                    cookies = context.cookies() # Assuming context is still valid
                    if browser.is_connected(): browser.close()
                    return cookies
                except PlaywrightTimeoutError:
                    print("Playwright: Timed out waiting for /home even after manual intervention prompt following an error.")
                    if browser and browser.is_connected(): browser.close()
                    return None
                except Exception as e_manual:
                    print(f"Playwright: Error during manual intervention wait: {e_manual}")
                    if browser and browser.is_connected(): browser.close()
                    return None
            else: # If page object was never created due to early error
                if browser and browser.is_connected(): browser.close()
                return None
        finally:
            if browser and browser.is_connected():
                # Ensure browser is closed if an unhandled exception occurs before explicit close
                # or if function returns early without closing.
                try:
                    browser.close()
                except Exception:
                    pass # Best effort to close

# --- Selenium: WebDriver Setup ---
def get_selenium_webdriver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu"); chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.uniform(530, 540):.2f} (KHTML, like Gecko) Chrome/{random.uniform(95, 105):.2f}.0.{random.randint(4000,5000)}.{random.randint(100,200)} Safari/{random.uniform(530, 540):.2f}")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(random.uniform(8, 12))
    return driver

# --- Database, Save Data, Parse Engagement, Get Engagement (All same as previous) ---
def setup_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, author_name TEXT, tweet_text TEXT,
            post_url TEXT UNIQUE, post_time TEXT, likes INTEGER, replies INTEGER,
            reposts INTEGER, views INTEGER, engagement DECIMAL(12,8) DEFAULT 0.0,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
    conn.commit(); conn.close()

def save_to_database(tweet_data_list):
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

def parse_engagement_number(s_num):
    s_num = str(s_num).strip().replace(',', ''); multiplier = 1
    if not s_num: return 0
    original_s_num = s_num
    if 'K' in s_num.upper(): multiplier = 1000; s_num = s_num.upper().replace('K', '')
    elif 'M' in s_num.upper(): multiplier = 1000000; s_num = s_num.upper().replace('M', '')
    try:
        if not s_num or (not s_num[0].isdigit() and s_num[0] != '.'):
            if original_s_num.isalpha(): return 0
            if not s_num or not s_num.replace('.', '', 1).isdigit(): return 0
        return int(float(s_num) * multiplier)
    except ValueError: return 0

def get_engagement_via_aria(article_soup, keyword):
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

# --- Selenium: Twitter Scraping Logic (using scrolling from your V4, no scroll-up) ---
def scrape_twitter_account(driver, account_username):
    print(f"\n--- Selenium: Scraping @{account_username} ---")
    driver.get(f"https://twitter.com/{account_username}")
    time.sleep(random.uniform(5, 8)); selenium_human_like_mouse_move(driver)
    tweets_collected, session_tweet_urls = [], set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts, MAX_SCROLL_ATTEMPTS = 0, 100
    consecutive_scrolls_no_new, CONSECUTIVE_NO_NEW_LIMIT = 0, random.randint(4, 6)
    consecutive_no_height_change, CONSECUTIVE_NO_HEIGHT_LIMIT = 0, random.randint(2, 4)
    current_scroll2 = driver.execute_script("return window.scrollY;")
    while len(tweets_collected) < MAX_POSTS_PER_ACCOUNT and scroll_attempts < MAX_SCROLL_ATTEMPTS:
        scroll_attempts += 1
        current_scroll = driver.execute_script("return window.scrollY;")
        driver.execute_script(f"""
            window.scrollBy({{
                top: window.innerHeight * {random.uniform(2, 4)},
                left: 0,
                behavior: 'smooth'
            }});
        """)
        if random.random() < 0.25: selenium_human_like_mouse_move(driver, num_moves=random.randint(1,3))
        time.sleep(random.uniform(3.0, 5.0) + (scroll_attempts * random.uniform(0.05, 0.15)))
        current_scroll2 = driver.execute_script("return window.scrollY;")
        if current_scroll2 <= current_scroll:
            print(f"  Scroll #{scroll_attempts}: No scroll change detected, retrying...")
            time.sleep(random.uniform(1.0, 2.0)); 
            target_scroll_retry = current_scroll + int(driver.execute_script("return window.innerHeight;") * random.uniform(0.5, 1.0)) 
            driver.execute_script(f"window.scrollTo(0, {target_scroll_retry});")
            print(f"  Retried scroll to y={target_scroll_retry}")
            time.sleep(random.uniform(1.5, 2.5)) # Wait after retry

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        newly_found_this_scroll_count = 0
        for article_idx, article in enumerate(soup.find_all('article', attrs={'data-testid': 'tweet'})):
            if len(tweets_collected) >= MAX_POSTS_PER_ACCOUNT: break
            tweet_data = {}
            try: # Data extraction logic (condensed for brevity, same as before)
                user_name_div = article.find('div', attrs={'data-testid': 'User-Name'})
                tweet_data['author'] = (name_span.get_text(strip=True) if (name_span := (user_name_div.find('span', string=True) if user_name_div else None)) else (parts[0] if (parts:=[s.get_text(strip=True) for s in user_name_div.find_all('span') if s.get_text(strip=True)]) else account_username)) if user_name_div else account_username
                tweet_data['text'] = (text_div.get_text(separator=' ', strip=True) if (text_div := article.find('div', attrs={'data-testid': 'tweetText'})) else "No text")
                tweet_data['time'] = (time_tag['datetime'] if (time_tag := article.find('time', attrs={'datetime': True})) else "Unknown Time")
                url_tag = (parent_a if (parent_a := (time_tag.find_parent('a', href=re.compile(r"/[^/]+/status/\d+")) if time_tag else None)) else (plausible_links[0] if (plausible_links := [l for l in article.find_all('a', href=re.compile(r"/[^/]+/status/\d+")) if 'analytics' not in l.get('href','').lower() and not l.find_parent('div',attrs={'data-testid':re.compile(r"tweetPhoto|tweetVideo",re.I)})]) else None))
                tweet_data['url'] = ("https://twitter.com" + url_tag['href'] if url_tag and url_tag.has_attr('href') else f"https://twitter.com/{account_username}/status/NO_URL_{int(time.time())}_{len(tweets_collected)}_{article_idx}")
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
        
        print(f"  Scroll #{scroll_attempts}: Processed {len(soup.find_all('article', attrs={'data-testid': 'tweet'}))} articles, found {newly_found_this_scroll_count} new.")
        if newly_found_this_scroll_count == 0: consecutive_scrolls_no_new += 1
        else: consecutive_scrolls_no_new = 0
        current_height = driver.execute_script("return document.body.scrollHeight")
        if current_height == last_height:
            if newly_found_this_scroll_count == 0: consecutive_no_height_change += 1
        else: consecutive_no_height_change = 0 
        last_height = current_height
        if consecutive_scrolls_no_new >= CONSECUTIVE_NO_NEW_LIMIT or \
           consecutive_no_height_change >= CONSECUTIVE_NO_HEIGHT_LIMIT or \
           len(tweets_collected) >= MAX_POSTS_PER_ACCOUNT or \
           scroll_attempts >= MAX_SCROLL_ATTEMPTS:
            print(f"  Exiting scroll loop for @{account_username} due to conditions."); break
    print(current_scroll2, "Final scroll positions.")
    return tweets_collected

# --- Main Execution ---
if __name__ == "__main__":
    if TWITTER_USERNAME == "YOUR_TWITTER_USERNAME" or TWITTER_PASSWORD == "YOUR_TWITTER_PASSWORD":
        print("!!! Please update TWITTER_USERNAME and TWITTER_PASSWORD !!!"); exit()
    print("Starting Twitter Scraper (Playwright Login + Selenium Scrape V6)...")
    print("WARNING: Scraping Twitter is against their ToS.")
    setup_database(); selenium_driver = None
    try:
        login_cookies = login_with_playwright(TWITTER_USERNAME, TWITTER_PASSWORD, headless_mode=False) 
        if not login_cookies: print("Failed to log in with Playwright. Exiting."); exit()
        print("Initializing Selenium WebDriver and loading cookies...")
        selenium_driver = get_selenium_webdriver()
        selenium_driver.get("https://twitter.com/") 
        time.sleep(random.uniform(1,2.5))
        for cookie in login_cookies:
            sel_cookie = {'name': cookie['name'], 'value': cookie['value'], 'domain': cookie['domain'], 
                          'path': cookie['path'], 'secure': cookie['secure'], 'httpOnly': cookie['httpOnly']}
            if 'expires' in cookie and cookie['expires'] != -1 : sel_cookie['expiry'] = int(cookie['expires'])
            if 'sameSite' in cookie and cookie['sameSite'] in ['Strict', 'Lax', 'None']:
                 if not (cookie['sameSite'] == 'None' and not cookie['secure']): sel_cookie['sameSite'] = cookie['sameSite']
            try: selenium_driver.add_cookie(sel_cookie)
            except Exception as e: print(f"Selenium: Error adding cookie {cookie['name']}: {e}")
        print("Cookies loaded. Navigating to home...")
        selenium_driver.get("https://x.com/home") 
        time.sleep(random.uniform(4, 7)); selenium_human_like_mouse_move(selenium_driver)
        if "login" in selenium_driver.current_url.lower():
            print("Selenium: Still on login page. Login transfer might have failed.")
            input("Press Enter to attempt scraping anyway or Ctrl+C to abort...")
        else: print("Selenium: Successfully on a logged-in page (presumably /home).")
        for account in TARGET_ACCOUNTS:
            account_tweets = scrape_twitter_account(selenium_driver, account)
            if account_tweets: save_to_database(account_tweets)
            print(f"Waiting before next account..."); 
            time.sleep(random.uniform(15.0, 30.0 + (MAX_POSTS_PER_ACCOUNT * 0.2))) 
            selenium_human_like_mouse_move(selenium_driver)
        print("\n--- Scraping Finished ---")
    except Exception as e:
        print(f"\nAn OVERALL SCRIPT ERROR: {e}"); import traceback; traceback.print_exc()
    finally:
        if selenium_driver: print("Closing Selenium WebDriver."); selenium_driver.quit()
