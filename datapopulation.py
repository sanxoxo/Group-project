import sqlite3
database = sqlite3.connect('databaseproject.db', isolation_level=None)

def insert_Company(vat, companyname, adress, bankaccountnumber):
    database.execute(''' 
            INSERT INTO Company(VAT, CompanyName, Adress, BankAccountN)
            VALUES(?,?,?,?)''', (vat, companyname, adress, bankaccountnumber))
    print("company inserted")

insert_Company(23456, "Amazon", "Antwerpen", 987,)
insert_Company(34567, "Netflix", "Amsterdam", 764)
insert_Company(45678,'damas','brussels', 555)
insert_Company(12345, "ben", "nairobi", 123)
