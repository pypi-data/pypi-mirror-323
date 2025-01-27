import os
from pathlib import Path

# Always save the .env file to the parent directory of the package
env_path = Path(__file__).resolve().parent.parent / '.env'

# Function to update or add the API_KEY in the .env file
def update_or_add_api_key(new_api_key):
    # Check if the .env file exists; if not, create it
    if not os.path.exists(env_path):
        os.makedirs(os.path.dirname(env_path), exist_ok=True)

    # Read the current contents of the .env file
    with open(env_path, "r") as env_file:
        lines = env_file.readlines()

    # Flag to check if the API_KEY is found and updated
    api_key_updated = False

    # Update the API_KEY if it exists, otherwise append a new key
    with open(env_path, "w") as env_file:
        for line in lines:
            # Check if the line starts with 'API_KEY='
            if line.startswith("API_KEY="):
                env_file.write(f"API_KEY={new_api_key}\n")
                api_key_updated = True
            else:
                env_file.write(line)
        
        # If API_KEY was not found, append the new key
        if not api_key_updated:
            env_file.write(f"API_KEY={new_api_key}\n")

    print(f"API_KEY has been {'updated' if api_key_updated else 'added'} in the .env file.")

# tldr_setup: Entry point for setting up or updating the API_KEY
def tldr_setup():
    # Ask user for the new API_KEY (or obtain it from another source)
    new_api_key = input("Enter the new API_KEY: ").strip()

    # Call the function to update or add the API_KEY
    update_or_add_api_key(new_api_key)

def main():
    tldr_setup()

# Example usage
if __name__ == "__main__":
    tldr_setup()
