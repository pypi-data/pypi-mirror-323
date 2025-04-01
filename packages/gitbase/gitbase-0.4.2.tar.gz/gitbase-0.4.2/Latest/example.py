from gitbase import *
from cryptography.fernet import Fernet
import sys

# Generate an example of how to use gitbase [NOT NEEDED IF YOU ARE READING THIS]
GitBase.generate_example()

# Initialize GitHub database and encryption key
GITHUB_TOKEN = "YOUR_TOKEN"
REPO_OWNER = "YOUR_GITHUB_USERNAME"
REPO_NAME = "YOUR_REPO_NAME"
key = Fernet.generate_key()

db = GitBase(GITHUB_TOKEN, REPO_OWNER, REPO_NAME)
player_data_system = PlayerDataSystem(db, key)
data_system = DataSystem(db, key)

# Player instance with some attributes
class Player:
    def __init__(self, username, score, password):
        self.username = username
        self.score = score
        self.password = password

player = Player("john_doe", 100, "123")

# Save specific attributes of the player instance
player_data_system.save_account(username="john_doe", player_instance=player, encryption=True, attributes=["username", "score", "password"])

# Load player data
player_data_system.load_account(username="john_doe", player_instance=player, encryption=True)

# Placeholder functions
def load_game():
    print("Cool game text")

def main_menu():
    sys.exit()

# Check if there is a valid account before prompting for password
if data_loaded():
    if player.password == input("Enter your password: "):
        print("Correct!")
        load_game()
    else:
        print("Incorrect password!")
        main_menu()

# Save a piece of data using a key and value pair
data_system.save_data(key="key_name", value=69, encryption=True)

# Load the value of a specific key by its name
key_1 = data_system.load_data(key="key_name", encryption=True)

# Print the value
print(key_1.value)

# Print the key
print(key_1.key)

# Get all key-value pairs
print(data_system.get_all())

# Delete data
data_system.delete_data(key="key_name")

# Delete account
player_data_system.delete_account(username="john_doe")