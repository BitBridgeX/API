import time
import json
from hashlib import sha256

class PersistentMemoryLogicLoop:
    def __init__(self, memory_timeout=300, max_memory_size=1024):
        """
        Initialize the Persistent Memory Logic Loop (PMLL).
        
        :param memory_timeout: Time in seconds for memory to expire (default: 300 seconds).
        :param max_memory_size: Maximum number of memory entries to retain.
        """
        self.memory = {}
        self.memory_timeout = memory_timeout
        self.max_memory_size = max_memory_size
    
    def _hash_key(self, key):
        """
        Generate a unique hash for a given key.
        """
        return sha256(key.encode()).hexdigest()
    
    def add_to_memory(self, key, value):
        """
        Add a new entry to the memory store.
        
        :param key: A unique identifier for the memory (e.g., user ID or session ID).
        :param value: The data to associate with the key.
        """
        current_time = time.time()
        hashed_key = self._hash_key(key)
        
        # Add to memory or update existing entry
        self.memory[hashed_key] = {
            "timestamp": current_time,
            "data": value
        }
        
        # Prune memory if it exceeds the maximum size
        if len(self.memory) > self.max_memory_size:
            self._prune_memory()
    
    def get_from_memory(self, key):
        """
        Retrieve memory associated with a key if it's still valid.
        
        :param key: The unique identifier for the memory.
        :return: The data associated with the key, or None if expired/not found.
        """
        hashed_key = self._hash_key(key)
        current_time = time.time()
        
        if hashed_key in self.memory:
            entry = self.memory[hashed_key]
            if current_time - entry["timestamp"] <= self.memory_timeout:
                return entry["data"]
            else:
                # Expire the memory entry
                del self.memory[hashed_key]
        return None
    
    def _prune_memory(self):
        """
        Prune memory to ensure the store size stays within max_memory_size.
        """
        # Sort memory by timestamp (oldest first)
        sorted_memory = sorted(self.memory.items(), key=lambda x: x[1]["timestamp"])
        
        # Remove oldest entries until within the limit
        while len(self.memory) > self.max_memory_size:
            oldest_key = sorted_memory.pop(0)[0]
            del self.memory[oldest_key]
    
    def save_memory(self, filename="persistent_memory.json"):
        """
        Save the current memory state to a file for persistence.
        
        :param filename: The file to save memory data.
        """
        with open(filename, "w") as file:
            json.dump(self.memory, file)
    
    def load_memory(self, filename="persistent_memory.json"):
        """
        Load memory state from a file.
        
        :param filename: The file containing saved memory data.
        """
        try:
            with open(filename, "r") as file:
                self.memory = json.load(file)
        except FileNotFoundError:
            self.memory = {}

# Example Usage
if __name__ == "__main__":
    pmll = PersistentMemoryLogicLoop(memory_timeout=600, max_memory_size=500)
    
    # Add memory
    pmll.add_to_memory("user_123", {"conversation": "Hello, how are you?"})
    
    # Retrieve memory
    memory = pmll.get_from_memory("user_123")
    print("Retrieved Memory:", memory)
    
    # Save and load memory
    pmll.save_memory()
    pmll.load_memory()
