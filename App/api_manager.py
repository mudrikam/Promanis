import os
import json
from pathlib import Path


class APIKeyManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.config_path = self.base_dir / "App" / "config" / "config.json"
        self.api_keys_path = self.base_dir / "api_keys.txt"
        self.api_keys = []
        self.current_index = 0
        self.load_api_keys()
        self.load_config()
    
    def load_api_keys(self):
        if not self.api_keys_path.exists():
            raise FileNotFoundError(f"File api_keys.txt tidak ditemukan di {self.api_keys_path}!")
        
        try:
            with open(self.api_keys_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                self.api_keys = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
                
            if not self.api_keys:
                raise ValueError("File api_keys.txt kosong atau tidak berisi API key yang valid!")
                
            print(f"Loaded {len(self.api_keys)} API keys from {self.api_keys_path}")
            
        except Exception as e:
            raise ValueError(f"Gagal membaca file api_keys.txt: {str(e)}")
    
    def load_config(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    loaded_index = config.get('current_api_key_index', 0)
                    if 0 <= loaded_index < len(self.api_keys):
                        self.current_index = loaded_index
                    else:
                        self.current_index = 0
            except (json.JSONDecodeError, KeyError, ValueError):
                self.current_index = 0
        else:
            self.current_index = 0
    
    def save_config(self):
        try:
            os.makedirs(self.config_path.parent, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({'current_api_key_index': self.current_index}, f, indent=4)
        except Exception as e:
            print(f"Warning: Failed to save config: {str(e)}")
    
    def get_next_api_key(self):
        if not self.api_keys:
            raise ValueError("Tidak ada API key yang tersedia!")
        
        if self.current_index >= len(self.api_keys):
            self.current_index = 0
        
        current_key = self.api_keys[self.current_index]
        
        if not current_key or current_key.strip() == "":
            raise ValueError(f"API key pada index {self.current_index} kosong atau tidak valid!")
        
        print(f"Using API key index: {self.current_index}")
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        self.save_config()
        
        return current_key.strip()
    
    def get_total_keys(self):
        return len(self.api_keys)
    
    def reset_index(self):
        self.current_index = 0
        self.save_config()
