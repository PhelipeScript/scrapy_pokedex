import json
import re
from pymongo import MongoClient

class MongoDB:
  client = MongoClient("mongodb+srv://phelipe:pereira@pokedex.mqthwr6.mongodb.net/?retryWrites=true&w=majority&appName=Pokedex")
  db = client["pokedex"]
  collection = db["pokemons"]

  def __remove_pokemon_nickname(self, pokemon):
    if pokemon['nickname'] is not None:
      pokemon['name'] = pokemon['nickname']
        
    del pokemon['nickname']

  def insert_pokemons(self):
    self.collection.delete_many({})

    with open("pokemons.json", "r", encoding="utf-8") as f:
      data = json.load(f)

    for entry in data:
      for unique_id, pokemon in entry.items():
        pokemon["_id"] = unique_id
        del pokemon["unique_id"]
        
        self.__remove_pokemon_nickname(pokemon)
        if pokemon['evolutions'] is not None:
          for evo in pokemon['evolutions']:
            self.__remove_pokemon_nickname(evo)
        else:
          pokemon['evolutions'] = f"{pokemon['name']} does not evolve."
        
        print(f"✅ Inserindo Pokémon: {pokemon['number']} - {pokemon['name']}")
        self.collection.update_one({"_id": unique_id}, {"$set": pokemon}, upsert=True)
    print("✅ Todos os Pokémons foram inseridos no MongoDB!")
  
  def fetch_all_pokemons(self):
    return list(self.collection.find({}))

  def fetch_pokemon_by_id(self, pokemon_id: str):
    return self.collection.find_one({"_id": pokemon_id})

  def fetch_pokemon_by_name(self, name: str):
    return self.collection.find_one({"name": name})

  def count_pokemons_by_min_types(self, min_types = 2):
    return self.collection.count_documents({
      "$expr": {"$gte": [{"$size": "$types"}, min_types]}
    })

  def fetch_evolutions_of_type_after_level(self, type="Water", level=30):
    res = self.collection.find({
        "types": type,
        "evolutions": {
            "$elemMatch": {
                "requirement": {"$regex": r"\(Level (\d+)\)", "$options": "i"}
            }
        }
    })
    
    pokemons = []
    level_pattern = re.compile(r"\(Level (\d+)\)", re.IGNORECASE)
    
    for p in res:
      if isinstance(p.get("evolutions"), list):
        for evo in p['evolutions']:
          requirement = evo['requirement'] if isinstance(evo['requirement'], str) else evo['requirement'][0]
          match = level_pattern.search(requirement)
          if match:
            evo_level = int(match.group(1))
            if evo_level >= level and evo['name'] not in pokemons:
              pokemons.append(evo['name'])

    return pokemons
