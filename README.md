# Rastreador de Hábitos

Aplicação de terminal em Python para registrar e analisar hábitos diários, com persistência de dados via SQLite.

> Este projeto faz parte do meu [Portfólio Pessoal](https://gabrielroma0.github.io/).

## Funcionalidades

- Cadastrar e remover hábitos
- Marcar hábitos como concluídos no dia
- Relatório semanal com visualização por dia
- Taxa de consistência geral por hábito

## Como executar

```bash
python main.py
```

Nenhuma biblioteca externa necessária — usa apenas a biblioteca padrão do Python. 

## Tecnologias

- Python 3
- SQLite (módulo `sqlite3`)
- `datetime`

## Estrutura do banco de dados

```
habitos   → id, nome
registros → id, habito_id, data
```

## Exemplo de uso

```
1. Adicione hábitos: "estudar", "exercício", "leitura"
2. Marque os que você fez hoje
3. No final da semana, veja o relatório e sua taxa de consistência
```

## Aprendizados

- Modelagem de banco de dados relacional
- Queries SQL com JOIN e GROUP BY
- Manipulação de datas com datetime
- Organização de código em funções
