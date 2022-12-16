#Description: Functions to dynamically create PDF labels and print labels 
#             for printers that do not play well with CUPS (Zebra Printers)
#             This specfic file is for 3.5 x 1.375 inch labels for HPC Containers
#             Background printing function has not been tested in LINUX/MAC systems (Windows only) 

#Author: AMB
#Created: 01/12/2022

from fpdf import FPDF
import os
import time
import pandas as pd
from datetime import date
import psutil
import qrcode
import PIL

#from .GoogleChatBot import *

#Create a dynamic label with Product Image, QR Code, and Description
def createMissingLabel(orderNumber, resultsDF):
    #try:
        #print("Generating PDF Label")
        #try:
        
        print(resultsDF)
        

        


        #generate qr_code
        #print('generated QR_Code: '+ str(partNumber) + " " + str(orderNumber))

        #Make a QR code image
        qr = qrcode.make(orderNumber)
        
        #save the QR code as a png
        qr.save(os.getcwd() + "/app/static/missing_label/qr_code.png")

        #Set Paths to Images
        logo = os.getcwd()+"/app/static/img/viewrailLogoBW.png"
        #Grabs the correct part image in "label_image folder"
        #image_path = os.getcwd()+"\\app\\static\\label_image\\" + str(partNumber)+".jpg"
        #grabs the newly created qr_code
        qr_path = os.getcwd() + r"/app/static/missing_label/qr_code.png"

        #Read "FPDF2" library documentation for more info
        #Set up PDF page (dimensions in inches)
        
        #Set label Size
        pdf = FPDF(unit='in', format=[2.25,7.4])
        #create a page
        pdf.add_page()
        #set margins
        pdf.set_margins(left=.05, top=.1, right=.1)
        pdf.set_auto_page_break(auto=False)
        
        #add images, resize, and postion
        pdf.image(logo, x=.2, y=.3, w = 1)
        pdf.image(qr_path, x=1.4, y=.1, w = .75)
        # #make new line
        
        pdf.set_line_width(.01)
        pdf.line(.05,.8,2.2,.8)
        #create Indents to postion text "Arial" "Bold" Font Size: 10 (add "border=True" argument to see cell borders)
        pdf.set_font('Arial', 'B', size=16)
        
        pdf.ln(.40)

        pdf.cell(.05, .5, txt=' Missing Items List', ln=True)  
        #write Order Number
        pdf.cell(.05, .2, txt='Order: '+ orderNumber, ln=True)
        #pdf.cell(.05, .16, txt=orderNumber, ln=True)
        
        #Write Part Number
        pdf.set_font('Arial', 'B', size=10)
        pdf.cell(.05, .4, txt='Printed: ' + str(date.today()), ln=True)

        #pdf.cell(.05, .25, txt='Posts in Gaylord: ' + postsInGaylord, ln=True)

        pdf.set_font('Arial','B', size=8)
        #Write Part Description
       # pdf.cell(1, .13, txt= PartDesc1, ln=True)
        
        pdf.cell(.01,.12, txt="Product ID    Finish                   Missing", ln=True)
        #pdf.cell(.1,.12)
        
        pdf.set_font('Arial', size=8)

        for index, post in resultsDF.iterrows():
            #Add a second line if description overflows first line
            pdf.set_font('Arial', size=10)
            print(resultsDF.at[index, "product_id"])
            pdf.cell(1.85,.2, txt=str(resultsDF.at[index, "product_id"]) + "      "  + str(resultsDF.at[index, "lineItemFinishes"]))
            pdf.set_font('Arial','B', size=9)
            pdf.cell(.8,.2, txt=str(resultsDF.at[index, "missing_quantity"]), ln=True)
            pdf.set_font('Arial', size=8)
            pdf.cell(0.1,0.1)
            pdf.cell(.2,.1, txt=str(resultsDF.at[index, "product_name"]), ln=True)
            pdf.ln(.1)
        # #New Line
        # pdf.cell(1,.15)
        # #Write Quantity
        # pdf.cell(.5, .15, txt='Quantity: ' + str(quantity), ln=True)
        
        #save the pdf
        pdf.output(os.getcwd() + "/app/static/missing_label/label.pdf")

        #print label creation confirmation
        print("New Label Created")
        
        
        return True

    #except Exception as err:
    #    print(err)
        #send_bot_message("HPCBulkFeeders", f"Error Creating PDF Label. Part Number {partNumber} for Order {orderNumber}. ErrorDetails: pdf.py > GenerateLabel(), {err}")

#Prints the label to the printer in the provided zone Number
#printers need to be installed in windows and named "Zone <zoneNumber> Printer"
def printLabel():
    print("Sending Label to Printer")
    try:
        #get path for label pdf file
        filename = os.getcwd() + r"\app\static\missing_label\label.pdf" 
        #Create printer name
        os.startfile(filename, "print")
        time.sleep(60)
        for p in psutil.process_iter(): #Close Acrobat after printing the PDF
    
            if 'Acrobat' in str(p):
                p.kill()
        
        #Open File and print to correct Zone Printer
        #win32api.ShellExecute(0, "printto", filename, f'\"{printer}\"', ".", 0)
        #AutoHotKey to kill pdf program after file prints
            
    except Exception as err:
        print(err)
        
          
        
        
       


    
    
    

    # def enumHandler(hwnd, lParam):
    #     print(hwnd)
    #     print(lParam)
    #     print(win32gui.GetWindowText(hwnd))
    #     if 'adobe' in win32gui.GetWindowText(hwnd):
    #         win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    
    # win32gui.EnumWindows(enumHandler, None)
    
   
    #subprocess.call([acrobat, "/T", filename, printer])
    #cmd = f"Start-Process -FilePath \"{filename}\" -Verb Print -PassThru"
    #print(cmd)
    #subprocess.run(f"start powershell -command {cmd}")
    

# $adobe='C:\Program Files (x86)\Adobe\Reader 11.0\Reader\acrord32.exe'
# $printername='HP LaserJet Professional P 1102w'
# $drivername='HP LaserJet Professional P 1102w'
# $portname='192.168.1.100_2'
# $pdf='c:\scripts\f1040.pdf'
# $arglist='/S /T "{0}" "{1}" "{2}" {3}' -f $pdf, $printername, $drivername, $portname
# Start-Process $adobe -ArgumentList $arglist
    
    #get the default printer
    # defaultPrinter = win32print.GetDefaultPrinter()
    
    # #If the default printer is not correct, change the printer
    # if defaultPrinter != ("Zone " + str(zoneNumber) + " Printer"):
        
    #     print("Changing Default Printer")
            
    #     try:
    #         os.system("taskkill /f /im Acrobat.exe") 
    #     except:
    #         pass
    #     try:
    #         os.system("taskkill /f /im AcroRd32.exe")
    #     except:
    #         pass

        
    #     try:
    #         #set the new default printer to correct zone
    #         win32print.SetDefaultPrinter("Zone " + str(zoneNumber) + " Printer")
    #         #open pdf and print
    #         time.sleep(1)
            
    #         win32api.ShellExecute(0, "print", filename, None,  ".",  0)
    #         #time.sleep(3)
    #     except:
    #         print("Could not set Zone " + str(zoneNumber) + " Printer as default. Label was not printed")
    # #if the default printer is correct
    # else:
        
    #     #open acrobat and print the file to the default printer
    #     win32api.ShellExecute(0, "print", filename, None,  ".",  0)
        #wait a few seconds for program to open and print
        #time.sleep(3)
