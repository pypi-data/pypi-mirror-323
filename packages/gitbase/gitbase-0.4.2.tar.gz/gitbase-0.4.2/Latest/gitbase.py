import requests
import json
import base64
import os
from cryptography.fernet import Fernet
from typing import Optional, Tuple, Union, Dict, Any, List
from altcolor import colored_text
from datetime import datetime
from time import sleep as wait

# Define a variable to check if data is loaded/has been found before continuing to try to update any class instances
loaded_data: bool = False

print(colored_text("BLUE", "\n\nThanks for using GitBase! Check out our other products at 'https://tairerullc.vercel.app'\n\n"))

# Define a function to check if the user is online
def is_online(url='http://www.google.com', timeout=5) -> bool:
    """Check if the user is online before continuing code"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        print(colored_text("YELLOW", "Network is offline."))
        return False

# Get the value of 'loaded_data'
def data_loaded() -> bool:
    """Get the value of 'loaded_data'"""
    return loaded_data

class GitBase:
    def __init__(self, token: str, repo_owner: str, repo_name: str, branch: str = 'main') -> None:
        self.token: str = token
        self.repo_owner: str = repo_owner
        self.repo_name: str = repo_name
        self.branch: str = branch
        self.headers: Dict[str, str] = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _get_file_url(self, path: str) -> str:
        """Reterive GitHub url for file"""
        return f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"

    def _get_file_content(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get the content of a file"""
        url: str = self._get_file_url(path)
        response: requests.Response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            file_data: Dict[str, Union[str, bytes]] = response.json()
            sha: str = file_data['sha']
            content: str = base64.b64decode(file_data['content']).decode('utf-8')
            return content, sha
        return None, None

    def read_data(self, path: str) -> Tuple[Optional[str], Optional[str]]:
        """Read a file and return it's data as content and sha"""
        content, sha = self._get_file_content(path)
        return content, sha

    def write_data(self, path: str, data: str, message: str = "Updated data") -> int:
        """Write to/update a file's content"""
        try:
            url: str = self._get_file_url(path)
            content, sha = self._get_file_content(path)
            encoded_data: str = base64.b64encode(data.encode('utf-8')).decode('utf-8')

            payload: Dict[str, Union[str, None]] = {
                "message": message,
                "content": encoded_data,
                "branch": self.branch
            }

            if sha:
                payload["sha"] = sha

            response: requests.Response = requests.put(url, headers=self.headers, json=payload)
            return response.status_code
        except Exception as e:
            print(colored_text("RED", f"Error: {e}"))
            return 500

    def delete_data(self, path: str, message: str = "Deleted data") -> int:
        """Delete data for a file"""
        try:
            url: str = self._get_file_url(path)
            _, sha = self._get_file_content(path)

            if sha:
                payload: Dict[str, str] = {
                    "message": message,
                    "sha": sha,
                    "branch": self.branch
                }
                response: requests.Response = requests.delete(url, headers=self.headers, json=payload)
                return response.status_code
            else:
                return 404
        except Exception as e:
            print(colored_text("RED", f"Error: {e}"))
            return 500

    @staticmethod
    def generate_example() -> None:
        """Generate an example of how to use GitBase"""
        # Get the directory of the current file (gitbase.py)
        current_dir = os.path.dirname(__file__)
        
        # Construct the full path to example.py
        example_file_path = os.path.join(current_dir, "example.py")
        
        # Read from test.py
        with open(example_file_path, "rb") as file:
            example_code: bytes = file.read()
        
        # Write to example_code.py
        with open("example_code.py", "wb") as file:
            file.write(example_code)

    def get_file_last_modified(self, path: str) -> Optional[float]:
        """Get the last modified timestamp of the file from the GitHub repository."""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits?path={path}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                commits = response.json()
                if commits:
                    # Get the date of the most recent commit
                    last_modified = commits[0]['commit']['committer']['date']
                    return datetime.strptime(last_modified, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        except Exception as e:
            print(colored_text("RED", f"Error getting last modified time for {path}: {e}"))
        return None

class PlayerDataSystem:
    def __init__(self, db: GitBase, encryption_key: bytes) -> None:
        self.db: GitBase = db
        self.encryption_key: bytes = encryption_key
        self.fernet: Fernet = Fernet(self.encryption_key)

    def encrypt_data(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode('utf-8'))

    def decrypt_data(self, encrypted_data: bytes) -> str:
        return self.fernet.decrypt(encrypted_data).decode('utf-8')

    def save_account(self, username: str, player_instance: Any, encryption: bool, attributes: Optional[List[str]] = None) -> None:
        """Saves player data, but please note offline data uses forced encryption to protect developer integrity"""
        try:
            if attributes:
                player_data: Dict[str, Union[str, int, float]] = {var: getattr(player_instance, var) for var in attributes if hasattr(player_instance, var)}
            else:
                player_data: Dict[str, Union[str, int, float]] = {var: getattr(player_instance, var) for var in player_instance.__dict__}

            if encryption:
                encrypted_data: bytes = self.encrypt_data(json.dumps(player_data)).decode('utf-8')
            else:
                encrypted_data: bytes = json.dumps(player_data)
            path: str = f"players/{username}.json"

            if is_online():
                response_code = self.db.write_data(path, encrypted_data, message=f"Saved data for {username}")
                if response_code == 201:
                    print(colored_text("GREEN", f"Successfully saved online data for {username}."))
                else:
                    print(colored_text("RED", f"Error saving online data for {username}. HTTP Status: {response_code}"))
            else:
                print(colored_text("YELLOW", "Network is offline, saving to offline backup version."))
                self.save_offline(username, player_instance, attributes)
        except Exception as e:
            print(colored_text("RED", f"Error: {e}"))
            print(colored_text("GREEN", "Attempting to save to offline backup version anyway."))
            self.save_offline(username, player_instance, attributes)

    def save_offline(self, username: str, player_instance: Any, attributes: Optional[List[str]] = None) -> None:
        """If offile data exists save to it"""
        if not os.path.exists("gitbase/players"):
            os.makedirs("gitbase/players")

        if attributes:
            player_data: Dict[str, Union[str, int, float]] = {var: getattr(player_instance, var) for var in attributes if hasattr(player_instance, var)}
        else:
            player_data: Dict[str, Union[str, int, float]] = {var: getattr(player_instance, var) for var in player_instance.__dict__}

        encrypted_data: bytes = self.encrypt_data(json.dumps(player_data))
        path: str = os.path.join("gitbase/players", f"{username}.gitbase")

        try:
            with open(path, "wb") as file:
                file.write(encrypted_data)
            print(colored_text("GREEN", f"Successfully saved offline backup for {username}."))
        except Exception as e:
            print(colored_text("RED", f"Error: {e}"))

    def load_account(self, username: str, player_instance: Any, encryption: bool) -> None:
        """Load player data from a GitBase and apply it to a class"""
        global loaded_data
        try:
            path: str = f"players/{username}.json"
            if is_online():
                online_data, _ = self.db.read_data(path)
                offline_path: str = f"gitbase/players/{username}.gitbase"
                if os.path.exists(offline_path):
                    offline_data_exists = True
                else:
                    offline_data_exists = False

                if online_data:
                    online_timestamp = self.db.get_file_last_modified(path)
                    if offline_data_exists:
                        offline_timestamp = os.path.getmtime(offline_path)

                    if offline_data_exists and offline_timestamp > online_timestamp:
                        print(colored_text("GREEN", f"Loading offline backup for {username} (newer version found)."))
                        self.load_offline(username, player_instance)
                    else:
                        print(colored_text("GREEN", f"Loading online data for {username}."))
                        # Apply online data to player_instance
                        decrypted_data = self.decrypt_data(online_data)
                        player_data = json.loads(decrypted_data)
                        for key, value in player_data.items():
                            setattr(player_instance, key, value)
                        loaded_data = True
                elif offline_data_exists:
                    print(colored_text("YELLOW", "Network down, loading from offline backup."))
                    self.load_offline(username, player_instance)
                else:
                    print(colored_text("RED", "No data found online or offline."))
            else:
                print(colored_text("YELLOW", "No network. Loading from offline data."))
                self.load_offline(username, player_instance)
        except Exception as e:
            print(colored_text("RED", f"Error loading account: {e}"))

    def load_offline(self, username: str, player_instance: Any) -> None:
        """If offline data exists load it"""
        global loaded_data
        path: str = os.path.join("gitbase/players", f"{username}.gitbase")
        try:
            if os.path.exists(path):
                with open(path, "rb") as file:
                    encrypted_data = file.read()
                decrypted_data: str = self.decrypt_data(encrypted_data)
                player_data: Dict[str, Union[str, int, float]] = json.loads(decrypted_data)
                for var, value in player_data.items():
                    setattr(player_instance, var, value)
                print(colored_text("GREEN", f"Successfully loaded offline backup for {username}."))
                loaded_data = True
            else:
                print(colored_text("RED", f"No offline backup found for {username}."))
                loaded_data = False
        except Exception as e:
            print(colored_text("RED", f"Error loading offline backup: {e}"))
            loaded_data = False

    def delete_account(self, username: str, delete_offline: bool = False) -> int:
        """Deletes the specified player account file from the online database and optionally from offline storage."""
        path: str = f"players/{username}.json"

        # Delete from the online database
        try:
            response_code = self.db.delete_data(path, message=f"Deleted account for {username}")
            if response_code == 204:
                print(colored_text("GREEN", f"Successfully deleted online account for {username}."))
            elif response_code == 404:
                print(colored_text("RED", f"No online account found for {username}."))
            else:
                print(colored_text("RED", f"Error deleting online account for {username}. HTTP Status: {response_code}"))
        except Exception as e:
            print(colored_text("RED", f"Error deleting online account: {e}"))

        # Delete from offline storage if requested
        if delete_offline:
            offline_path = os.path.join("gitbase/players", f"{username}.gitbase")
            if os.path.exists(offline_path):
                os.remove(offline_path)
                print(colored_text("GREEN", f"Successfully deleted offline backup for {username}."))
            else:
                print(colored_text("RED", f"No offline backup found for {username}."))

    def get_all(self) -> Dict[str, Any]:
        """Retrieve all player accounts stored in the system."""
        all_players = {}

        if is_online():
            try:
                # List all player files in the GitHub repository (assumed to be in a specific folder)
                path = "players"  # Add your specific path logic if necessary
                response = requests.get(self.db._get_file_url(path), headers=self.db.headers)
                
                if response.status_code == 200:
                    files = response.json()
                    for file in files:
                        if file['name'].endswith('.json'):
                            online_data, _ = self.db.read_data(file['name'])
                            if online_data:
                                username = file['name'].rsplit('.', 1)[0]  # Remove '.json'
                                decrypted_content = self.decrypt_data(online_data.encode('utf-8'))
                                player_data = json.loads(decrypted_content)
                                all_players[username] = player_data
                else:
                    print(colored_text("RED", f"Error retrieving player files from online database. HTTP Status: {response.status_code}"))
            except Exception as e:
                print(colored_text("RED", f"Error retrieving online player data: {e}"))
        else:
            print(colored_text("YELLOW", "Network is offline, loading player data from local storage."))
            # Load all offline data
            for filename in os.listdir("gitbase/players"):
                if filename.endswith('.gitbase'):
                    username = filename.rsplit('.', 1)[0]  # Remove '.gitbase'
                    player_data = self.load_offline(username)
                    if player_data:
                        all_players[username] = player_data

        return all_players

class DataSystem:
    def __init__(self, db: GitBase, encryption_key: bytes) -> None:
        self.db: GitBase = db
        self.encryption_key: bytes = encryption_key
        self.fernet: Fernet = Fernet(self.encryption_key)

    def encrypt_data(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode('utf-8'))

    def decrypt_data(self, encrypted_data: bytes) -> str:
        return self.fernet.decrypt(encrypted_data).decode('utf-8')

    def save_data(self, key: str, value: Any, encryption: bool = False) -> None:
        """Saves data, please note offline data uses forced encryption"""
        try:
            if encryption:
                data: bytes = self.encrypt_data(json.dumps(value)).decode('utf-8')
            else:
                data: bytes = json.dumps(value)
            path: str = f"data/{key}.json"

            if is_online():
                response_code = self.db.write_data(path, data, message=f"Saved {key}")
                if response_code == 201:
                    print(colored_text("GREEN", f"Successfully saved online data for {key}."))
                else:
                    print(colored_text("RED", f"Error saving online data for {key}. HTTP Status: {response_code}"))
            else:
                print(colored_text("YELLOW", "Network is offline, saving to offline backup version."))
                self.save_offline(key, value)
        except Exception as e:
            print(colored_text("RED", f"Error: {e}"))
            print(colored_text("GREEN", "Attempting to save to offline backup version anyway."))
            self.save_offline(key, value)

    def save_offline(self, key: str, value: Any) -> None:
        os.makedirs("gitbase/data", exist_ok=True)

        data: bytes = self.encrypt_data(json.dumps(value))
        path: str = os.path.join("gitbase/data", f"{key}.gitbase")

        try:
            with open(path, "wb") as file:
                file.write(data)
            print(colored_text("GREEN", f"Successfully saved offline backup for {key}."))
        except Exception as e:
            print(colored_text("RED", f"Error: {e}"))

    def load_data(self, key: str, encryption: bool) -> Optional[Any]:
        path: str = f"data/{key}.json"
        
        try:
            # Attempt to load online data if network is available
            if is_online():
                online_data, online_timestamp = self.db.read_data(path)
                if online_data:
                    if encryption:
                        decrypted_data: str = self.decrypt_data(online_data.encode('utf-8'))
                    else:
                        decrypted_data: str = online_data.encode('utf-8')
                    
                    # Create Data object with the loaded online data
                    class Data:
                        def __init__(self, key, value):
                            self.key = key
                            self.value = value
                    
                    obj = Data(key, json.loads(decrypted_data))
                    return obj
                
                print(colored_text("RED", f"No online data found for {key}."))
            else:
                # Fallback to offline data loading when offline
                print(colored_text("YELLOW", "Network is offline, loading from offline backup."))
                return self.load_offline(key)
        
        except Exception as e:
            print(colored_text("RED", f"Error loading data: {e}"))
            return None

    def load_offline(self, key: str) -> Optional[Any]:
        path: str = os.path.join("gitbase/data", f"{key}.gitbase")
        
        try:
            # Read offline data from the specified path
            with open(path, "rb") as file:
                data = file.read()
            
            # Decrypt offline data
            decrypted_data: str = self.decrypt_data(data)
            
            # Create Data object with the loaded offline data
            class Data:
                def __init__(self, key, value):
                    self.key = key
                    self.value = value
            
            obj = Data(key, json.loads(decrypted_data))
            return obj
        
        except Exception as e:
            print(colored_text("RED", f"Error loading offline data for {key}: {e}"))
            return None
    
    def delete_data(self, key: str, delete_offline: bool = False) -> int:
        """Deletes the specified key-value file from the online database and optionally from offline storage."""
        path: str = f"data/{key}.json"

        # Delete from the online database
        try:
            response_code = self.db.delete_data(path, message=f"Deleted {key}")
            if response_code == 204:
                print(colored_text("GREEN", f"Successfully deleted online data for {key}."))
            elif response_code == 404:
                print(colored_text("RED", f"No online data found for {key}."))
            else:
                print(colored_text("RED", f"Error deleting online data for {key}. HTTP Status: {response_code}"))
        except Exception as e:
            print(colored_text("RED", f"Error deleting online data: {e}"))

        # Delete from offline storage if requested
        if delete_offline:
            offline_path = os.path.join("gitbase/data", f"{key}.gitbase")
            if os.path.exists(offline_path):
                os.remove(offline_path)
                print(colored_text("GREEN", f"Successfully deleted offline backup for {key}."))
            else:
                print(colored_text("RED", f"No offline backup found for {key}."))
        
    def get_all(self) -> Dict[str, Any]:
        """Retrieve all key-value pairs stored in the system."""
        all_data = {}
        if is_online():
            try:
                # List all files in the GitHub repository (assumed to be in a specific folder)
                path = "data"  # Add your specific path logic if necessary
                response = requests.get(self.db._get_file_url(path), headers=self.db.headers)
                if response.status_code == 200:
                    files = response.json()
                    for file in files:
                        if file['name'].endswith('.json'):
                            content, _ = self.db.read_data(file['name'])
                            if content:
                                key = file['name'].rsplit('.', 1)[0]  # Remove '.json'
                                decrypted_content = self.decrypt_data(content.encode('utf-8'))
                                all_data.update({key: json.loads(decrypted_content)})
                else:
                    print(colored_text("RED", f"Error retrieving files from online database. HTTP Status: {response.status_code}"))
            except Exception as e:
                print(colored_text("RED", f"Error retrieving online data: {e}"))
        else:
            print(colored_text("YELLOW", "Network is offline, loading data from local storage."))
            # Load all offline data
            for filename in os.listdir("gitbase/data"):
                if filename.endswith('.gitbase'):
                    key = filename.rsplit('.', 1)[0]  # Remove '.gitbase'
                    all_data.update({key: self.load_offline(key)})

        return all_data