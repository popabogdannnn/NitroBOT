import csv
import pandas as pd

def load(path):
    return pd.read_csv(path)

def merge(db1, db2):
    return pd.concat([db1, db2], ignore_index=True).drop_duplicates()

def save(db, path):
    db.to_csv(path, index=False)
    