import requests
import json
import time
from datetime import datetime, timedelta
from colorama import Fore, Style, init

init(autoreset=True)

def print_welcome_message():
    print(Fore.WHITE + r"""
 ____  _   _    _    ____   _____        __
/ ___|| | | |  / \  |  _ \ / _ \ \      / /
\___ \| |_| | / _ \ | | | | | | \ \ /\ / / 
 ___) |  _  |/ ___ \| |_| | |_| |\ V  V /  
|____/|_| |_/_/   \_\____/ \___/  \_/\_/   
 ____   ____ ____  ___ ____ _____ _____ ____  ____  
/ ___| / ___|  _ \|_ _|  _ \_   _| ____|  _ \/ ___| 
\___ \| |   | |_) || || |_) || | |  _| | |_) \___ \ 
 ___) | |___|  _ < | ||  __/ | | | |___|  _ < ___) |
|____/ \____|_| \_\___|_|    |_| |_____|_| \_\____/ 
          """)
    print(Fore.GREEN + Style.BRIGHT + "Shadow Scripters Cat Gold Miner Bot")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/shadowscripters")

def load_accounts():
    with open('data.txt', 'r') as file:
        return [line.strip() for line in file if line.strip()]

def login(authorization):
    url = "https://api-server1.catgoldminer.ai/auth/login"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {"refBy": ""}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_profile(authorization):
    url = "https://api-server1.catgoldminer.ai/users/getProfile2"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_all_social_quests(authorization):
    url = "https://api-server1.catgoldminer.ai/quest/getAllSocialQuestAndStatus"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_all_daily_quests(authorization):
    url = "https://api-server1.catgoldminer.ai/quest/getAllDailyQuestAndStatus"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def claim_quest(authorization, action_code, quest_type, quest_value):
    url = "https://api-server1.catgoldminer.ai/quest/claimQuest"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "actionCode": action_code,
        "questType": quest_type,
        "questValue": quest_value
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def do_telegram_quest(authorization, action_code, quest_value):
    url = "https://api-server1.catgoldminer.ai/quest/doTelegramQuest"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "actionCode": action_code,
        "questValue": quest_value
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_offline_currency(authorization, mine_id, location_id):
    url = "https://api-server1.catgoldminer.ai/users/getOfflineCurrency"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "mineID": mine_id,
        "locationID": location_id
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def claim_offline_currency(authorization, mine_id, location_id):
    url = "https://api-server1.catgoldminer.ai/users/claimOfflineCurrency2"
    headers = {
        "authorization": f"tma {authorization}",
        "content-type": "application/json"
    }
    payload = {
        "mineID": mine_id,
        "locationID": location_id,
        "isClaimWithHardCurrency": False,
        "hashSoftCurrencyProfile": None
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def process_quests(authorization):
    # Get all daily and social quests
    daily_quests = get_all_daily_quests(authorization)
    social_quests = get_all_social_quests(authorization)

    if daily_quests['code'] != 0 or social_quests['code'] != 0:
        print(Fore.RED + "Failed to retrieve quest data.")
        return

    # Combine all quests (daily and social)
    all_quests = daily_quests['data'] + social_quests['data']

    for quest in all_quests:
        # Check if the quest has already been claimed
        if quest.get('claimStatus', False):
            print(Fore.YELLOW + f"Quest already claimed: {quest['questDescription']}. Skipping.")
            continue

        # Check time validity if required
        if quest.get('isCheckTimeValidQuest', False) and quest.get('timeValidQuest', 0) > 0:
            # Ensure 'claimDate' is available before trying to use it
            if 'claimDate' in quest:
                current_time = time.time()
                quest_time_start = datetime.fromisoformat(quest['claimDate'].replace('Z', ''))  # Get start time
                time_valid = quest.get('timeValidQuest', 0)  # duration in seconds

                # Validate if the quest time is still valid
                if (current_time - quest_time_start.timestamp()) > time_valid:
                    print(Fore.YELLOW + f"Quest time expired: {quest['questDescription']}. Skipping.")
                    continue
            else:
                print(Fore.YELLOW + f"Quest does not have claimDate, skipping time validation: {quest['questDescription']}.")

        # Get actionCode, questValue, and questType from the response
        action_code = quest['actionCode']
        quest_value = quest['questValue']
        quest_type = quest.get('questType', 0)  # Get questType from response, default to 0 if not present

        # Perform the quest first using do_telegram_quest
        do_quest_result = do_telegram_quest(authorization, action_code, quest_value)
        if do_quest_result['code'] != 0:
            print(Fore.RED + f"Failed to complete quest: {quest['questDescription']}.")
            continue
        print(Fore.GREEN + f"Quest successfully completed: {quest['questDescription']}.")

        # After the quest is completed, claim the quest
        claim_result = claim_quest(authorization, action_code, quest_type, quest_value)  # Using questType from data
        if claim_result['code'] == 0:
            print(Fore.GREEN + f"Successfully claimed quest: {quest['questDescription']}.")
        else:
            print(Fore.RED + f"Failed to claim quest: {quest['questDescription']}.")

def process_account(authorization, account_number, total_accounts):
    print(Fore.CYAN + f"\nProcessing account {account_number}/{total_accounts}")
    
    # Login
    login_data = login(authorization)
    if login_data['code'] != 0:
        print(Fore.RED + "Login failed. Continuing to next account.")
        return

    user_id = login_data['data']['userID']
    user_name = login_data['data']['name']
    assign_location = login_data['data']['assignLocation']
    last_login_date = login_data['data']['lastLoginDate']
    
    print(Fore.GREEN + f"Login successful.")
    print(Fore.YELLOW + f"User ID: {user_id}")
    print(Fore.YELLOW + f"Name: {user_name}")
    print(Fore.YELLOW + f"Location: {assign_location}")
    print(Fore.YELLOW + f"Last Login: {last_login_date}")

    # Get user profile
    profile_data = get_profile(authorization)
    if profile_data['code'] != 0:
        print(Fore.RED + "Failed to get profile. Continuing to next account.")
        return

    total_currency = profile_data['data']['totalSoftCurrency']
    print(Fore.YELLOW + f"Total Currency: {total_currency}")

    # Process all quests
    process_quests(authorization)

    # Get and claim offline currency based on the correct location
    offline_currency = get_offline_currency(authorization, 0, assign_location)
    if offline_currency['code'] == 0:
        print(Fore.YELLOW + f"Offline currency: {offline_currency['data']}")
        claim_result = claim_offline_currency(authorization, 0, assign_location)
        print(Fore.GREEN + f"Offline currency claim status: {'Successful' if claim_result['code'] == 0 else 'Failed'}.")
    else:
        print(Fore.RED + "Failed to get offline currency.")

def main():
    print_welcome_message()
    accounts = load_accounts()
    total_accounts = len(accounts)
    print(Fore.CYAN + f"Total accounts: {total_accounts}")

    while True:
        for i, authorization in enumerate(accounts, 1):
            process_account(authorization, i, total_accounts)
            if i < total_accounts:
                print(Fore.YELLOW + "Waiting 5 seconds before processing the next account...")
                time.sleep(5)

        print(Fore.MAGENTA + "\nAll accounts have been processed. Waiting about 2 hours before restarting...")
        countdown_time = datetime.now() + timedelta(days=0.084)
        
        while datetime.now() < countdown_time:
            remaining_time = countdown_time - datetime.now()
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            print(f"\rTime remaining: {hours:02d}:{minutes:02d}:{seconds:02d}", end="", flush=True)
            time.sleep(1)

        print("\nRestarting the process...")

if __name__ == "__main__":
    main()