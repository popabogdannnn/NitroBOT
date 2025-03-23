import csv
import pandas as pd
import gspread

DISCORD_USER = 'Username Discord'
TEAM_NAME = 'Daca da, care este numele echipei'

gc = gspread.oauth()

SPREADSHEET_ID = "16bMBw_XNP-tUQP5H1Zdd2C_oOjJTxnI7eNnXWvU0GqY"
SHEET_ID = "1439690484"
sheet = gc.open_by_key(SPREADSHEET_ID).get_worksheet_by_id(SHEET_ID)

def load():
    db = pd.DataFrame(sheet.get_all_records())
    db[DISCORD_USER] = db[DISCORD_USER].astype(str)
    db[TEAM_NAME] = db[TEAM_NAME].astype(str)
    return db


    