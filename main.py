import scrapy
from collections import defaultdict
from scrapy.crawler import CrawlerProcess

class PokeSpider(scrapy.Spider):
  name = 'pokespider'
  base_url = 'https://pokemondb.net'
  start_urls = [f'{base_url}/pokedex/all']
  
  custom_settings = {
      "FEEDS": {
          "pokemons.json": {
            "format": "json",
            "encoding": "utf8",
            "indent": 2,
          },
      },
      "LOG_LEVEL": "ERROR",
  }

  def parse(self, response):
    rows = response.css('table#pokedex > tbody > tr')
    for row in rows:
      number = row.css("td:first-child > span::text").get()
      name = row.css("td:nth-child(2) > a::text").get()
      nickname = row.css("td:nth-child(2) > small::text").get()
      url = row.css("td:nth-child(2) > a::attr(href)").get()
      types = row.css("td:nth-child(3) > a::text").getall()
      
      yield response.follow(
        url, 
        self.parser_pokemon, 
        meta={
          "unique_id": f"{number}-{nickname.strip('()') if nickname else name}".lower().replace(' ', '_'),
          "number": number, 
          "name": name, 
          "nickname": nickname if nickname else None,
          "url": self.base_url + url,
          "types": types
        },
        dont_filter=True 
      )
    
  def parser_pokemon(self, response):
    unique_id = response.meta['unique_id']
    number = response.meta['number']
    name = response.meta['name']
    nickname = response.meta['nickname']
    url = response.meta['url']
    types = response.meta['types']
    
    pokemon_tab_index = self.parse_pokemon_tab_index(response, nickname if nickname else name)
    pokemon_panel = self.parse_get_pokemon_panel(response, pokemon_tab_index)
    
    height_str = pokemon_panel.css('table.vitals-table > tbody > tr:nth-child(4) > td::text').get()
    if height_str:
      height_str = height_str.split()[0]  
      height_m = float(height_str)        
      height_cm = int(height_m * 100)     
    else:
      height_cm = None
    
    weight_str = pokemon_panel.css('table.vitals-table > tbody > tr:nth-child(5) > td::text').get()
    weight_kg = float(weight_str.split()[0]) if weight_str and weight_str != '—' else None

    yield {
      "id": unique_id,
      "number": number,
      "name": name,
      "nickname": nickname,
      "types": types,
      "height_cm": height_cm,
      "weight_kg": weight_kg,
      "url": url,
      "effectiveness": self.parse_type_effectiveness(pokemon_panel),
      "evolutions": self.parse_evolutions(response, name, nickname is not None),
    }
  
  def parse_pokemon_tab_index(self, response, name_nickname):
    pokemon_tabs = response.css('#main > div.tabset-basics.sv-tabs-wrapper > div.sv-tabs-tab-list > a::text').getall()
    index = pokemon_tabs.index(name_nickname)+1 if name_nickname in pokemon_tabs else 1
    return index
    
  def parse_get_pokemon_panel(self, response, pokemon_tab_index):
    pseudo_class = ':first-child' if pokemon_tab_index == 1 else f':nth-child({pokemon_tab_index})'
    pokemon_panel = response.css(f'#main > div.tabset-basics.sv-tabs-wrapper > div.sv-tabs-panel-list > div.sv-tabs-panel{pseudo_class}')
    return pokemon_panel
  
  def parse_get_effectiveness_from_tables(self, tables, effectiveness, ability_name='default_ability'):
    fraction_to_decimal = {"¼": 0.25, "½": 0.5, "¾": 0.75 }
    
    for table in tables:
      types_name = table.css('tr:first-child > th > a::attr(title)').getall()
      tds = table.css('tr:nth-child(2) > td')
      raw_types_effectiveness = [td.css('::text').get(default="").strip() for td in tds]
      types_effectiveness = []
      for eff in raw_types_effectiveness:
        if eff in fraction_to_decimal:
          types_effectiveness.append(fraction_to_decimal[eff])
        elif eff.isdigit():
          types_effectiveness.append(int(eff))
        elif eff == '':
          types_effectiveness.append(None)
        else: 
          types_effectiveness.append(eff)

      effectiveness[ability_name].update(
        {name: effectiveness for name, effectiveness in zip(types_name, types_effectiveness)}
      )
  
  def parse_type_effectiveness(self, panel_pokemon):
    effectiveness = defaultdict(dict)
    abilities_tabs = panel_pokemon.css('div:nth-child(2) > div.grid-col.span-md-12.span-lg-4 > div > div.sv-tabs-tab-list.sv-tabs-grow > a::text').getall()
    if abilities_tabs and len(abilities_tabs) > 1:
      effectiveness_panel = panel_pokemon.css('div:nth-child(2) > div.grid-col.span-md-12.span-lg-4 > div > div.sv-tabs-panel-list > div.sv-tabs-panel')
      
      for i, div in enumerate(effectiveness_panel):
        tables = div.css('table')
        self.parse_get_effectiveness_from_tables(tables, effectiveness, abilities_tabs[i].lower().replace(' ', '_'))
    else: 
      tables = panel_pokemon.css('div:nth-child(2) > div.grid-col.span-md-12.span-lg-4 > div > table')
      self.parse_get_effectiveness_from_tables(tables, effectiveness)
    return effectiveness

  def parse_evolutions(self, response, name, has_nickname):
    # Ignora os pokemons que são evoluções do Eevee (Se for o próprio Eevee, esta permitido)
    Eevee_evolution = ['vaporeon', 'jolteon', 'flareon', 'espeon', 'umbreon', 'leafeon', 'glaceon', 'sylveon']
    if name.lower() in Eevee_evolution:
      return []
    
    info_cards = response.css('div.infocard')
    evolutions = []
    start_collecting = False
    
    levels_and_items = []
    for small in response.css('span.infocard > small'):
      item = small.css('a::text').get()
      if item:
        levels_and_items.append((item, 'Item'))
      else:
        text = small.css('::text').get()
        if text and 'Level' in text:
          levels_and_items.append((text, 'Level'))

    for i, info_card in enumerate(info_cards):
        evolution_name = info_card.css('span:nth-child(2) > a::text').get()

        evolution_nickname_list = info_card.css('span:nth-child(2) > small::text').getall()
        evolution_nickname = evolution_nickname_list[1].strip() if len(evolution_nickname_list) > 1 else None
        if evolution_nickname in ["", "·"]:
            evolution_nickname = None

        # Só começo a coletar quando encontrar o pokemon base (atual) pq eu quero apenas suas evoluções e não as anteriores
        if not start_collecting:
          if evolution_name == name and ((has_nickname == (evolution_nickname is not None))):
            start_collecting = True
            i > 0 and len(levels_and_items) > 0 and levels_and_items.pop(0)
          continue

        if evolution_name == name and evolution_nickname is None:
          continue

        evolution_number = info_card.css('span:nth-child(2) > small:first-child::text').get().strip('#')
        evolution_url = info_card.css('span:nth-child(2) > a::attr(href)').get()

        if has_nickname == (evolution_nickname is not None):
            evolutions.append({
                "id": f"{evolution_number}-{evolution_nickname.strip('()') if evolution_nickname else evolution_name}".lower().replace(' ', '_'),
                "number": evolution_number,
                "name": evolution_name,
                "nickname": evolution_nickname,
                "url": self.base_url + evolution_url,
                "level": levels_and_items[0][0] if len(levels_and_items) > 0 and levels_and_items[0][1] == 'Level' else None,
                "item": levels_and_items[0][0] if len(levels_and_items) > 0 and levels_and_items[0][1] == 'Item' else None
            })
            len(levels_and_items) > 0 and levels_and_items.pop(0)

    return evolutions




if __name__ == "__main__":
  process = CrawlerProcess(settings=PokeSpider.custom_settings)
  process.crawl(PokeSpider)
  process.start()
