import requests
import sys
import threading
import json
import re
import phonenumbers
import asyncio
from getpass import getpass
from telethon.sync import TelegramClient, functions
from telethon.tl import types
from phonenumbers import geocoder, carrier
from playwright.sync_api import sync_playwright

# --- ANSI Colors for Beautification ---
C = "\033[96m"  # Cyan
G = "\033[92m"  # Green
R = "\033[91m"  # Red
Y = "\033[93m"  # Yellow
W = "\033[0m"   # White / Reset
B = "\033[1m"   # Bold

if len(sys.argv) != 2:
    print(f"{R}[!] Usage: python3 enum3.py <number>{W}")
    sys.exit(1)

number = sys.argv[1]
results = []

def get_headers(referer=""):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive",
        "Referer": referer
    }

# --- 1. Flipkart Module ---
def check_flipkart(number, result):
    try:
        num = f"+91{number}"
        url = "https://2.rome.api.flipkart.com/api/6/user/signup/status"
        
        headers = get_headers("https://www.flipkart.com/")
        headers.update({
            "Content-Type": "application/json",
            "X-User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0 FKUA/website/42/website/Desktop",
            "Origin": "https://www.flipkart.com"
        })
        payload = {"loginId": [num], "supportAllStates": True}
        
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if res.status_code == 200:
            status = res.json().get("RESPONSE", {}).get("userDetails", {}).get(num, "")
            if status == "VERIFIED":
                result.append({"Flipkart": f"{G}Registered (True){W}"})
            elif status == "NOT_FOUND":
                result.append({"Flipkart": f"{R}Not Registered (False){W}"})
            else:
                result.append({"Flipkart": f"{Y}Unknown Response{W}"})
        else:
            result.append({"Flipkart": f"{R}Blocked (Status: {res.status_code}){W}"})
    except Exception as e:
        result.append({"Flipkart": f"{R}Error: {str(e)}{W}"})

# --- 2. Swiggy Module ---
def check_swiggy(number, result):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(user_agent=get_headers()["User-Agent"])
            page = context.new_page()
            page.goto("https://www.swiggy.com", wait_until="networkidle")

            js_code = f"""
            async () => {{
                let res = await fetch('https://www.swiggy.com/dapi/auth/signin-with-check', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json', '__fetch_req__': 'true', 'Platform': 'dweb' }},
                    body: JSON.stringify({{ mobile: '{number}', password: '', _csrf: window._csrfToken }})
                }});
                return await res.json();
            }}
            """
            response_json = page.evaluate(js_code)
            is_registered = response_json.get("data", {}).get("registered")
            
            if is_registered is True:
                result.append({"Swiggy": f"{G}Registered (True){W}"})
            elif is_registered is False:
                result.append({"Swiggy": f"{R}Not Registered (False){W}"})
            else:
                result.append({"Swiggy": f"{Y}Unknown Response{W}"})
            browser.close()
    except Exception as e:
        result.append({"Swiggy": f"{R}Error: {str(e)}{W}"})

# --- 3. Twitter Module ---
def check_twitter(number, result):
    try:
        base_url = "https://twitter.com/account/begin_password_reset"
        session = requests.Session()
        headers = get_headers("https://twitter.com/")
        res = session.get(base_url, headers=headers, timeout=10)
        
        auth_match = re.search(r'<input type="hidden" name="authenticity_token" value="([^"]*)">', res.text)
        if not auth_match:
            result.append({"Twitter": f"{R}Blocked (No CSRF Token){W}"})
            return
            
        data = {"authenticity_token": auth_match.group(1), "account_identifier": number}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        
        res = session.post(base_url, data=data, headers=headers, allow_redirects=False, timeout=10)
        if res.status_code == 302 and "send_password_reset" in str(res.headers.get("location")):
            result.append({"Twitter": f"{G}Registered (True){W}"})
        else:
            result.append({"Twitter": f"{R}Not Registered (False){W}"})
    except Exception as e:
        result.append({"Twitter": f"{R}Error: {str(e)}{W}"})

