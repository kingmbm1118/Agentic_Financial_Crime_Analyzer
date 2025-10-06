"""
Quick test to verify Hugging Face token authentication
"""
from huggingface_hub import login, whoami
from dotenv import load_dotenv
import os

# Load token from .env file
load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')

print("Testing Hugging Face authentication...")
print("="*60)

if not HF_TOKEN:
    print("[ERROR] No HF_TOKEN found in .env file")
    print("\nPlease check that:")
    print("  1. .env file exists in the project root")
    print("  2. .env file contains: HF_TOKEN=your_token_here")
    exit(1)

print(f"[OK] Token loaded from .env file (length: {len(HF_TOKEN)})")

try:
    # Login with token
    login(token=HF_TOKEN, add_to_git_credential=False)
    print("[OK] Successfully authenticated with Hugging Face")

    # Get user info
    user_info = whoami()
    print(f"[OK] Logged in as: {user_info['name']}")
    print(f"[OK] Token type: {user_info.get('auth', {}).get('type', 'Unknown')}")

    print("\n" + "="*60)
    print("Authentication successful! You can now run:")
    print("  python main.py")
    print("="*60)

except Exception as e:
    print(f"[ERROR] Authentication failed: {e}")
    print("\nPlease check:")
    print("  1. Token is valid")
    print("  2. Token has 'read' permissions")
    print("  3. You have internet connection")
