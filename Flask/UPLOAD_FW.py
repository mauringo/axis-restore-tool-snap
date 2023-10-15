
import json 
import time
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
__name__ = "__main__"

#TARGET to be modified
IPADDRESS='192.168.15.1'
if 'SNAP' in os.environ:
    IPADDRESS='localhost'



########CODE :)
def main():


    TOKEN=auth(ip=IPADDRESS)
    FilesList=getFilesList(TOKEN,IPADDRESS)
    #deleteFile(TOKEN,FilesList[0],IPADDRESS)
    drivesList=buildDrivesInfos(TOKEN,IPADDRESS)
    print(checkStatus(TOKEN,drivesList,IPADDRESS))
    #bakupOneDrive(TOKEN,drivesList[0],IPADDRESS)
    #restoreOneDrive(TOKEN,drivesList[0],IPADDRESS)
    print(drivesList)



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
            mydata1={"state":"empty"}
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
            mydata={"state":"empty"}
        else:
            API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/import-parameter/"+mytask[0]
            response = requests.get(API_ENDPOINT, headers=headers, verify=False)
            mydata=response.json()['value']
            mydata.pop('result', None)
            mydata.pop('id', None)
            print(mydata)        
        temp={"import":mydata, "export":mydata1}
        infos.append(temp)
        if driveInfo['subDeviceCount']==2:
            drive=driveInfo['drive']
            API_ENDPOINT = "https://"+ip+"/automation/api/v2/nodes/devices/drives/"+drive+"/subdevices/subdevice-0/export-parameter?type=browse"
            response = requests.get(API_ENDPOINT, headers=headers, verify=False)
            mytask=response.json()['value']
            if len(mytask)==0:
                mydata1={"state":"empty"}
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
                mydata={"state":"empty"}
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




if __name__ == "__main__":
    main()