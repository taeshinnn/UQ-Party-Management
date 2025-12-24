import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class QueueManager:
    def __init__(self, party_size: int = 4, parties_needed: int = 2):
        self.party_size = party_size
        self.parties_needed = parties_needed
        self.max_players = party_size * parties_needed
        self.queue: List[Dict] = []
        self.history: List[Dict] = []
        
    def add_player(self, name: str, source: str = "manual") -> Dict:
        if self.is_player_in_queue(name):
            return {
                "success": False,
                "message": f"{name} is already in queue",
                "queue": self.get_queue_status()
            }
        
        player = {
            "name": name,
            "joined_at": datetime.now().isoformat(),
            "source": source
        }
        
        self.queue.append(player)
        
        is_ready = len(self.queue) >= self.max_players
        
        return {
            "success": True,
            "message": f"{name} joined queue",
            "player": player,
            "queue": self.get_queue_status(),
            "ready": is_ready,
            "parties": self.form_parties() if is_ready else None
        }
    
    def add_multiple_players(self, names: List[str], source: str = "manual") -> Dict:
        added = []
        skipped = []
        
        for name in names:
            name = name.strip()
            if not name:
                continue
                
            if self.is_player_in_queue(name):
                skipped.append(name)
            else:
                player = {
                    "name": name,
                    "joined_at": datetime.now().isoformat(),
                    "source": source
                }
                self.queue.append(player)
                added.append(name)
        
        is_ready = len(self.queue) >= self.max_players
        
        return {
            "success": True,
            "added": added,
            "skipped": skipped,
            "queue": self.get_queue_status(),
            "ready": is_ready,
            "parties": self.form_parties() if is_ready else None
        }
    
    def remove_player(self, name: str) -> Dict:
        original_length = len(self.queue)
        self.queue = [p for p in self.queue if p["name"].lower() != name.lower()]
        
        if len(self.queue) < original_length:
            return {
                "success": True,
                "message": f"{name} removed from queue",
                "queue": self.get_queue_status()
            }
        else:
            return {
                "success": False,
                "message": f"{name} not found in queue",
                "queue": self.get_queue_status()
            }
    
    def is_player_in_queue(self, name: str) -> bool:
        return any(p["name"].lower() == name.lower() for p in self.queue)
    
    def form_parties(self) -> Optional[List[List[Dict]]]:
        if len(self.queue) < self.max_players:
            return None
        
        parties = []
        players_to_group = self.queue[:self.max_players]
        
        for i in range(self.parties_needed):
            start_idx = i * self.party_size
            end_idx = start_idx + self.party_size
            party = players_to_group[start_idx:end_idx]
            parties.append(party)
        
        return parties
    
    def finalize_parties(self) -> Dict:
        if len(self.queue) < self.max_players:
            return {
                "success": False,
                "message": "Not enough players to form parties"
            }
        
        parties = self.form_parties()
        
        party_record = {
            "parties": parties,
            "formed_at": datetime.now().isoformat()
        }
        self.history.append(party_record)
        
        self.queue = self.queue[self.max_players:]
        
        return {
            "success": True,
            "parties": parties,
            "queue": self.get_queue_status(),
            "history": self.get_history()
        }
    
    def clear_queue(self) -> Dict:
        self.queue = []
        return {
            "success": True,
            "message": "Queue cleared",
            "queue": self.get_queue_status()
        }
    
    def get_queue_status(self) -> Dict:
        return {
            "players": self.queue,
            "count": len(self.queue),
            "max": self.max_players,
            "percentage": (len(self.queue) / self.max_players) * 100,
            "ready": len(self.queue) >= self.max_players
        }
    
    def get_history(self, limit: int = 5) -> List[Dict]:
        return self.history[-limit:]
    
    @staticmethod
    def parse_log_line(line: str) -> Optional[Tuple[str, str, int, List[str]]]:
        pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}\.\d{2}\.\d{2})\s+(\d+)\s+(\w+)\s+(.+?)\s+(.+)$'
        match = re.match(pattern, line)
        
        if not match:
            return None
        
        timestamp, increment, chat_type, player_name, message = match.groups()
        
        message = message.strip()
        
        if not message.startswith('+'):
            return None
        
        plus_match = re.match(r'^\+(\d*)\s*(.*)$', message)
        if not plus_match:
            return None
        
        count_str, names_str = plus_match.groups()
        count = int(count_str) if count_str else 1
        
        names = []
        if count == 1:
            names = [player_name]
        else:
            if names_str:
                names = [name.strip() for name in re.split(r'[,;]', names_str) if name.strip()]
                if len(names) != count:
                    names = names[:count]
            
            if len(names) < count:
                names.extend([f"{player_name}_guest{i+1}" for i in range(count - len(names))])
        
        return timestamp, player_name, count, names

