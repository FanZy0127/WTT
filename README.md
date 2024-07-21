# Test Technique chez Weenat

Ce projet est une application Python d’ingestion et de restitution de données utilisant FastAPI, SQLAlchemy, Pandas, et Hypercorn.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- Python 3.9 ou plus récent
- Node.js et npm (pour le serveur JSON)

## Installation

### Clonage du dépôt

Clonez le dépôt GitHub sur votre machine locale :

```sh
git clone https://github.com/FanZy0127/WTT.git
cd WTT
```

## Création et activation de l'environnement virtuel

### Sous Windows :

```sh
python -m venv venv
source venv/bin/activate
```

### Installation des dépendances Python

```sh
pip install -r requirements.txt
```

### Installation du serveur JSON

```sh
npm install -g json-server
```

## Lancement du projet

### Lancement du serveur JSON

```sh
json-server --watch data/extracted/datalogger/db.json
```

###  Initialisation de la bdd (base de données)

#### Depuis la racine du projet

```sh
python app.init_db.py
```

OU

#### Depuis /app

```sh
python init_db.py
```

### Lancement du serveur FastAPI avec hypercorn

```sh
hypercorn app.main:app --reload
```

### Ingestion des données

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

### Exécution des tests unitaires (TU)

```sh
pytest tests/nom_du_fichier_de_test
```

OU pour run tous les tests 

```sh
coverage run -m pytest
```