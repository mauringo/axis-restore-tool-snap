from flask import Flask, redirect, render_template, request, session, url_for, Response, Blueprint

import json
import time
import sys
import os
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN=""
DRIVELIST=[]
##settings 

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
app = Flask(__name__, static_url_path='')

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

os.chdir(dir_path)

#TARGET to be modified
IPADDRESS='192.168.15.1'
if 'SNAP' in os.environ:
    IPADDRESS='localhost'




########## serving functions

@app.route('/axisrestoretool/')
def index():
    
    return app.send_static_file('axisrestoretool/index.html')

@app.route('/axisrestoretool/filemanager')
def systemdevices():
    
    return app.send_static_file('axisrestoretool/filemanager.html')

@app.route('/axisrestoretool/staticdata',methods=['GET', 'POST'])
def staticdata():              
    global TOKEN
    global IPADDRESS
    global drivesList
    try:
 
        
        TOKEN=auth(ip=IPADDRESS)
        drivesList=buildDrivesInfos(TOKEN,IPADDRESS)
        return Response(json.dumps(drivesList), mimetype='json')
    except Exception as e:
        print(e)

@app.route('/axisrestoretool/backupany',methods=['GET', 'POST'])
def backupany():              
    global TOKEN
    global IPADDRESS
    global drivesList
    try:
        
        drivesList=buildDrivesInfos(TOKEN,IPADDRESS)
        for drive in drivesList:
            bakupOneDrive(TOKEN,drive,IPADDRESS)
        myinfo=drivesList
        return Response(json.dumps(myinfo), mimetype='json')
    except Exception as e:
        print(e)

@app.route('/axisrestoretool/restoreany',methods=['GET', 'POST'])
def restoreany():              
    global TOKEN
    global IPADDRESS
    global drivesList
    try:
        
        drivesList=buildDrivesInfos(TOKEN,IPADDRESS)
        for drive in drivesList:
            restoreOneDrive(TOKEN,drive,IPADDRESS)
        myinfo=drivesList
        return Response(json.dumps(myinfo), mimetype='json')
    except Exception as e:
        print(e)

    

@app.route('/axisrestoretool/backuprestoreinfo',methods=['GET', 'POST'])
def backuprestoreinfo():              
    global TOKEN
    global IPADDRESS
    global drivesList
    try:
        

        myinfo=checkStatus(TOKEN,drivesList,IPADDRESS)
    
        return Response(json.dumps(myinfo), mimetype='json')
    except Exception as e:
        print(e)


@app.route('/axisrestoretool/files',methods=['GET', 'POST'])
def dataproc():              

    return Response(getSetupInfo(), mimetype='json')  



## functions used to pack the json 

  
def getSystemUsageInfo():
    try:
        info={}
        info['CPU']="pippo"
        

        return json.dumps(info)
        
    except Exception as e:
        print(e)

######### Functions :)
def auth(name="boschrexroth",password="boschrexroth",ip="localhost"):
    
    # defining the api-endpoint 
    API_ENDPOINT = "https://"+ip+"/identity-manager/api/v2/auth/token"

    # data to be sent to api
    data = {'name':name,
            'password':password}

    # sending post request and saving response as response object
    #print(API_ENDPOINT)
    r = requests.post(url = API_ENDPOINT, json = data, verify=False)
    if r.status_code==201:
        # extracting response text 
        pastebin_url = r.json()['access_token']
        return(pastebin_url)
    return None

##FilesSearchAndDelete

def deleteFile(bearer,filename, ip="localhost"):
    API_ENDPOINT = "https://"+ip+"/solutions/webdav/appdata%2FDRIVEConnect%2F"+filename
    headers = {"authorization": "Bearer "+bearer}
    #print(headers)
    response = requests.delete(API_ENDPOINT, headers=headers, verify=False)
    #print("Status Code", response.status_code)
    return  response.status_code

def getFilesList(bearer, ip="localhost"):
    API_ENDPOINT = "https://"+ip+"/solutions/api/v1/solutions/DefaultSolution/filesystem?dir=%2Fconfigurations%2Fappdata%2FDRIVEConnect%2F"

    headers = {"authorization": "Bearer "+bearer}
    #print(headers)
    response = requests.get(API_ENDPOINT, headers=headers, verify=False)
    #print("Status Code", response.status_code)
    #print("JSON Response ", response.json())
    out=response.json()
    files=[]
    for file in out['entries']:
        #print(file['name'])
        if '.par' in file['name']:
            files.append(file['name'])
    #print(files)
    return  files

#backup and restore functions
def bakupOneDrive(bearer,driveInfo, ip="localhost"):
    drive=driveInfo['drive']
    filename=driveInfo['ip']+'-0.par'
    API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/export-parameter"
    headers = {"authorization": "Bearer "+bearer}
    #print(headers)
    myobj = {"type": "object", "value": {"fileName": filename, "backupType": "All"}}
    response = requests.post(API_ENDPOINT, headers=headers, json = myobj,verify=False)
    mydata=response.json()
    if driveInfo['subDeviceCount']==2:
        filename=driveInfo['ip']+'-1.par'
        API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-1/export-parameter"
        headers = {"authorization": "Bearer "+bearer}
        #print(headers)
        myobj = {"type": "object", "value": {"fileName": filename, "backupType": "All"}}
        response = requests.post(API_ENDPOINT, headers=headers, json = myobj,verify=False)
        mydata=response.json()

    return  mydata

