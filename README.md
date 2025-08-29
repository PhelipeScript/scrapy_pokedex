# Pokédex Scraper

Um web scraper desenvolvido em Python usando Scrapy para extrair informações completas de Pokémons do site [PokemonDB](https://pokemondb.net/pokedex/all) e armazená-las em MongoDB.

## 📋 Funcionalidades

Este scraper coleta as seguintes informações de cada Pokémon:

### Dados Básicos
- ✅ **Número do Pokédex**
- ✅ **Nome e apelido** (se houver)
- ✅ **URL da página**
- ✅ **Tipos** (Água, Fogo, Grama, etc.)
- ✅ **Altura** (em centímetros)
- ✅ **Peso** (em quilogramas)

### Evoluções
- ✅ **Próximas evoluções** (se houver)
  - Número do Pokédex
  - Nome e apelido
  - Requisito de evolução (nível, item, etc.)
  - URL da página

### Efetividade de Tipos
- ✅ **Tabela de efetividade** contra todos os tipos
- ✅ **Diferentes habilidades** (quando aplicável)

### Habilidades
- ✅ **Nome da habilidade**
- ✅ **Descrição completa**
- ✅ **Habilidades ocultas**
- ✅ **URL da página da habilidade**

## 🛠️ Tecnologias Utilizadas

- **Python 3.12**
- **Scrapy** - Framework para web scraping
- **MongoDB** - Banco de dados NoSQL
- **PyMongo** - Driver MongoDB para Python

## 📦 Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd pokemon-scraper
```

2. **Instale as dependências usando Pipenv:**
```bash
pipenv install
```

3. **Ative o ambiente virtual:**
```bash
pipenv shell
```

4. **Configure a conexão MongoDB:**
   - Edite o arquivo `mongodb.py` com suas credenciais do MongoDB
   - Ou configure as variáveis de ambiente necessárias

## 🚀 Como Usar

### Execução Básica

```bash
python main.py
```

### Fluxo de Execução

1. **Scraping**: O spider navega pelo Pokédex coletando dados de todos os Pokémons
2. **Processamento**: Os dados são processados e salvos em `pokemons.json`
3. **Armazenamento**: Os dados são inseridos no MongoDB
4. **Análises**: Executa consultas de exemplo nos dados coletados

### Saída do Console

O programa exibe informações coloridas durante a execução:
- 🔍 **Cyan**: Buscando dados básicos do Pokémon
- 🔍 **Blue**: Coletando efetividade de tipos
- 🔍 **Magenta**: Extraindo habilidades
- 🔍 **Green**: Processando evoluções

## 📊 Estrutura dos Dados

### Formato JSON de Saída

```json
{
  "pokemon_id": {
    "number": "001",
    "name": "Bulbasaur",
    "nickname": null,
    "url": "https://pokemondb.net/pokedex/bulbasaur",
    "types": ["Grass", "Poison"],
    "height_cm": 70,
    "weight_kg": 6.9,
    "evolutions": [
      {
        "unique_id": "002_ivysaur",
        "numero": "002",
        "name": "Ivysaur",
        "nickname": null,
        "requirement": "Level 16",
        "url": "https://pokemondb.net/pokedex/ivysaur"
      }
    ],
    "effectiveness": {
      "default_ability": {
        "Fire": 2,
        "Water": 0.5,
        "Electric": 0.5,
        "Grass": 0.25
      }
    },
    "abilities": {
      "overgrow": {
        "name": "Overgrow",
        "description": "Powers up Grass-type moves when the Pokémon's HP is low.",
        "is_hidden_ability": false,
        "url": "https://pokemondb.net/ability/overgrow"
      }
    }
  }
}
```

### Estrutura no MongoDB

Os dados são armazenados no MongoDB com a seguinte estrutura:
- **Database**: `pokedex`
- **Collection**: `pokemons`
- **_id**: ID único do Pokémon
- **Campos**: Todos os dados coletados do scraping

## 🔍 Consultas de Exemplo

O código inclui algumas consultas de análise:

### 1. Pokémons com Múltiplos Tipos
```python
# Conta Pokémons com 2 ou mais tipos
count = db.count_pokemons_by_min_types(2)
```

### 2. Evoluções por Tipo e Nível
```python
# Busca Pokémons do tipo Água que evoluem após nível 30
water_pokemons = db.fetch_evolutions_of_type_after_level("Water", 30)
```

## 📁 Estrutura do Projeto

```
pokemon-scraper/
├── main.py              # Spider principal e lógica de scraping
├── mongodb.py           # Classe para interação com MongoDB
├── colors.py            # Constantes para cores no terminal
├── Pipfile             # Dependências do projeto
├── Pipfile.lock        # Versões específicas das dependências
├── .gitignore          # Arquivos ignorados pelo Git
├── README.md           # Este arquivo
└── pokemons.json       # Arquivo de saída (gerado após execução)
```

## ⚙️ Configurações Personalizadas

### Configurações do Scrapy

O spider possui configurações customizadas:
- **Formato de saída**: JSON com encoding UTF-8
- **Log level**: ERROR (para reduzir verbosidade)
- **Indentação**: 2 espaços para melhor legibilidade

### Tratamento de Casos Especiais

- **Pokémons com formas alternativas** (ex: Alolan, Galarian)
- **Evoluções com requisitos especiais** (pedras, trocas, itens)
- **Pokémons com múltiplas habilidades**
- **Eevee e suas múltiplas evoluções**

## 🐛 Tratamento de Erros

- **Dados ausentes**: Valores nulos para campos não encontrados
- **URLs inválidas**: Verificação de links antes do processamento
- **Conexão de rede**: Retry automático do Scrapy
- **Dados malformados**: Limpeza e validação de strings

## 📈 Performance

- **Rate limiting**: Configurado para ser respeitoso com o servidor
- **Caching**: Evita requisições duplicadas
- **Processamento assíncrono**: Utiliza a natureza assíncrona do Scrapy

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## ⚠️ Disclaimer

Este projeto é apenas para fins educacionais e de pesquisa. Sempre respeite os termos de uso dos sites que você está fazendo scraping e use práticas éticas de web scraping.

## 📞 Suporte

Se você encontrar algum problema ou tiver sugestões, por favor abra uma [issue](../../issues) no repositório.
