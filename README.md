# Test Technique chez Weenat

Ce projet est une application Python d’ingestion et de restitution de données utilisant FastAPI, SQLAlchemy, Pandas, et Hypercorn.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- Python 3.8 ou plus récent
- Node.js et npm (pour le serveur JSON)

## Installation

### Clonage du dépôt

Clonez le dépôt GitHub sur votre machine locale :

```sh
git clone https://github.com/FanZy0127/WTT.git
cd WTT
```

Créez un .env à la racine dans lequel pour entrerez la configuration locale suivante : 

```dotenv
DATABASE_URL=sqlite+aiosqlite:///./test.db
# For PostgreSQL, uncomment the line below and comment the SQLite line
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

DATA_URL=http://localhost:3001/measurements
JSON_SERVER_PATH="C:\\PATH\\TO\\YOUR\\npm\\json-server.cmd"
```

## Création et activation de l'environnement virtuel

### Sous Git Bash :

```sh
python -m venv venv
source venv/Scripts/activate
```

### Sous Windows :

```sh
python -m venv venv
.\venv\Scripts\activate
```

### Sous Mac/Linux :

```sh
python -m venv venv
source venv/bin/activate
```

### Installation des dépendances Python

```sh
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
```

## Lancement du projet

### Lancement de l'application FastAPI avec hypercorn (incluant l'extraction et la validation des données, le démarrage 
### du serveur JSON, l'initialisation de la base de données, l'ingestion des données et la génération de la data 
### visualisations :

```sh
hypercorn app.main:app --config hypercorn_config.py
```

#### Par requête curl

```sh
curl -X POST "http://127.0.0.1:8000/ingest/"
```

OU 

#### Par API front 

Cliquez sur **Try it out** à droite de *Parameters* puis sur **Execute**.

![data_ingestion.png](imgs%2Fdata_ingestion.png)


## Utilisation des endpoints

### Récupération de la data brute

#### Par requête curl

```sh
curl -X GET "http://127.0.0.1:8000/api/data?datalogger=temp&since=2023-01-01T00:00:00&before=2023-01-02T00:00:00"
```

OU 

#### Par API front 

Cliquez sur **Try it out** à droite de *Parameters*, remplissez les paramètres désirés, puis cliquez sur **Execute**.

![raw_data_retrieval.png](imgs%2Fraw_data_retrieval.png)


### Agréagation globale, par jour ou par heure

#### Agrégation globale par requête curl

```sh
curl -X GET "http://127.0.0.1:8000/api/summary?datalogger=temp&span=max&since=2023-01-01T00:00:00&before=2023-01-02T00:00:00"
```

#### Agrégation par jour par requête curl

```sh
curl -X GET "http://127.0.0.1:8000/api/summary?datalogger=temp&span=day&since=2023-01-01T00:00:00&before=2023-01-02T00:00:00"
```

#### Agrégation par heure par requête curl

```sh
curl -X GET "http://127.0.0.1:8000/api/summary?datalogger=temp&span=hour&since=2023-01-01T00:00:00&before=2023-01-02T00:00:00"
```

OU 

#### Par API front 

Cliquez sur **Try it out** à droite de *Parameters*, remplissez les paramètres désirés, puis cliquez sur **Execute**.

![aggregated_data_retrieval.png](imgs%2Faggregated_data_retrieval.png)


## Tests

### Exécution manuelle des tests unitaires (TU)

```sh
pytest tests/nom_du_fichier_de_test
```

OU pour run tous les tests 

```sh
coverage run -m pytest
```

OU

```sh
pytest tests/
```

OU pour une couverture plus complètes et détaillée

```sh
pytest --cov=app --cov-report=term-missing:skip-covered --cov-report=xml --cov-report=html
```