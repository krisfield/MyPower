import os
import sys

import csv
import datetime
from databasemanager import DatabaseManager
from terminaltables import AsciiTable
import urllib.request

def clear():
  os.system('cls' if os.name == 'nt' else 'clear')

def dbBuild():
  print("Updating database...")
  #DOWNLOADING CSV FROM POWERTOCHOOSE.ORG AND SAVING FILE
  url = 'http://www.powertochoose.org/en-us/Plan/ExportToCsv'
  urllib.request.urlretrieve(url, 'mypower.csv')

  #CONNECTING TO DB
  dbmgr = DatabaseManager("mypower.db")
  dbmgr.query("DROP TABLE IF EXISTS offers")

  #CREATING DB TABLE IF IT DOESN'T EXIST
  dbmgr.query("CREATE TABLE IF NOT EXISTS offers ('idKey' INTEGER, 'TduCompanyName', 'RepCompany', 'Product', 'kwh500' INTEGER, 'kwh1000' INTEGER, 'kwh2000' INTEGER, 'FeesCredits', 'PrePaid', 'TimeOfUse', 'Fixed', 'RateType', 'Renewable' INTEGER, 'TermValue' INTEGER, 'CancelFee', 'Website', 'SpecialTerms', 'TermsURL', 'Promotion', 'PromotionDesc', 'FactsURL', 'EnrollURL', 'PrepaidURL', 'EnrollPhone', 'NewCustomer', 'MinUsageFeesCredits');")

  #OPENING DOWNLOADED CSV TO SAVE IT INTO DB
  with open('mypower.csv','rt') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['[idKey]'], i['[TduCompanyName]'], i['[RepCompany]'], i['[Product]'], i['[kwh500]'], i['[kwh1000]'], i['[kwh2000]'], i['[Fees/Credits]'], i['[PrePaid]'], i['[TimeOfUse]'], i['[Fixed]'], i['[RateType]'], i['[Renewable]'], i['[TermValue]'], i['[CancelFee]'], i['[Website]'], i['[SpecialTerms]'], i['[TermsURL]'], i['[Promotion]'], i['[PromotionDesc]'], i['[FactsURL]'], i['[EnrollURL]'], i['[PrepaidURL]'], i['[EnrollPhone]'], i['[NewCustomer]'], i['[MinUsageFeesCredits]']) for i in dr]

    #SAVING CSV INTO DB
    dbmgr.querymany("INSERT INTO offers ('idKey', 'TduCompanyName', 'RepCompany', 'Product', 'kwh500', 'kwh1000', 'kwh2000', 'FeesCredits', 'PrePaid', 'TimeOfUse', 'Fixed', 'RateType', 'Renewable', 'TermValue', 'CancelFee', 'Website', 'SpecialTerms', 'TermsURL', 'Promotion', 'PromotionDesc', 'FactsURL', 'EnrollURL', 'PrepaidURL', 'EnrollPhone', 'NewCustomer', 'MinUsageFeesCredits') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)

    #DELETES LAST ROW
    dbmgr.query('DELETE FROM offers WHERE "idKey"="END OF FILE";')
  #COMMITING CHANGES AND CLOSING CONNECTION
  del(dbmgr)

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
      if tdu_num in TDU:
        user_pref["tdu"] = TDU[tdu_num]["tdu_name"]
        break
      print("Oops! That was not a valid TDU number. Try again...")

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
      print("Oops! That was not a valid entry. Try again...")
    else:
      if renewable != 'y':
        user_pref["renewable"] = 0
      else:
        user_pref["renewable"] = 100
    break

  while True:
    try:
      contract = int(input("Desired minimum contract length (months) [0]?: ") or "0")
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
  dbmgr = DatabaseManager("mypower.db")
  dbmgr.query('SELECT * FROM offers WHERE "kwh500" IS NOT NULL')
  result = dbmgr.fetchall()

  dbmgr.query("DROP TABLE IF EXISTS user")
  dbmgr.query('CREATE TABLE user (idKey INTEGER, avgPrice INTEGER)')
  for row in result:
    kwh2000 = row[6]
    kwh1000 = row[5]
    kwh500 = row[4]
    idkey = row[0]

    if USER["usage"] >= 1000:
      price = ((USER["usage"]-1000) * kwh2000) + (500 * kwh1000) + (500 * kwh500)

    elif USER["usage"] >= 500:
      price = ((USER["usage"]-500) * kwh1000) + (500 * kwh500)

    else:
      price = USER["usage"] * kwh500

    t = (idkey, price)
    dbmgr.query('INSERT INTO user VALUES (?, ?)', t)

  del(dbmgr)

def build_tdu():
  clear()
  dbmgr = DatabaseManager("mypower.db")
  dbmgr.query('SELECT DISTINCT "TduCompanyName" FROM offers')
  result = dbmgr.fetchall()
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

def view_offers(USER):
  """View offers."""
  clear()
  dbmgr = DatabaseManager("mypower.db")

  data = []
  offer_ids = []
  data.append(['id', 'Company', 'Price ($)', 'Term (months)', 'Renewable (%)', 'Rate Type'])

  for row in dbmgr.query('SELECT offers.idKey, offers.RepCompany, user.avgPrice, offers.TermValue, offers.Renewable, offers.RateType FROM offers INNER JOIN user ON offers.idKey = user.idKey WHERE offers.TduCompanyName=? AND offers.TermValue >=? AND offers.Renewable >=? ORDER BY user.avgPrice ASC LIMIT 10', (USER["tdu"], USER["contract term"], USER["renewable"])):
    data.append([row[0], row[1], row[2], row[3], row[4], row[5] ])
    offer_ids.append(row[0])

  table = AsciiTable(data, title="Best offers")
  print (table.table)
  print ("Above are the best deals based on your average {}Kwh usage\n\n".format(USER["usage"]))
  return offer_ids
  del(dbmgr)

def offer_details(OFFER_IDS):
  dbmgr = DatabaseManager("mypower.db")

  while True:
    try:
      selected_offer = int(input("Enter the offer id to view more details: ").lower())
    except ValueError:
      print("Oops! That was not a valid number. Try again...")
    else:
      if selected_offer in OFFER_IDS:
        t = (selected_offer, )
        dbmgr.query('SELECT offers.Product, offers.idKey, offers.RepCompany, user.avgPrice, offers.kwh500, offers.kwh1000, offers.kwh2000, offers.FeesCredits, offers.TermValue, offers.FactsURL, offers.EnrollURL FROM offers INNER JOIN user ON offers.idKey = user.idKey WHERE offers.idKey = ?', t)
        offer = dbmgr.fetchone()
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
         """.format(offer[0], offer[1], offer[2], offer[3], offer[4], offer[5], offer[6], offer[7], offer[8], offer[9], offer[10]))

if __name__ == '__main__':
  menu()
  dbCheck()
  tdu_choices = build_tdu()
  preferences = user_input(tdu_choices)
  avgprice(preferences)
  offer_ids = view_offers(preferences)
  offer_details(offer_ids)

