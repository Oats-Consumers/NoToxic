import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.build_unlabeled_dataset import collect_contexts_from_match
from utils.game_info import load_hero_data, load_chatwheel_data


hero_names, npc_names, npc_to_id = load_hero_data("data/heroes.json")