import requests
import pathlib
import configparser
import json
import os
import pandas as pd
import math
from datetime import datetime

def dbconfig():
    moddir = os.path.abspath(os.path.dirname(__file__))

    configPath = pathlib.Path(moddir) / '.gql_config.txt'
    
    config = configparser.ConfigParser()
    config.read(configPath)
    
    url = config.get('CONNECTION', 'URL')
    
    api_token = config.get('CONNECTION', 'TOKEN')
    headers = {'x-api-key': api_token}
    return url, headers


#Use Terminals graphQL query to get order status by type
#kinda broken, when an order is completed, the query returns null... 
#but it is faster than the checkForPackedSmallParts2 query, so try this first,
# if it returns null, then call checkForPackedSmallParts2
def getAllSmallParts(orderNumber):
    
    #CREDENTIALS = pathlib.Path(__file__).resolve().parent.parent / ".credentials"
    #connection_factory = ConnectionFactory(CREDENTIALS)
    

    # query = f"""query getStatusOfSmallParts {{
    # orderByNumber(order_number: \"{orderNumber}\") {{
    #         packableItems {{
    #             quantity
    #             quantity_packed
    #             lineItemFinishes
    #             itemType
    #             product {{
    #                 id

    #                 od1ProductionType {{
    #                 id
    #                 name
    #                 }}
    #                 od1Group {{
    #                 name
    #                 }}
    #             }}
    #         }}
    #     }}
    # }}
    # """

    query = f"""
        query getStatusOfSmallParts {{
            orderByNumber(order_number: \"{orderNumber}\") {{
                packableItems {{
                getProduct{{
                    id
                }}
                quantity
                quantity_packed
                lineItemFinishes
                itemType
                }}
            }}
        }}
    """

    # query= f"""
    #     query GetPackedStatusByItemType2 {{  
    # orderByNumber(order_number: \"{orderNumber}\"){{
    #     productionItems{{
    #         product{{
    #             id
    #         }}
    #         id
    #         isPacked
    #         productionItemStep{{
    #             in_process_metal
    #             }}
    #         }}
    #     }} 
    # }}"""


    url, headers = dbconfig()
    request = requests.post(url=url, json={'query': query}, headers=headers)
    
    
    if request.status_code == 200:
        # Return only the dictionary contents at the orderlineitems level of the query results.
        request = request.json()
        
        #get the data from query
        
        statusList = request['data']['orderByNumber']['packableItems']
        
        #Read each category of small parts and update overall order status
        #try:    
        #statusListJSON = json.loads(statusList[0])
        # except:
        #     statusListJSON = {}
        
        print(statusList)
        output = ""
        resultsDF = pd.read_json(json.dumps(statusList[:]))
        print(resultsDF)
        resultsDF = resultsDF[resultsDF.itemType == "SMALL_PARTS"].reset_index()
        print(resultsDF)
        resultsDF = resultsDF[resultsDF.quantity != resultsDF.quantity_packed].reset_index()
        

        resultsDF["product_id"] = resultsDF["getProduct"].apply(pd.Series)
        resultsDF = resultsDF.drop(["getProduct", "index", "level_0"], axis=1)
        
        resultsDF["missing_quantity"] = resultsDF["quantity"] - resultsDF["quantity_packed"]
        print(resultsDF)
        return resultsDF
        
    else:
        raise Exception("Query failed to run. returning code of {}. {}".format(request.status_code, query))




def setPostAsFinished(orderLineItemID, orderNumber):
    mutation = f"""
        mutation setPostAsFinished {{
            completeSomeOrderProductionSteps(
                id: \"{orderNumber}\"
                lineItemIds: [{orderLineItemID}]
                step: FINISHED
                quantity: 1
                )

            {{
                id
            }}
        }}
    """
    
    url, headers = dbconfig()
    request = requests.post(url=url, json={'query': mutation}, headers=headers)
    
    if request.status_code == 200:
        
        request = request.json()
        
        return True
    else:
        raise Exception
        
