import os
import sys

import csv
import datetime
import sqlite3
from terminaltables import AsciiTable
import urllib.request

con = sqlite3.connect('mypower.db')
con.text_factory = str
cur = con.cursor()

def clear():
  os.system('cls' if os.name == 'nt' else 'clear')

def dbBuild():
  print("Updating database...")
  #DOWNLOADING CSV FROM POWERTOCHOOSE.ORG AND SAVING FILE
  url = 'http://www.powertochoose.org/en-us/Plan/ExportToCsv'
  urllib.request.urlretrieve(url, 'mypower.csv')

  #CONNECTING TO DB
  con = sqlite3.connect('mypower.db')
  #con.text_factory = str
  cur = con.cursor()
  #DROPING TABLE OR ELSE IT JUST GROWS
  cur.execute("DROP TABLE IF EXISTS offers")

  #CREATING DB TABLE IF IT DOESN'T EXIST
  cur.execute("CREATE TABLE IF NOT EXISTS offers ('idKey' INTEGER, 'TduCompanyName', 'RepCompany', 'Product', 'kwh500' INTEGER, 'kwh1000' INTEGER, 'kwh2000' INTEGER, 'Fees/Credits', 'PrePaid', 'TimeOfUse', 'Fixed', 'RateType', 'Renewable' INTEGER, 'TermValue' INTEGER, 'CancelFee', 'Website', 'SpecialTerms', 'TermsURL', 'Promotion', 'PromotionDesc', 'FactsURL', 'EnrollURL', 'PrepaidURL', 'EnrollPhone', 'NewCustomer', 'MinUsageFeesCredits', 'avgPrice');")

  #OPENING DOWNLOADED CSV TO SAVE IT INTO DB
  with open('mypower.csv','rt') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['[idKey]'], i['[TduCompanyName]'], i['[RepCompany]'], i['[Product]'], i['[kwh500]'], i['[kwh1000]'], i['[kwh2000]'], i['[Fees/Credits]'], i['[PrePaid]'], i['[TimeOfUse]'], i['[Fixed]'], i['[RateType]'], i['[Renewable]'], i['[TermValue]'], i['[CancelFee]'], i['[Website]'], i['[SpecialTerms]'], i['[TermsURL]'], i['[Promotion]'], i['[PromotionDesc]'], i['[FactsURL]'], i['[EnrollURL]'], i['[PrepaidURL]'], i['[EnrollPhone]'], i['[NewCustomer]'], i['[MinUsageFeesCredits]']) for i in dr]

    #SAVING CSV INTO DB
    cur.executemany("INSERT INTO offers ('idKey', 'TduCompanyName', 'RepCompany', 'Product', 'kwh500', 'kwh1000', 'kwh2000', 'Fees/Credits', 'PrePaid', 'TimeOfUse', 'Fixed', 'RateType', 'Renewable', 'TermValue', 'CancelFee', 'Website', 'SpecialTerms', 'TermsURL', 'Promotion', 'PromotionDesc', 'FactsURL', 'EnrollURL', 'PrepaidURL', 'EnrollPhone', 'NewCustomer', 'MinUsageFeesCredits') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)

    #DELETES LAST ROW
    cur.execute('DELETE FROM offers WHERE "idKey"="END OF FILE";')
  #COMMITING CHANGES AND CLOSING CONNECTION
  con.commit()
  con.close()

def dbCheck():
  """Shows last time data was downloaded from Power To Choose and gives option to update"""
  if os.path.isfile('mypower.csv'):
    csv_last_download = datetime.datetime.fromtimestamp(os.stat('mypower.csv').st_mtime)
    print ("This database was last updated from Power to Choose at {}\n\n".format(csv_last_download))
    if input("Would you like to update this database? [y/N]: ").lower() == 'y':
      dbBuild()
  else:
    dbBuild()

def user_input(TDU):
  """Enter your preferences to find the best deal for your situation"""
  user_pref = {}
  while True:
    try:
      tdu_num = int(input("Enter number of your TDU: ")) - 1
      ##need to have a check that this value is in range
    except ValueError:
      print("Oops! That was not a valid number. Try again...")
    else:
      user_pref["tdu"] = TDU[tdu_num]["tdu_name"]
      break

  while True:
    try:
      usage = int(input("Enter you average energy consumption in Kwh: "))
    except ValueError:
      print("Oops! That was not a valid number. Try again...")
    else:
      user_pref["usage"] = usage
      break

  while True:
    try:
      renewable = input("Do you want fully Renewable energy? [y/N]: ").lower()
    except ValueError:
      print("Oops! That was not a valid number. Try again...")
    else:
      if renewable != 'y':
        user_pref["renewable"] = 0
      else:
        user_pref["renewable"] = 100
    break

  while True:
    try:
      contract = int(input("Desired minimum contract lenght (months) [0]?: ") or "0")
    except ValueError:
      print("Oops! That was not a valid number. Try again...")
    else:
      user_pref["contract term"] = contract
      break

  return user_pref


def menu():
  clear()
  print("""
Welcome to MyPowerToChoose a script which makes finding the best deal on power easier than every. This program will weed out the misleading utility ads commonly seen on powertochoose.org.
""")

def avgprice(USER):
  con = sqlite3.connect('mypower.db')
  con.text_factory = str
  cur = con.cursor()
  cur.execute('SELECT * FROM offers WHERE "kwh500" IS NOT NULL')
  result = cur.fetchall()

  for row in result:
    kwh2000 = float(row[6])
    kwh1000 = float(row[5])
    kwh500 = float(row[4])
    idkey = row[0]

    if USER["usage"] >= 1000:
      price = ((USER["usage"]-1000) * kwh2000) + (500 * kwh1000) + (500 * kwh500)

    elif USER["usage"] >= 500:
      price = ((USER["usage"]-500) * kwh1000) + (500 * kwh500)

    else:
      price = USER["usage"] * kwh500

    cur.execute('UPDATE offers SET "avgPrice"=? WHERE "idKey"=?', (price, idkey))
    con.commit()
  con.close()

def build_tdu():
  clear()
  con = sqlite3.connect('mypower.db')
  cur = con.cursor()
  cur.execute('SELECT DISTINCT "TduCompanyName" FROM offers')
  result = cur.fetchall()
  i = 0
  tdu = {}
  print("Choose your TDU provider:")
  print("_"*25)
  for row in result:
    tdu[i] = {'tdu_name': row[0]}
    print('{}) {}'.format(i+1, row[0]))
    i += 1
  print("\n\n")
  return tdu
  con.close()

def view_offers(USER):
  """View offers."""
  clear()
  con = sqlite3.connect('mypower.db')
  cur = con.cursor()

  data = []
  offer_ids = []
  data.append(['id', 'Company', 'Price ($)', 'Term (months)', 'Renewable (%)', 'Rate Type'])

  for row in cur.execute('SELECT * FROM offers WHERE TduCompanyName=? AND TermValue >=? AND Renewable >=? ORDER BY avgPrice ASC LIMIT 10', (USER["tdu"], USER["contract term"], USER["renewable"])):
    data.append([row[0], row[2], row[26], row[13], row[12], row[11] ])
    offer_ids.append(row[0])

  table = AsciiTable(data, title="Best offers")
  print (table.table)
  print ("Above are the best deals based on your average {}Kwh usage\n\n".format(USER["usage"]))
  return offer_ids
  con.close()

def offer_details(OFFER_IDS):
  con = sqlite3.connect('mypower.db')
  cur = con.cursor()

  while True:
    try:
      selected_offer = int(input("Enter the offer id to view more details: ").lower())
    except ValueError:
      print("Oops! That was not a valid number. Try again...")
    else:
      if selected_offer in OFFER_IDS:
        t = (selected_offer, )
        cur.execute('SELECT * FROM offers WHERE idKey = ?', t)
        offer = cur.fetchone()
        break
      else:
        print("Offer ID {} is not a valid selection".format(selected_offer))

  clear()
  print ("""
  OFFER DETAILS
  _________________________
  Plan name: {}  (ID #: {})
  Company: {}
  Average monthly price*: ${} (500Kwh: ${}   1000Kwh: ${}   2000Kwh: ${})
  Fees/Credits: {}
  Contract length: {} months
  Details: {}
  Enroll: {}
  (Cmd + double-click to open urls)
         """.format(offer[3], offer[0], offer[2], offer[26], offer[4], offer[5], offer[6], offer[7], offer[13], offer[20], offer[21]))

if __name__ == '__main__':
  menu()
  dbCheck()
  tdu_choices = build_tdu()
  preferences = user_input(tdu_choices)
  avgprice(preferences)
  offer_ids = view_offers(preferences)
  offer_details(offer_ids)

