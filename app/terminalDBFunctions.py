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
                    name
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
        
        resultsDF = pd.read_json(json.dumps(statusList[:]))
        
        resultsDF = resultsDF[resultsDF.itemType == "SMALL_PARTS"].reset_index()
        
        resultsDF = resultsDF[resultsDF.quantity != resultsDF.quantity_packed].reset_index()
        
        print(resultsDF)
        
        if len(resultsDF != 0):
            resultsDF[["product_id", "product_name"]] = resultsDF["getProduct"].apply(pd.Series)
            resultsDF = resultsDF.drop(["getProduct", "index", "level_0"], axis=1)
            print(resultsDF)
            resultsDF["missing_quantity"] = resultsDF["quantity"] - resultsDF["quantity_packed"]
            
            resultsDF = resultsDF.sort_values("product_id", ascending=True).reset_index()

            aggregation_functions = {'missing_quantity': 'sum', "product_name":'first'}
            resultsDF = resultsDF.groupby(["product_id","lineItemFinishes"], as_index=False).aggregate(aggregation_functions)
            
            PC_COLOR = {

                'PC - Black':'Black',
                'Platinum Black':'P-Black',
                'PC: Black':'Black',
                'PC Fluoropolymer: Antique Bronze':'F-Antique Br',
                'PC Fluoropolymer: Apollo White':'F-Apollo White',
                'PPG Fluoropolymer: Apollo White':'F-Apollo White',
                'PC Fluoropolymer: Black':'F-Black',
                'PC Fluoropolymer: Bone White':'F-Bone White',
                'PC Fluoropolymer: Colonial Grey':'F-Colo Grey',
                'PC Fluoropolymer: Fashion Grey':'F-Fash Grey',
                'PC Fluoropolymer: Platinum Matte':'F-Plat Matt',
                'PC Fluoropolymer: Silver Spark':'F-Silver Sprk',
                'PC Fluoropolymer: Speedboat Silver':'F-SBS',
                'PC: Apollo White':'Apollo White',
                'PC: Bone White':'Bone White',
                'PC: Bronze Akzonobel GM2007':'Bronze Akz',
                'PC: Brushed Aluminum w/ Clear - SRSF-90299':'Brsh-Al-Clear',
                'PC: Brushed w/ Clear':'Brsh w/ Clear',
                'PC: Charcoal':'Charcoal',
                'PC: Clear Finish':'Clear Finish',
                'PC: Colonial Grey':'Colonial Grey',
                'PC: Copper Vein':'Copper Vein',
                'PC: Fashion Grey':'Fashion Grey',
                'PC: Hunter Green':'Hunter Green',
                'PC: Light Blue':'Light Blue',
                'PC: Lithonia Bronze':'Lith Bronze',
                'PC: Mineral Bronze':'Mineral Bronze',
                'PC: Rust Spice':'Rust Spice',
                'PC: Sandstone':'Sandstone',
                'PC: Seawolf':'Seawolf',
                'PC: Speedboat Silver':'Speedboat Silv',
                'PC: Super C-33 Bronze':'C-33 Brnze',
                'PC: Super Bronze':'Super Bronze',
                'PC: Tube Brown':'Tube Brown',
                'PC: Legacy Speedboat Silver':'Legacy SBS',
                'PC: Legacy Copper Vein':'Legacy Copp Vein',
                'Brushed Stainless':'Brushed Stainless',
                'Platinum Apollo White':'P-Apollo White',
                'Platinum Bronze':'P-Bronze',
                'PC - Black For Glass Hardware': 'Black Glass',
                'N/A':'N/A',
                'None': 'None'

            }

            for index, row in resultsDF.iterrows():
                finish = resultsDF.at[index, "lineItemFinishes"]
                print(finish)
                shortFinish = PC_COLOR[finish]
                print(shortFinish)

                resultsDF.at[index, "lineItemFinishes"] = shortFinish

            
            print(resultsDF)
            return resultsDF
        
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
        
