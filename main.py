import sqlite3
from fastapi import FastAPI, Request
import uvicorn
app = FastAPI()

# Router
@app.get("/")
def root():
  return {"hey Hadile": "It works !"}
#--------------------------
#1 register customer
#--------------------------
@app.post("/register_customer")
async def register_customer(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    query_customer = database.execute('''
            INSERT INTO Customer(CustomerAccount, VAT, FullName, Country, RegistreNational, Password)
            VALUES ({customer}, {company}, {fullname}, {country}, {registrenational}, {password})
            '''.format(customer=(values_dict['CustomerAccount']) ,
                       company=(values_dict['VAT']),
                       fullname=values_dict['FullName'],
                       country=(values_dict['Country']),
                       registrenational=(values_dict['RegistreNational']),
                       password=(values_dict['Password'])))
    print (query_customer)
    # Close the DB
    database.close()
    return True
  #--------------------------------------------------------
  # 2 a company creates subscriptions in Subscriptions
  #---------------------------------------------------------
@app.post("/register_subscription")
async def register_subscription(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    query_subscription = database.execute('''
                         INSERT INTO Subscriptions (SubscriptionN, Price, VAT, SubscriptionInfo)
                         VALUES ({subscription}, {price}, {company}, {info})
                         '''.format(subscription=(values_dict['SubscriptionN']),
                             price=(values_dict['Price']),
                             company=(values_dict['VAT']),
                             info=(values_dict['SubscriptionInfo'])))
    print (query_subscription)
    # Close the DB
    database.close()
    return True
  #--------------------------------------------------------
  # 3 create a quote for each customer
  #---------------------------------------------------------
  # inputs: quoteid, subscription, registre national
@app.post("/register_quote")
async def register_quote(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    # Step 1: retrieve the subscription via VAT

    query_quote = database.execute(''' 
                  SELECT VAT FROM Subscriptions
                  WHERE SubscriptionN =  {}               
                  '''.format(values_dict['SubscriptionN']))  
    # where = je donne les subscitpionsN
    # We then store the results of the query with fetchall.
    quote_results = query_quote.fetchall()[0][0]
    print(quote_results)

    # thanks to the VAT that we get, we will retrieve the customer list that are in this company
    query_quote2 = database.execute(''' 
                  SELECT  RegistreNational FROM Customer
                  WHERE VAT = {}               
                  '''.format(str(quote_results)))  #the result will be all the customers that belong to the company that has the VAT stored previously ==> NOT A LIST!! BC NO FETCHALL 
    # We then store the results of the query with fetchall.
    quote_results2 = query_quote2.fetchall()
    # here, it becomes a list [(customerAccount,Fullname),();()...]
    print(quote_results2)
    
    query_price = database.execute('''
                                   SELECT Price FROM Subscriptions
                                   WHERE SubscriptionN ={}
                                   '''.format(values_dict['SubscriptionN']))
    price_results = query_price.fetchall()[0][0]
    print(price_results)
    
    pricevat = float(price_results)*1.21
    print(pricevat)
  # Jusqu'ici, we have succeeded to retrieve the VAT and all its customers based ONLYYYY on the subcriptionN
    for i in quote_results2: 
      print(i) 
      if str(i[0]) == str(values_dict['RegistreNational']): # valuedict = données que on va donner, cad ce qui sera mis dans le http 
        x =str(i[0])
        
        query_quote3 = database.execute('''
            INSERT INTO Quote (QuoteID, SubscriptionN, RegistreNational, Price, Accepted, PriceVAT) 
            VALUES ({quote}, {subscription}, {registrenational}, {price}, {accepted}, {pricevat})             
            '''.format(quote=str(values_dict['QuoteID']),
                       subscription=str(values_dict['SubscriptionN']),
                       price=price_results,
                       accepted='FALSE',
                       pricevat=pricevat,
                       registrenational=x))
        print(query_quote3)
      else: 
        print("Client does not exist for this VAT:"+ str(quote_results))
# valuedict = données que on va donner, cad ce qui sera mis dans le http
   
    # Close the DB
    database.close()
    return True
 #---------------------------------------
 #update Accepted in Quote
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
  
    password = secret_query.fetchall()[0][0]
    print(password)
    if (password) == (values_dict['Password']):
      print('yess')
      accept_query = database.execute(''' 
                                       UPDATE Quote 
                                       SET Accepted = TRUE
                                       WHERE QuoteID = {quote}       
                                       '''.format(quote = str(values_dict['QuoteID'])))
       
      print('quote accepted')
      a = database.execute('''
                           SELECT * FROM  Quote
                           ''')
      a_results=a.fetchall()
      print(a_results)
    else:
      print('quote not accepted')
      
   
    # Close the DB
    database.close()
    return True
 #---------------------------------------------------
 #activate the subscription in Subscription (update)
 #---------------------------------------------------
@app.post("/activate_subscription")
async def activate_Subscription(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
    query_accepted=database.execute('''SELECT Accepted FROM Quote
                                       WHERE QuoteID= {}
                                    '''.format(values_dict['QuoteID'])) 
    accepted_results=query_accepted.fetchall()
    print(accepted_results)
    
    if int(accepted_results[0][0])==1 :
         query_activated=database.execute('''UPDATE Quote 
                                          SET Activated = TRUE
                                          WHERE QuoteID = {}     
                                          '''.format(values_dict['QuoteID']))
         print('subscription activated')
         b=database.execute('''
                            SELECT * FROM Quote
                            ''')
         b_results=b.fetchall()
         print(b_results)
    else: 
      print('subscription can not be activated')    
       #Close the DB
    database.close()
    return True                  
#---------------------------------------------------------------------
# for an activated subscription, send invoice
#---------------------------------------------------------------------
@app.post("/send_invoice")
async def send_invoice(payload: Request):
    values_dict = await payload.json()
    # Open the DB
    database = sqlite3.connect('databaseproject.db', isolation_level=None)
#select tous les subscriptionN et pricevat d'un registre national qui sont activated dans quote
    query_price = database.execute('''
                                   SELECT PriceVAT FROM Quote
                                   WHERE RegistreNational = {registre}
                                   '''.format(registre=values_dict['RegistreNational']))
    price_results=query_price.fetchall()
    print(price_results)
    query_price2 = database.execute('''
                                    SELECT SubscriptionN FROM Subscriptions
                                    WHERE Activated = TRUE
                                    AND RegistreNational = {registre}
                                    '''.format(registre=values_dict['RegistreNational']))
    h=[]
    
#calcule la somme de tous les pricevat d'un registre national

   
    # Close the DB
    database.close()
    return True
#---------------------------------------------------
# cutomer pays the invoice (update paid)
#----------------------------------------------------
#@app.post("/pay_invoice")
#async def activate_Subscription(payload: Request):
    #values_dict = await payload.json()
    # Open the DB
    #database = sqlite3.connect('databaseproject.db', isolation_level=None)
    #query_accepted=database.execute('''SELECT Accepted FROM Quote
                                    #WHERE QuoteID = {}
                                    #'''.format(values_dict['QuoteID'])) 
    
    
    #accepted_results = query_accepted.fetchall()
    #print(accepted_results)
    
    #if accepted_results == '1' and values_dict['Password'] == 'Password'     :
         #query_pay=database.execute('''UPDATE Invoice 
                                        #SET Paid = 1
                                        #WHERE CustomerAccount = {customer}       
                                        #'''.format(customer = values_dict['CustomerAccount']))
         #activated_results = query_activated.fetchall()
         #print(activated_results)
         #print('subscription activated')
    #else: 
      #print('subscription can not be activated')    
    # Close the DB
    database.close()
    return True          


#------------------------------------
#if not paid send a pending incoice 
#------------------------------------




#---------------------------------------------------------
# else, delete pending 
#---------------------------------------------------------




if __name__ == '__main__':
  uvicorn.run(app, host='127.0.0.1', port=8000)
