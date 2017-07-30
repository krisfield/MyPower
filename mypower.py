import os
import sys
import sqlite3

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
  c.execute('SELECT * FROM power_offers WHERE "[kwh500]" IS NOT NULL')
  result = c.fetchall()

  for row in result:
    kwh2000 = float(row[6])
    kwh1000 = float(row[5])
    kwh500 = float(row[4])
    idkey = row[0]

    if avgKWH >= 1000:
      price = ((avgKWH-1000) * kwh2000) + (500 * kwh1000) + (500 * kwh500)

    elif avgKWH >= 500:
      price = ((avgKWH-500) * kwh1000) + (500 * kwh500)

    else:
      price = avgKWH * kwh500

    c.execute('UPDATE power_offers SET avgprice={} WHERE "[idKey]"={}'.format(price, idkey))
    conn.commit()

#need to find way to only add this column once
#c.execute('ALTER TABLE power_offers ADD COLUMN avgprice INTEGER')
#conn.commit()

def view_offers():
  """View offers."""
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
  for row in c.execute('SELECT * FROM power_offers ORDER BY avgprice ASC LIMIT 10'):
    print("{}) {} || ${} || {} months || {}% || {} \n".format(i, row[2], row[26], row[13], row[12], row[11]))
    i += 1

conn = sqlite3.connect('mypower.db')
c = conn.cursor()

if __name__ == '__main__':
  home_screen()
  avgprice(user_input())
  view_offers()
