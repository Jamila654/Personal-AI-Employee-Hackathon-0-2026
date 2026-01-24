# import os
# import time
# from pathlib import Path
# from playwright.sync_api import sync_playwright

# # --- 1. CONFIGURATION ---
# VAULT_BASE = Path.cwd()
# APPROVED_FOLDER = VAULT_BASE / "Approved"
# DONE_FOLDER = VAULT_BASE / "Done"
# SESSION_DIR = VAULT_BASE / "playwright_session"

# # Ensure directories exist
# os.makedirs(APPROVED_FOLDER, exist_ok=True)
# os.makedirs(DONE_FOLDER, exist_ok=True)

# def post_to_linkedin(content):
#     success = False
#     with sync_playwright() as p:
#         print("Launching browser with persistent session...")
#         context = p.chromium.launch_persistent_context(
#             user_data_dir=str(SESSION_DIR),
#             headless=False, 
#             slow_mo=1000,   
#         )
        
#         page = context.pages[0] if context.pages else context.new_page()
#         page.set_viewport_size({"width": 1280, "height": 720})
        
#         print("Navigating to LinkedIn...")
#         page.goto("https://www.linkedin.com/feed/")

#         # Check if login is needed
#         if "login" in page.url:
#             print("--- ACTION REQUIRED: Please log in manually ---")
#             page.wait_for_url("**/feed/**", timeout=0) 
#             print("Login successful!")

#         try:
#             # 3. CLICK 'START A POST'
#             print("Finding 'Start a post' button...")
#             post_trigger = page.get_by_role("button", name="Start a post")
#             if not post_trigger.is_visible():
#                  post_trigger = page.locator(".share-mb__trigger")
            
#             post_trigger.wait_for(state="visible", timeout=10000)
#             post_trigger.click()
#             print("Clicked Start Post!")

#             # 4. FILL THE CONTENT (Targeting the placeholder from your screenshot)
#             print("Entering content...")
            
#             # This matches the "What do you want to talk about?" text in your image
#             try:
#                 # Look for the exact placeholder text visible in your screenshot
#                 editor_placeholder = page.get_by_text("What do you want to talk about?")
#                 editor_placeholder.wait_for(state="visible", timeout=10000)
                
#                 # Click it to ensure the focus is in the right spot
#                 editor_placeholder.click()
#                 print("Clicked placeholder, now typing...")
                
#                 # Using keyboard.type mimics human entry letter-by-letter
#                 page.keyboard.type(content)
#                 print("Content entered successfully.")
                
#             except Exception as e:
#                 print("Primary text-search failed, trying backup selectors...")
#                 # Fallback to the code-level selectors if the text-search fails
#                 editor = page.locator("div[role='textbox'], div.ql-editor").first
#                 editor.click()
#                 page.keyboard.type(content)

#             # 5. CLICK POST
#             print("Submitting post...")
#             # exact=True ensures we don't accidentally click 'Post settings'
#             submit_btn = page.get_by_role("button", name="Post", exact=True)
#             submit_btn.wait_for(state="visible", timeout=5000)
            
#             # Check if button is enabled (sometimes it takes a second after typing)
#             if submit_btn.is_enabled():
#                 submit_btn.click()
#                 print("✅ Successfully posted to LinkedIn!")
#                 page.wait_for_timeout(5000) 
#                 success = True
#             else:
#                 print("❌ Post button was disabled. Content might not have entered correctly.")
#                 success = False
            
#         except Exception as e:
#             print(f"❌ Error during posting: {e}")
#             page.screenshot(path="debug_error.png")
#             print("Check 'debug_error.png' to see what the robot saw.")
#             success = False
        
#         finally:
#             context.close()
#             print("Browser closed.")
#     return success

# # --- 2. MAIN EXECUTION LOOP ---
# if __name__ == "__main__":
#     print("--- LinkedIn Robot Poster Active ---")
    
#     # Check for .md files in Approved folder
#     files = [f for f in os.listdir(APPROVED_FOLDER) if f.endswith(".md")]
    
