# Extraindo Pokémons do Pokédex
### Neste EP vamos fazer a extração da base de Pokémons do [Pokédex](https://pokemondb.net/pokedex/all)

<strong>O objetivo é fazer um scraper que navega no site e coleta as informações, trata e gerar o resultado em formato json usando a ferramenta Scrapy</strong>

O que devemos buscar de cada Pokémon obrigatoriamente:
- [X] Número
- [X] URL da página
- [X] Nome
- [X] Próximas evoluções do Pokémon se houver (ainda precisa arrumar meowth estranho)
    - [X] Número, level se tiver, item se tiver, nome e URL
- [X] Tipos (água, veneno, ...). Pegar todos.
- [X] Tamanho em cm
- [X] Peso em kg apenas
- [X] Salvar a efetividade de cada tipo sobre o Pokemon
- [X] Habilidades (link para outra página)
    - [X] URL da página
    - [X] Nome
    - [X] Descrição do efeito
