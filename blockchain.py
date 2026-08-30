"""
Blockchain Verification Module
Reputation system with proof-of-work
"""

import hashlib
import json
import time
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Dict]
    proof: int
    previous_hash: str
    hash: str = None
    
    def calculate_hash(self) -> str:
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'proof': self.proof,
            'previous_hash': self.previous_hash
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

@dataclass
class NodeTransaction:
    sender: str
    receiver: str
    amount: float
    action: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class MeshBlockchain:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.chain: List[Block] = []
        self.pending_transactions: List[NodeTransaction] = []
        self.reputation_scores = defaultdict(float)
        self.difficulty = 4
        self._create_genesis_block()
        
    def _create_genesis_block(self):
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            proof=100,
            previous_hash="0"
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
    
    def add_transaction(self, sender: str, receiver: str, amount: float, action: str) -> bool:
        transaction = NodeTransaction(sender, receiver, amount, action)
        self.pending_transactions.append(transaction)
        
        if action == 'share':
            self.reputation_scores[sender] += amount * 0.1
        elif action == 'connect':
            self.reputation_scores[receiver] += amount * 0.05
        
        return True
    
    def mine_block(self, miner_address: str) -> Optional[Block]:
        if not self.pending_transactions:
            return None
        
        last_block = self.chain[-1]
        proof = self._proof_of_work(last_block.proof)
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            proof=proof,
            previous_hash=last_block.hash
        )
        new_block.hash = new_block.calculate_hash()
        
        self.chain.append(new_block)
        self.pending_transactions.clear()
        self.reputation_scores[miner_address] += 1.0
        
        return new_block
    
    def _proof_of_work(self, last_proof: int) -> int:
        proof = 0
        while True:
            guess = f"{last_proof}{proof}".encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            if guess_hash[:self.difficulty] == "0" * self.difficulty:
                return proof
            proof += 1
    
    def get_reputation(self, node_id: str) -> float:
        return self.reputation_scores.get(node_id, 0.5)
    
    def is_trusted(self, node_id: str, threshold: float = 0.6) -> bool:
        return self.get_reputation(node_id) >= threshold
    
    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
            
            guess = f"{previous.proof}{current.proof}".encode()
            guess_hash = hashlib.sha256(guess).hexdigest()
            if guess_hash[:self.difficulty] != "0" * self.difficulty:
                return False
        
        return True

class ReputationManager:
    def __init__(self, node_id: str):
        self.blockchain = MeshBlockchain(node_id)
        self.banned_nodes = set()
        
    def record_share(self, sharer: str, receiver: str, bandwidth: float):
        self.blockchain.add_transaction(sharer, receiver, bandwidth, 'share')
        
        if len(self.blockchain.pending_transactions) >= 5:
            self.blockchain.mine_block(self.blockchain.node_id)
    
    def record_connection(self, client: str, gateway: str):
        self.blockchain.add_transaction(client, gateway, 0.1, 'connect')
    
    def get_trust_score(self, node_id: str) -> float:
        score = self.blockchain.get_reputation(node_id)
        
        if node_id in self.banned_nodes:
            score *= 0.1
        
        return score
    
    def ban_node(self, node_id: str, reason: str):
        self.banned_nodes.add(node_id)
        print(f"🚫 Node {node_id[:8]} banned: {reason}")
        
        self.blockchain.add_transaction(
            self.blockchain.node_id,
            node_id,
            0.0,
            'ban'
        )
    
    def get_network_stats(self) -> Dict:
        return {
            'chain_length': len(self.blockchain.chain),
            'pending_transactions': len(self.blockchain.pending_transactions),
            'total_nodes': len(self.blockchain.reputation_scores),
            'banned_nodes': len(self.banned_nodes),
            'average_reputation': np.mean(list(self.blockchain.reputation_scores.values())) 
                if self.blockchain.reputation_scores else 0.5
        }