#     if not files:
#         print("Nothing found in 'Approved' folder.")
#     else:
#         print(f"Found {len(files)} files to process.")
#         for filename in files:
#             file_path = APPROVED_FOLDER / filename
#             done_path = DONE_FOLDER / filename
            
#             with open(file_path, "r", encoding="utf-8") as f:
#                 post_body = f.read()
                
#             print(f"Current Task: {filename}")
#             if post_to_linkedin(post_body):
#                 os.rename(file_path, done_path)
#                 print(f"Moved {filename} to Done folder.")
#             else:
#                 print(f"Keeping {filename} in Approved folder for retry.")

#     print("--- Robot Task Complete ---")

import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# --- 1. CONFIGURATION ---
VAULT_BASE = Path.cwd()
APPROVED_FOLDER = VAULT_BASE / "Approved"
DONE_FOLDER = VAULT_BASE / "Done"
SESSION_DIR = VAULT_BASE / "playwright_session"

os.makedirs(APPROVED_FOLDER, exist_ok=True)
os.makedirs(DONE_FOLDER, exist_ok=True)

def sanitize_content(text):
    """Automatically removes common robot labels and markdown stars."""
    labels = ["**Headline:**", "**Body:**", "**Call to Action:**", "**Hashtags:**", "Headline:", "Body:"]
    clean_text = text
    for label in labels:
        clean_text = clean_text.replace(label, "")
    return clean_text.replace("**", "").strip()

def post_to_linkedin(content):
    success = False
    clean_text = sanitize_content(content)
    
    with sync_playwright() as p:
        print("Launching browser...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False, 
            slow_mo=1000,   
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        page.set_viewport_size({"width": 1280, "height": 720})
        
        try:
            print("Navigating to LinkedIn...")
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")

            if "login" in page.url:
                print("--- ACTION REQUIRED: Please log in manually ---")
                page.wait_for_url("**/feed/**", timeout=0) 

            # 3. CLICK 'START A POST'
            print("Opening post box...")
            post_trigger = page.get_by_role("button", name="Start a post")
            if not post_trigger.is_visible():
                 post_trigger = page.locator(".share-mb__trigger")
            
            post_trigger.click(timeout=10000)

            # 4. FILL THE CONTENT
            print("Entering content...")
            try:
                # Use the placeholder text you saw in your screenshot
                editor = page.get_by_text("What do you want to talk about?")
                editor.wait_for(state="visible", timeout=5000)
                editor.click()
            except:
                # Fallback to the code-level selector
                page.locator("div[role='textbox'], div.ql-editor").first.click()
                
            page.keyboard.type(clean_text)
            print("Content typed.")

            # 5. CLICK POST
            print("Submitting post...")
            submit_btn = page.get_by_role("button", name="Post", exact=True)
            submit_btn.wait_for(state="visible", timeout=5000)
            
            if submit_btn.is_enabled():
                submit_btn.click()
                print("✅ Successfully posted to LinkedIn!")
                page.wait_for_timeout(3000) # Short wait for upload
                success = True
            
        except Exception as e:
            print(f"❌ Error during posting: {e}")
            # Only screenshot if the page is still open
            if not page.is_closed():
                page.screenshot(path="debug_error.png")
        finally:
            context.close()
            print("Browser closed.")
    return success

# --- 2. MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    print("--- LinkedIn Robot Poster Active ---")
    files = [f for f in os.listdir(APPROVED_FOLDER) if f.endswith(".md")]
    
    if not files:
        print("Nothing found in 'Approved' folder.")
    else:
        for filename in files:
            file_path = APPROVED_FOLDER / filename
            with open(file_path, "r", encoding="utf-8") as f:
                post_body = f.read()
                
            print(f"Current Task: {filename}")
            if post_to_linkedin(post_body):
                os.rename(file_path, DONE_FOLDER / filename)
                print(f"Moved {filename} to Done folder.")

    print("--- Robot Task Complete ---")