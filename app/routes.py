from flask import render_template
from flask_socketio import SocketIO, emit 
from app import app
import json
import asyncio
import time
import regex as re
import random

from app.terminalDBFunctions import *
from app.pdf import *

socketio = SocketIO(app, cors_allowed_origins="*", access_control_allow_origins="*")



#Render page for Scan Input
@app.route('/', methods=['POST', 'GET'])
@app.route('/postPut', methods=['POST', 'GET'])
def index():
    title = "Missing Small Parts List Creator"
    return render_template("index.html", title=title, projectTitle=title)


###########################
#Post Label Creation Screen: postLabelCreate.js

#When an order is scanned, create a label
@socketio.on("scanLabel")
def scanLabel(rawScanData):
    print("Raw input")
    #Try to parse for Order Number from a JSON scan
    try:
        package = json.loads(rawScanData)
        try:
            orderNumber = package["order_number"]
        except:
            orderNumber = package["OrderNumber"]

    #if not, try a raw scan input
    except:
        print("Raw Order Input Detected")
        if re.search(r"\d{6}-\d{2}", rawScanData) or re.search(r"\d{6}", rawScanData): 
            orderNumber = rawScanData
        else:
             socketio.emit("fromScanLabel", (False, "invalid"))
             return
    
    #If the Scan is VALID, Continue...
    
    #Query for all unpacked Small Parts
    resultsDF = getAllSmallParts(orderNumber)

    #if there are any results, print the results, else skip
    if len(resultsDF) != 0:
    #Make and Print a label
        socketio.emit("fromScanLabel", (True, "success"))    
        createMissingLabel(orderNumber, resultsDF)
        printLabel()
    else:
        socketio.emit("fromScanLabel", (False, "no_parts_found"))
        return

    
        
    return




    