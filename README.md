# World Cup Goal Alert

Sistema de monitoramento de partidas de futebol ao vivo que analisa estatísticas em tempo real e envia alertas no Discord quando indicadores apontam alta probabilidade de gol.

## Como funciona

O sistema roda em background e executa três loops em paralelo:

1. **Coleta de dados** — a cada 5 minutos busca todas as partidas ao vivo na API-Sports, salva times, partidas e estatísticas no banco de dados e avalia as regras de alerta.
2. **Motor de regras** — pontua cada partida com base em indicadores estatísticos. Se o score atingir o limiar configurado (≥ 2.0), um alerta é disparado no Discord (com cooldown de 10 minutos por partida).
3. **Validador de alertas** — a cada 30 minutos verifica os alertas pendentes. Após o fim da partida, consulta os eventos e marca cada alerta como **Green** (saiu gol após o alerta) ou **Red** (partida terminou sem gol).

## Regras de alerta

| Regra | Condição | Pontuação |
|---|---|---|
| Pressão no Fim do Jogo | Minuto ≥ 70, Chutes a gol ≥ 8, Escanteios ≥ 7 | 1.5 |
| xG Alto | Expected Goals ≥ 1.5 | 1.0 |
| Alto Momentum | Ataques Perigosos ≥ 75 | 1.0 |
| Pressão no Fim do 1º Tempo | Minuto entre 35–45, Chutes ≥ 5, Escanteios ≥ 4 | 1.5 |

> Alertas só são disparados a partir do **minuto 15** e quando o score total ≥ **2.0 pontos**.

## Stack

- **Python 3.11+**
- **FastAPI** — API REST e gerenciamento do ciclo de vida da aplicação
- **SQLAlchemy 2.0** + **PostgreSQL** — persistência de partidas, estatísticas e alertas
- **Alembic** — migrações de banco de dados
- **API-Sports** — fonte de dados de partidas ao vivo
- **Discord Webhooks** — canal de notificação
- **httpx** — cliente HTTP assíncrono
- **loguru** — logging

## Pré-requisitos

- Python 3.11+
- PostgreSQL rodando localmente ou via Docker
- Conta na [API-Sports](https://www.api-football.com/) (plano gratuito suportado)
- Webhook configurado em um canal do Discord

## Instalação

```bash
# Clone o repositório
git clone https://github.com/Rafael-Casemiro/world-cup-goal-alert.git
cd world-cup-goal-alert

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/macOS

# Instale as dependências
pip install -r requirements.txt
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/goal_alert
API_SPORTS_KEY=sua_chave_aqui
API_SPORTS_HOST=v3.football.api-sports.io
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
LEAGUE_ID=1
```

> `LEAGUE_ID=1` corresponde à Copa do Mundo. Consulte a API-Sports para outros IDs de liga.

## Banco de dados

Execute as migrações para criar as tabelas:

```bash
alembic upgrade head
```

## Executando

```bash
uvicorn app.main:app --reload
```

A aplicação sobe na porta `8000` e inicia automaticamente os loops de coleta, avaliação e validação.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Verifica se a API está no ar |
| GET | `/matches/live` | Lista as partidas ao vivo no banco |

## Estrutura do projeto

```
app/
├── main.py               # Entrypoint FastAPI e loops de background
├── database.py           # Conexão e sessão do banco
├── models.py             # Modelos SQLAlchemy (Team, Match, Statistic, Alert)
└── services/
    ├── football_api.py   # Integração com API-Sports
    ├── collector.py      # Coleta e persistência de dados ao vivo
    ├── rules_engine.py   # Motor de regras e pontuação
    ├── discord_notifier.py # Envio de alertas via Discord
    └── validator.py      # Validação de alertas (Green/Red) pós-partida
alembic/
└── versions/             # Migrações de banco de dados
```
