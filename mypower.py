"""Script to search for best Texas electricity plan availble"""

import os

import csv
import datetime
import textwrap
import urllib.request
from databasemanager import DatabaseManager
from terminaltables import SingleTable

def clear():
    """Clears the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def db_build():
    """Creating MyPower database if one doesn't exist"""
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
    with open('mypower.csv', 'rt') as fin:
        imported_csv = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['[idKey]'], i['[TduCompanyName]'], i['[RepCompany]'], i['[Product]'], i['[kwh500]'], i['[kwh1000]'], i['[kwh2000]'], i['[Fees/Credits]'], i['[PrePaid]'], i['[TimeOfUse]'], i['[Fixed]'], i['[RateType]'], i['[Renewable]'], i['[TermValue]'], i['[CancelFee]'], i['[Website]'], i['[SpecialTerms]'], i['[TermsURL]'], i['[Promotion]'], i['[PromotionDesc]'], i['[FactsURL]'], i['[EnrollURL]'], i['[PrepaidURL]'], i['[EnrollPhone]'], i['[NewCustomer]'], i['[MinUsageFeesCredits]']) for i in imported_csv]

        #SAVING CSV INTO DB
        dbmgr.querymany("INSERT INTO offers ('idKey', 'TduCompanyName', 'RepCompany', 'Product', 'kwh500', 'kwh1000', 'kwh2000', 'FeesCredits', 'PrePaid', 'TimeOfUse', 'Fixed', 'RateType', 'Renewable', 'TermValue', 'CancelFee', 'Website', 'SpecialTerms', 'TermsURL', 'Promotion', 'PromotionDesc', 'FactsURL', 'EnrollURL', 'PrepaidURL', 'EnrollPhone', 'NewCustomer', 'MinUsageFeesCredits') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)

      #DELETES LAST ROW
        dbmgr.query('DELETE FROM offers WHERE "idKey"="END OF FILE";')
    #COMMITING CHANGES AND CLOSING CONNECTION
    del dbmgr

def db_check():
    """Shows last time data was downloaded from Power To Choose and gives option to update"""
    clear()
    if os.path.isfile('mypower.csv'):
        csv_last_download = datetime.datetime.fromtimestamp(os.stat('mypower.csv').st_mtime)
        print("This database was last updated from Power to Choose at {}\n\n".format(csv_last_download))
        if input("Would you like to update this database? [y/N]: ").lower() == 'y':
            db_build()
    else:
        db_build()

def user_input(tdu):
    """Enter your preferences to find the best deal for your situation"""
    user_pref = {}
    while True:
        try:
            tdu_num = int(input("Enter number of your TDU: ")) - 1
            ##need to have a check that this value is in range
        except ValueError:
            print("Oops! That was not a valid number. Try again...")
        else:
            if tdu_num in tdu:
                user_pref["tdu"] = tdu[tdu_num]["tdu_name"]
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
    """Displays MyPower menu/navigation"""
    clear()
    print("##################################")
    print("MyPower 1.0")
    print("################################## \n")
    print("\n".join(textwrap.wrap("""Welcome to MyPower, a program which allows you to easily find the best deal when it comes to electricity. Simply input your average monthly power usage and then compare availbe offers by their estimated average monthly cost.
  """, 50)))

    input("\n\nPress enter to continue: ")

def avg_price(user_preferences):
    """Estimates monthly electric bill"""
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

        if user_preferences["usage"] >= 1000:
            price = round(((user_preferences["usage"]-1000) * kwh2000) + (500 * kwh1000) + (500 * kwh500), 0)

        elif user_preferences["usage"] >= 500:
            price = round(((user_preferences["usage"]-500) * kwh1000) + (500 * kwh500), 0)

        else:
            price = round(user_preferences["usage"] * kwh500, 0)

        deal_price = (idkey, price)
        dbmgr.query('INSERT INTO user VALUES (?, ?)', deal_price)

    del dbmgr

def build_tdu():
    """Creates list of available TDUs"""
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

def view_offers(user_preferences):
    """View offers."""
    clear()
    dbmgr = DatabaseManager("mypower.db")

    data = []
    offer_ids = []
    data.append(['id', 'Company', 'Price ($)', 'Term (months)', 'Renewable (%)', 'Rate Type'])

    for row in dbmgr.query('SELECT offers.idKey, offers.RepCompany, user.avgPrice, offers.TermValue, offers.Renewable, offers.RateType FROM offers INNER JOIN user ON offers.idKey = user.idKey WHERE offers.TduCompanyName=? AND offers.TermValue >=? AND offers.Renewable >=? AND offers.MinUsageFeesCredits = ? ORDER BY user.avgPrice ASC LIMIT 10', (user_preferences["tdu"], user_preferences["contract term"], user_preferences["renewable"], 'FALSE')):
        data.append([row[0], row[1], row[2], row[3], row[4], row[5]])
        offer_ids.append(row[0])

    table = SingleTable(data, title="Best offers")
    print(table.table)
    print("Above are the best deals based on your average {}Kwh usage\n\n".format(user_preferences["usage"]))
    return offer_ids
    del dbmgr

def offer_details(offers):
    """Displays details of selected offer"""
    dbmgr = DatabaseManager("mypower.db")
    data = []

    while True:
        try:
            selected_offer = int(input("Enter the offer id to view more details: ").lower())
        except ValueError:
            print("Oops! That was not a valid number. Try again...")
        else:
            if selected_offer in offers:
                chosen_offer = (selected_offer, )
                dbmgr.query('SELECT offers.Product, offers.idKey, offers.RepCompany, user.avgPrice, offers.kwh500, offers.kwh1000, offers.kwh2000, offers.FeesCredits, offers.TermValue, offers.FactsURL, offers.EnrollURL FROM offers INNER JOIN user ON offers.idKey = user.idKey WHERE offers.idKey = ?', chosen_offer)
                offer = dbmgr.fetchone()
                break
            else:
                print("Offer ID {} is not a valid selection".format(selected_offer))

    clear()
    data.append(['Plan #{}'.format(offer[1]), '{}'.format(offer[0])])
    data.append(['Company', offer[2]])
    data.append(['Estimated Monthly Bill', '${}'.format(offer[3])])
    data.append(['Price breakdown', '[500Kwh: ${}]  [1000Kwh: ${}]  [2000Kwh: ${}]'.format(offer[4], offer[5], offer[6])])
    data.append(['Contract Length', '{} months'.format(offer[8])])
    table = SingleTable(data, title="Plan details")
    table.justify_columns[1] = 'left'
    print(table.table)
    print('Details: {}'.format(offer[9]))
    print('Enroll: {}'.format(offer[10]))
    print('\n(Cmd + double-click to open urls)\n\n')

    choice = input("Press any key to return to your offers or 'q' to quit: ").lower()
    clear()

    if choice == 'q':
        return False
    else:
        return True

if __name__ == '__main__':
    ACTIVE = True
    menu()
    db_check()
    TDU_CHOICES = build_tdu()
    PREFERENCES = user_input(TDU_CHOICES)
    avg_price(PREFERENCES)
    while ACTIVE is True:
        AVAILABLE_OFFERS = view_offers(PREFERENCES)
        ACTIVE = offer_details(AVAILABLE_OFFERS)