# --- 4. Cellular Intelligence ---
def check_cellular(number, result):
    try:
        parsed_number = phonenumbers.parse(f"+91{number}")
        if phonenumbers.is_valid_number(parsed_number):
            circle = geocoder.description_for_number(parsed_number, "en") or "India"
            operator_name = carrier.name_for_number(parsed_number, "en") or "Unknown Operator"
            result.append({"Cellular Data": f"{C}{operator_name} - {circle}{W}"})
        else:
            result.append({"Cellular Data": f"{R}Invalid Number{W}"})
    except Exception as e:
        result.append({"Cellular Data": f"{R}Error: {str(e)}{W}"})

# --- 5. Telegram OSINT Module ---
def get_human_readable_user_status(status):
    if isinstance(status, types.UserStatusOnline): return "Currently online"
    elif isinstance(status, types.UserStatusOffline): return status.was_online.strftime("%Y-%m-%d %H:%M:%S") if getattr(status, 'was_online', None) else "Offline"
    elif isinstance(status, types.UserStatusRecently): return "Last seen recently"
    elif isinstance(status, types.UserStatusLastWeek): return "Last seen last week"
    elif isinstance(status, types.UserStatusLastMonth): return "Last seen last month"
    return "Unknown"

async def _telegram_logic(number):
    api_id = YOUR API_ID
    api_hash = "YOUR_API_HASH"
    session_name = "cybercop_session" 
    client = TelegramClient(session_name, api_id, api_hash)
    
    await client.connect()
    if not await client.is_user_authorized():
        await client.disconnect()
        return f"{R}Auth Required! Need to login first.{W}"

    try:
        contact = types.InputPhoneContact(client_id=0, phone=f"+91{number}", first_name="", last_name="")
        contacts = await client(functions.contacts.ImportContactsRequest([contact]))
        
        users = contacts.users

        if len(users) == 0:
            res = f"{R}Not Registered or Private{W}"
        else:
            raw_user = users[0]
            
            await client(functions.contacts.DeleteContactsRequest(id=[raw_user.id])) 
            
            u_id = raw_user.id
            u_user = f"@{raw_user.username}" if raw_user.username else "None"
            
            f_name = raw_user.first_name or ""
            l_name = raw_user.last_name or ""
            name = f"{f_name} {l_name}".strip() if (f_name or l_name) else "Unknown"
            
            phone = raw_user.phone or "Hidden/None"
            status = get_human_readable_user_status(raw_user.status)
            verified = raw_user.verified
            bot = raw_user.bot
            
            sp = "\n" + (" " * 22) 
            res = f"{G}Found!{W}"
            res += f"{sp}{C}├─ ID{W}       : {u_id}"
            res += f"{sp}{C}├─ Name{W}     : {name}"
            res += f"{sp}{C}├─ Username{W} : {u_user}"
            res += f"{sp}{C}├─ Phone{W}    : {phone}"
            res += f"{sp}{C}├─ Status{W}   : {status}"
            res += f"{sp}{C}├─ Verified{W} : {verified}"
            res += f"{sp}{C}└─ Bot{W}      : {bot}"
            
    except Exception as e:
        res = f"{R}Error: {str(e)}{W}"
    
    await client.disconnect() 
    return res

def check_telegram(number, result):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tg_result = loop.run_until_complete(_telegram_logic(number))
        result.append({"Telegram": tg_result})
        loop.close()
    except Exception as e:
        result.append({"Telegram": f"{R}Error: {str(e)}{W}"})

# --- Main Execution ---
if __name__ == "__main__":
    print(f"\n{B}{C}[*] CYBERCOP OSINT INITIALIZED [*]{W}")
    print(f"{Y}[~] Scanning targets for : +91 {number}{W}\n")
    
    threads = []
    
    threads.append(threading.Thread(target=check_flipkart, args=(number, results)))
    threads.append(threading.Thread(target=check_swiggy, args=(number, results)))
    threads.append(threading.Thread(target=check_twitter, args=(number, results)))
    threads.append(threading.Thread(target=check_cellular, args=(number, results)))
    threads.append(threading.Thread(target=check_telegram, args=(number, results)))

    for thread in threads:
        thread.start()
        
    for thread in threads:
        thread.join()
        
    print(f"{B}{C}="*55)
    print(f"       OSINT REPORT FOR: +91 {number}")
    print("="*55 + f"{W}")
    
    final_dict = {}
    for r in results:
        final_dict.update(r)
        
    for key, value in final_dict.items():
        print(f" {B}[+]{W} {key:<15}: {value}")
        
    print(f"{B}{C}="*55 + f"{W}\n")
