import json
import os
import hashlib
from dte.distribution_model import VaultDistribution

dist = VaultDistribution("data/real_vaults.json")

SEED_MAP_FILE = "data/seed_map.json"



def load_seed_map():
    """Load the seed map from file each time to get fresh data."""
    if os.path.exists(SEED_MAP_FILE):
        with open(SEED_MAP_FILE) as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {}

def decode_seed(seed):
    # Load fresh seed map
    real_seeds = load_seed_map()
    
    # Real seed path
    if seed in real_seeds:
        return real_seeds[seed]

    # Honey path
    return {
        "email": dist.sample_email(),
        "password": dist.sample_password(),
        "notes": dist.sample_note()
    }
