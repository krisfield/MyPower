import os
import sys

import csv
import sqlite3
import urllib

def connect():
  #DOWNLOADING CSV FROM POWERTOCHOOSE.ORG AND SAVING FILE
  url = 'http://www.powertochoose.org/en-us/Plan/ExportToCsv'
  urllib.urlretrieve(url, 'mypower.csv')

  #CONNECTING TO DB
  con = sqlite3.connect('mypower.db')
  con.text_factory = str
  cur = con.cursor()

  #CREATING DB TABLE IF IT DOESN'T EXIST
  cur.execute("CREATE TABLE IF NOT EXISTS offers ('idKey', 'TduCompanyName', 'RepCompany', 'Product', 'kwh500', 'kwh1000', 'kwh2000', 'Fees/Credits', 'PrePaid', 'TimeOfUse', 'Fixed', 'RateType', 'Renewable', 'TermValue', 'CancelFee', 'Website', 'SpecialTerms', 'TermsURL', 'Promotion', 'PromotionDesc', 'FactsURL', 'EnrollURL', 'PrepaidURL', 'EnrollPhone', 'NewCustomer', 'MinUsageFeesCredits', 'avgPrice');")

  #OPENING DOWNLOADED CSV TO SAVE IT INTO DB
  with open('mypower.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['[idKey]'], i['[TduCompanyName]'], i['[RepCompany]'], i['[Product]'], i['[kwh500]'], i['[kwh1000]'], i['[kwh2000]'], i['[Fees/Credits]'], i['[PrePaid]'], i['[TimeOfUse]'], i['[Fixed]'], i['[RateType]'], i['[Renewable]'], i['[TermValue]'], i['[CancelFee]'], i['[Website]'], i['[SpecialTerms]'], i['[TermsURL]'], i['[Promotion]'], i['[PromotionDesc]'], i['[FactsURL]'], i['[EnrollURL]'], i['[PrepaidURL]'], i['[EnrollPhone]'], i['[NewCustomer]'], i['[MinUsageFeesCredits]']) for i in dr]

    #SAVING CSV INTO DB
    cur.executemany("INSERT INTO offers ('idKey', 'TduCompanyName', 'RepCompany', 'Product', 'kwh500', 'kwh1000', 'kwh2000', 'Fees/Credits', 'PrePaid', 'TimeOfUse', 'Fixed', 'RateType', 'Renewable', 'TermValue', 'CancelFee', 'Website', 'SpecialTerms', 'TermsURL', 'Promotion', 'PromotionDesc', 'FactsURL', 'EnrollURL', 'PrepaidURL', 'EnrollPhone', 'NewCustomer', 'MinUsageFeesCredits') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)

  #COMMITING CHANGES AND CLOSING CONNECTION
  con.commit()
  con.close()

def clear():
  os.system('cls' if os.name =='nt' else 'clear')

def user_input():
  """Enter your avg kwh usage"""
  try:
    usage = int(input("Enter you average energy consumption in Kwh: "))
  except ValueError:
    print("Avg energy consumption must be a number")
  else:
    return usage
  #Ask them to select current company or no company
  #ask them if they want renewable
  #Ask minimum term length

def home_screen():
  print("""
Welcome to MyPowerToChoose a script which makes finding the best deal on power easier than every. This program will weed out the misleading utility ads commonly seen on powertochoose.org.
___________________________________________________
""")

def avgprice(avgKWH):
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

    if avgKWH >= 1000:
      price = ((avgKWH-1000) * kwh2000) + (500 * kwh1000) + (500 * kwh500)

    elif avgKWH >= 500:
      price = ((avgKWH-500) * kwh1000) + (500 * kwh500)
      print price

    else:
      price = avgKWH * kwh500

#THIS IS NOT SETTING AVGPRICE ALTHOUGH PRICE IS BEING SET ABOVE
    cur.execute('UPDATE offers SET "avgPrice"={} WHERE "idKey"={}'.format(price, idkey))
    con.commit()

def view_offers():
  """View offers."""
  con = sqlite3.connect('mypower.db')
  con.text_factory = str
  cur = con.cursor()
  clear()
  print("Company           ||Price:   ||Term ||Renewable ||Rate Type")
  print("_"*50)
  i = 1
  ##Displaying Top Ten lowest prices based on power consumption
  ##Add fees in red
  ##Highlight in green if renewable
  ##Allow user to go to next page and back
  ##Show links to deals
  #clean up table format
  #Allow user to select the offer they want and the display all important info
  for row in cur.execute('SELECT * FROM offers ORDER BY avgPrice ASC LIMIT 10'):
    print("{}) {} || ${} || {} months || {}% || {} \n".format(i, row[2], row[26], row[13], row[12], row[11]))
    i += 1

if __name__ == '__main__':
  connect()
  home_screen()
  avgprice(user_input())
  view_offers()
