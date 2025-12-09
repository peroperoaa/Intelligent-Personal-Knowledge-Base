from dotenv import load_dotenv
import os
from pinecone import Pinecone
import time

load_dotenv()

key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=key)
index_name = "notecraft"

index = pc.Index(index_name)

# Define Golden Spatula (TFT) Namespaces
namespaces = {
    "compositions": [
        "meta_comps",
        "reroll_comps",
        "fast_8_comps",
        "level_9_comps",
        "early_game_boards"
    ],
    "items": [
        "item_combinations",
        "radiant_items",
        "artifact_items",
        "support_items",
        "best_in_slot"
    ],
    "champions": [
        "1_cost_units",
        "2_cost_units",
        "3_cost_units",
        "4_cost_units",
        "5_cost_units",
        "hero_augments"
    ],
    "traits": [
        "origin_traits",
        "class_traits",
        "trait_breakpoints",
        "spatula_emblems"
    ],
    "augments": [
        "silver_augments",
        "gold_augments",
        "prismatic_augments",
        "hero_augments"
    ],
    "game_mechanics": [
        "leveling_guide",
        "economy_management",
        "rolling_odds",
        "pool_sizes",
        "damage_calculation"
    ],
    "patch_notes": [
        "buffs",
        "nerfs",
        "system_changes",
        "reworks"
    ]
}

def seed_initial_data():
    """
    This function can be used to seed the database with initial text data.
    You can create text files in a 'data' folder and ingest them here.
    """
    print("Initializing Golden Spatula Knowledge Base Structure...")
    
    print("Namespaces ready for ingestion:")
    for ns in namespaces:
        print(f"- {ns}")

if __name__ == "__main__":
    seed_initial_data()
