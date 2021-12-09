import sqlite3
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

# Router
@app.get("/")
def root():
  return {"hey Hadile": "It works !"}
#--------------------------
#register customer
#--------------------------
@app.post("/register_customer")
async def register_customer(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    query_company = database.execute(''' 
                    SELECT VAT FROM Company
                    WHERE VAT = {}               
                    '''.format(str(values_dict['VAT'])))
    # We then store the results of the query with fetchall.
    company_results = query_company.fetchall()[0]
    print(company_results)
    # Step 2: create a new customer:
    query_customer = database.execute('''
            INSERT INTO Customer (CustomerAccount, VAT)
            VALUES ({customer}, {company})
            '''.format(customer=str(values_dict['CustomerAccount']) ,company=str(values_dict['VAT'])))
    print (query_customer)
    # Close the DB
    database.close()
    return True
  #--------------------------------------------------------
  # a company creates subscriptions in Subscriptions
  #---------------------------------------------------------
@app.post("/register_subscription")
async def register_subscription(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    query_company = database.execute(''' 
                    SELECT VAT FROM Company
                    WHERE VAT = {}               
                    '''.format(str(values_dict['VAT'])))
    # We then store the results of the query with fetchall.
    company_results = query_company.fetchall()[0]
    print(company_results)
    # Step 2: create a new subscription:
    query_subscription = database.execute('''
            INSERT INTO Subscriptions (SubscriptionN, Price, VAT, SubscriptionInfo)
            VALUES ({subscription}, {price}, {company}, {info})
            '''.format(subscription=str(values_dict['SubscriptionN']) ,
                       price=str(values_dict['Price']) ,
                       company=str(values_dict['VAT']),
                       info=str(values_dict['SubscriptionInfo'])))
    print (query_subscription)
    # Close the DB
    database.close()
    return True
#--------------------------------------------------------
# create a quote for each customer (via subscriptions)    PAS DEFINITIF
#---------------------------------------------------------
  @app.post("/register_quote")
async def register_Quote(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    # Step 1: retrieve the customer

    query_customer = database.execute(''' 
                    SELECT CustomerAccount FROM Customer
                    WHERE VAT = {}               
                    '''.format(str(values_dict['VAT'])))
    # We then store the results of the query with fetchall.
    customer_results = query_customer.fetchall()
    print(customer_results)
    # Step 2: create a new quote for the customer and subscription:
    #query_quote = database.execute('''
            #INSERT INTO Quote(CustomerAccount, SubscriptionN) 
            #VALUES ({customer}, {subscription})             
            #'''.format(customer=str(customer_results), subscription=str(values_dict['SubscriptionN'])))
    #print(query_quote)
    # Close the DB
    database.close()
    return True