def restoreOneDrive(bearer,driveInfo, ip="localhost"):
    drive=driveInfo['drive']
    filename=driveInfo['ip']+'-0.par'
    headers = {"authorization": "Bearer "+bearer}
    API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/import-parameter"
    
    #print(headers)
    myobj = {"type": "object", "value": {"fileName": filename}}
    response = requests.post(API_ENDPOINT, headers=headers, json = myobj,verify=False)
    mydata=response.json()
    if driveInfo['subDeviceCount']==2:
        filename=driveInfo['ip']+'-1.par'
        API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-1/import-parameter"
        
        #print(headers)
        myobj = {"type": "object", "value": {"fileName": filename}}
        response = requests.post(API_ENDPOINT, headers=headers, json = myobj,verify=False)
        mydata=response.json()

    return  mydata


def checkStatus(bearer,drivesList, ip="localhost"):
    newdrivesList=[]
    headers = {"authorization": "Bearer "+bearer}
    for driveInfo in drivesList:
        infos=[]
        drive=driveInfo['drive']
        API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/export-parameter?type=browse"
        response = requests.get(API_ENDPOINT, headers=headers, verify=False)
        mytask=response.json()['value']
        if len(mytask)==0:
            mydata1=None
        else:
            API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/export-parameter/"+mytask[0]
            response = requests.get(API_ENDPOINT, headers=headers, verify=False)
            mydata1=response.json()['value']
            mydata1.pop('id', None)
            
        API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/import-parameter?type=browse"
        response = requests.get(API_ENDPOINT, headers=headers, verify=False)
        mytask=response.json()['value']
        if len(mytask)==0:
            mydata=None
        else:
            API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/import-parameter/"+mytask[0]
            response = requests.get(API_ENDPOINT, headers=headers, verify=False)
            mydata=response.json()['value']
            mydata.pop('result', None)
            mydata.pop('id', None)
                 
        temp={"import":mydata, "export":mydata1}
        infos.append(temp)
        if driveInfo['subDeviceCount']==2:
            drive=driveInfo['drive']
            API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/export-parameter?type=browse"
            response = requests.get(API_ENDPOINT, headers=headers, verify=False)
            mytask=response.json()['value']
            if len(mytask)==0:
                mydata1=None
            else:
                API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/export-parameter/"+mytask[0]
                response = requests.get(API_ENDPOINT, headers=headers, verify=False)
                mydata1=response.json()['value']
                mydata1.pop('id', None)
                print(mydata1)
            API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/import-parameter?type=browse"
            response = requests.get(API_ENDPOINT, headers=headers, verify=False)
            mytask=response.json()['value']
            if len(mytask)==0:
                mydata=None
            else:
                API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/import-parameter/"+mytask[0]
                response = requests.get(API_ENDPOINT, headers=headers, verify=False)
                mydata=response.json()['value']
                mydata.pop('result', None)
                mydata.pop('id', None)
                print(mydata)        
            temp={"import":mydata, "export":mydata1}
            infos.append(temp)
        driveInfo['info']=infos
        newdrivesList.append(driveInfo)

    return  newdrivesList


#Drive Infos 

def buildDrivesInfos(bearer, ip="localhost"):
    drivesList=getDrivesList(bearer,IPADDRESS)
    myDriveinfolist=[]
    mydrivesInfo={}
    for drive in drivesList:
        mydrivesInfo={}
        
        API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive
        headers = {"authorization": "Bearer "+bearer}
        #print(headers)
        response = requests.get(API_ENDPOINT, headers=headers, verify=False)
        mydata=response.json()['value']
        mydrivesInfo['drive']=drive
        mydrivesInfo['subDeviceCount']=mydata['subDeviceCount']
        mydrivesInfo['ip']=mydata['commAddress'][0]
        #print(mydrivesInfo)
        myDriveinfolist.append(mydrivesInfo)
        #print("Status Code", response.status_code)
        #print("JSON Response ", response.json())

    return  myDriveinfolist

def getDrivesList(bearer, ip="localhost"):
    API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives?type=browse"
    headers = {"authorization": "Bearer "+bearer}
    #print(headers)
    response = requests.get(API_ENDPOINT, headers=headers, verify=False)
    #print("Status Code", response.status_code)
    #print("JSON Response ", response.json())
    return  response.json()['value']





##server start

if __name__ == '__main__':
  
    
    if "SNAP_DATA" in os.environ:
        run_simple('unix://'+os.environ['SNAP_DATA']+'/package-run/axis-restore-tool/example.sock', 0, app)
        #app.run(host='0.0.0.0',debug = False, port=3125)
    else:

        app.run(host='0.0.0.0',debug = True, port=3546)

