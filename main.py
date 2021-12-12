import sqlite3
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

# Router
@app.get("/")
def root():
  return {"hey Hadile": "It works !"}
#--------------------------
#(1) register customer
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
            INSERT INTO Customer (CustomerAccount, VAT, FullName, Email, Password)
            VALUES ({customer}, {company}, {fullname}, {email}, {password})
            '''.format(customer=str(values_dict['CustomerAccount']) ,
                       company=str(values_dict['VAT']),
                       fullname=values_dict['FullName'],
                       email=str(values_dict['Email']),
                       password=str(values_dict['Password'])))
    print (query_customer)
    # Close the DB
    database.close()
    return True
  #--------------------------------------------------------
  # (2) a company creates subscriptions in Subscriptions
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
  # (3.1)create a quote for each customer
  #---------------------------------------------------------
@app.post("/register_quote")
async def register_Quote(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    
    # Step 1: retrieve the subscription via VAT
    query_quote = database.execute(''' 
                    SELECT VAT FROM Subscriptions
                    WHERE SubscriptionN = {}               
                    '''.format(str(values_dict['SubscriptionN'])))   # where = je donne les subscitpionsN
    # We then store the results of the query with fetchall.
    quote_results = query_quote.fetchall()[0][0]
    print(quote_results)

    # thanks to the VAT that we get, we will retrieve the customer list that are in this company

    query_quote2 = database.execute(''' 
                    SELECT CustomerAccount, FullName FROM Customer
                    WHERE VAT = {}               
                    '''.format(str(quote_results)))  #the result will be all the customers that belong to the company that has the VAT stored previously ==> NOT A LIST!! BC NO FETCHALL 
    # We then store the results of the query with fetchall.
    quote_results2 = query_quote2.fetchall() # here, it becomes a list [(customerAccount,Fullname),();()...]
    print(quote_results2)
    x = []
  # Jusqu'ici, we have succeeded to retrieve the VAT and all its customers based ONLYYYY on the subcriptionN
    for i in quote_results2: 
      print(i) 
      if str(i[1]) == str(values_dict['FullName']): # valuedict = données que on va donner, cad ce qui sera mis dans le http 
        x =str(i[0])
        
        query_quote3 = database.execute('''
            INSERT INTO Quote (QuoteID, SubscriptionN, CustomerAccount) 
            VALUES ({quote}, {subscription}, {customer})             
            '''.format(quote=str(values_dict['QuoteID']), subscription=str(values_dict['SubscriptionN']), customer=x))
        print(query_quote3)
      else: 
        print("Client does not exist")
# valuedict = données que on va donner, cad ce qui sera mis dans le http 

    # Close the DB
    database.close()
    return True
#--------------------------------------------------------------------------------
#(3.2) if quote accepted by customer, activate subscription for the customer
#--------------------------------------------------------------------------------

 #---------------------------------------
 #(3.3) update Accepted in Quote
 #--------------------------------------
@app.post("/accept_quote")
async def accept_quote(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
  
    secret_query = database.execute(''' 
                             SELECT Password FROM Customer
                             WHERE CustomerAccount = {}
                  '''.format(values_dict['CustomerAccount']))
  
    password = secret_query.fetchall()
    print(password)
    if password == values_dict['Password']:
      #return "error"
       accept_query = database.execute(''' 
                    UPDATE Quote
                    SET Accepted = 1
                    WHERE CustomerAccount = {customer}       
                    '''.format(customer = values_dict['CustomerAccount']))
       accepted = accept_query.fetchall()
       print(accepted)
       print('quote_accepted')
    else:
      print('incorrect password')
    # Close the DB
      database.close()
      return True
 #---------------------------------------------------
 # (4) activate the subscription in Subscription (update)
 #---------------------------------------------------
@app.post("/activate_subscription")
async def activate_Subscription(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    query_accepted=database.execute('''SELECT Accepted FROM Quote
                                    WHERE CustomerAccount = {}
                                    '''.format(values_dict['CustomerAccount'])) 
    
    accepted_results = query_accepted.fetchall()
    print(accepted_results)
    if accepted_results == '1' :
         query_activated=database.execute('''UPDATE Subscriptions 
                                        SET Activated = 1
                                        WHERE CustomerAccount = {customer}       
                                        '''.format(customer = values_dict['CustomerAccount']))
         activated_results = query_activated.fetchall()
         print(activated_results)
         print('subscription activated')
    else: 
      print('subscription can not be activated')    
    # Close the DB
      database.close()
      return True                  

#---------------------------------------------------------------------
# (5) for an activated subscription, we will send an invoice  PAS DEFINITIF
#---------------------------------------------------------------------
@app.post("/send_invoice")
async def send_invoice(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    query_accepted_for_invoice=database.execute('''SELECT Accepted FROM Quote
                                    WHERE SubscriptionN = {}
                                    '''.format(values_dict['CustomerAccount'])) 
send_results = query_accepted_for_invoice.fetchall()
    print(send_results)
    if send_results == '1' :                   #We can send an invoice only if the quote is accepted
         query_send_invoice=database.execute('''UPDATE Invoice 
                                        SET Pending = 1
                                        WHERE QuoteID = {quote_number}       
                                        '''.format(quote_number = values_dict['QuoteID']))
         send_invoice_results = query_send_invoice.fetchall()
         print(send_invoice_results)
         print('invoice sent to customer')
    else: 
      print('invoice can not be sent')    
    # Close the DB
      database.close()
      return True

#---------------------------------------------------
# if not paid send a pending invoice
#----------------------------------------------------


#---------------------------------------------------------
# if paid, delete pending 
#---------------------------------------------------------




if _name_ == '_main_':
  uvicorn.run(app, host='127.0.0.1', port=8000)it
