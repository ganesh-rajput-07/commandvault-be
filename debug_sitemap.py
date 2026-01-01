import os
import django
import sys

# Add project root to path
sys.path.append('/home/ganesh-rajput/Desktop/CommandVault-Project-Full-stack/CommandVault')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commandvault.settings')
django.setup()

from vault.sitemaps import PromptSitemap, UserSitemap, StaticSitemap

def check_sitemaps():
    print("--- Checking Sitemaps ---")
    
    # Check Static
    static_map = StaticSitemap()
    static_items = static_map.items()
    print(f"Static Sitemap Items: {len(static_items)}")
    for item in static_items:
        print(f" - {static_map.location(item)}")

    # Check Prompts
    prompt_map = PromptSitemap()
    try:
        prompt_items = prompt_map.items()
        count = prompt_items.count()
        print(f"\nPrompt Sitemap Items: {count}")
        if count > 0:
            print(f" - First item: {prompt_map.location(prompt_items[0])}")
        else:
            print(" - query:", prompt_items.query)
    except Exception as e:
        print(f"Error checking prompts: {e}")

    # Check Users
    user_map = UserSitemap()
    try:
        user_items = user_map.items()
        count = user_items.count()
        print(f"\nUser Sitemap Items: {count}")
        if count > 0:
            print(f" - First item: {user_map.location(user_items[0])}")
    except Exception as e:
        print(f"Error checking users: {e}")

if __name__ == '__main__':
    check_sitemaps()
