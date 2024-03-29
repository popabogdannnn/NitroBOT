import csv
import pandas as pd

DISCORD_USER = 'Username Discord'
TEAM_NAME = 'Dacă da, care este numele echipei?'

def load(path):
    db = pd.read_csv(path)
    db[DISCORD_USER] = db[DISCORD_USER].astype(str)
    db[TEAM_NAME] = db[TEAM_NAME].astype(str)
    return db

def merge(db1, db2):
    return pd.concat([db1, db2], ignore_index=True).drop_duplicates()

def save(db, path):
    db.to_csv(path, index=False)
    