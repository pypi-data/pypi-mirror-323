import numpy as np
from typing import List, Dict

class AuctionManager:
    def __init__(self):
        """Initialize auction manager"""
        self.temperature = 1.0  # For probability adjustment
        
    def calculate_allocation_probability(self, similarities: List[float], bids: List[float]) -> List[float]:
        """Calculate allocation probabilities based on similarities and bids"""
        try:
            # If all bids are 0, use only similarities
            if all(bid == 0 for bid in bids):
                # Normalize similarities to probabilities
                total = sum(similarities)
                if total == 0:
                    return [1/len(similarities)] * len(similarities)  # Equal probability if all similarities are 0
                return [sim/total for sim in similarities]
            
            # Convert to numpy arrays for efficient computation
            sims = np.array(similarities)
            b = np.array(bids)
            
            # Calculate adjusted probabilities (equation 3.2 in paper)
            numerator = b * np.exp(sims / self.temperature)
            denominator = sum(b * np.exp(sims / self.temperature))
            
            # Avoid division by zero
            if denominator == 0:
                return [1/len(similarities)] * len(similarities)
                
            probabilities = numerator / denominator
            return probabilities.tolist()
            
        except Exception as e:
            # print(f"Error calculating allocation probabilities: {e}")
            return [1/len(similarities)] * len(similarities)  # Default to equal probabilities
    
    def select_ad(self, companies: List[Dict]) -> List[Dict]:
        """Select ad based on auction mechanism"""
        try:
            if not companies:
                return []
                
            similarities = [c.get('similarity', 0) for c in companies]
            bids = [c.get('bid', 0) for c in companies]
            
            # Calculate allocation probabilities
            probs = self.calculate_allocation_probability(similarities, bids)
            
            # Select highest probability when all bids are 0
            if all(bid == 0 for bid in bids):
                selected_idx = similarities.index(max(similarities))
                return [companies[selected_idx]]
            
            # Otherwise use probabilistic selection
            selected_idx = np.random.choice(len(companies), p=probs)
            return [companies[selected_idx]]
            
        except Exception as e:
            # print(f"Error in ad selection: {e}")
            if companies:  # Fallback to highest similarity
                return [max(companies, key=lambda x: x.get('similarity', 0))]
            return [] 