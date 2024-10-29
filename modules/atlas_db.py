from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
import json
import os
import base64

def addFromFile(conn,file):
    try:
        f = open(file)
        data = json.load(f)
        x = conn.insert_many(data)
        print(x.inserted_ids)
        f.close()
    except Exception as e:
        print(e)

def addData(conn):
    cmd = input('Name of the command to register (ex: msfvenom): ')
    image = input('Name of the image containing the command: ')
    tags = input('Tags for the image (ex: web, externa, interna, etc...): ')
    entrypoint = input('Entrypoint of the container (ex: /usr/bin/): ')
    profile = input('Docker run profile name (ex: normal, C2, neo4j): ')
    version = input('Tag of the image containing the command (ex: latest, 2.11, etc...): ')
    newc = {
        "cmd": cmd,
        "image": image,
        "tags": tags,
        "entrypoint": entrypoint,
        "profile": profile,
        "version": version
    }
    try:
        x = conn.insert_one(newc)
        print(x.inserted_id, " document added.")
    except Exception as e:
        print(e)

def searchData(conn):
    field = input('Field to search for? ')
    value = input('Value of the field? ')
    try:
        myquery = {
            field:value
         }
        x = conn.find(myquery)
        for r in x:
            print("----------")
            print("Command: %s" % r['cmd'])
            print("Image: %s" % r['image'])
            print("Tags: %s" % r['tags'])
            print("Entrypoint: %s" % r['entrypoint'])
            print("Profile: %s" % r['profile'])
            print("Version: %s" % r['version'])
    except Exception as e:
        print(e)

def removeData(conn):
    field = input('Field to search and delete for? ')
    value = input('Value of the field? ')
    try:
        myquery = {
            field:value
         }
        x = conn.delete_one(myquery)
        print(x.deleted_count, " documents deleted.")
    except Exception as e:
        print(e)

def updateData(conn):
    cmd = input('Name of the command to update (ex: msfvenom): ')
    field = input('Field to update? ')
    value = input('New value? ')
    try:
        myquery = { "cmd": cmd }
        newvalues = { "$set": { field: value } }
        conn.update_one(myquery, newvalues)
        print("\nData updated")
    except Exception as e:
        print(e)

def dumpData(conn):
    try:
        x = conn.find()
        for r in x:
            print("----------")
            print("Command: %s" % r['cmd'])
            print("Image: %s" % r['image'])
            print("Tags: %s" % r['tags'])
            print("Entrypoint: %s" % r['entrypoint'])
            print("Profile: %s" % r['profile'])
            print("Version: %s" % r['version'])
    except Exception as e:
        print(e)

def purgeData(conn,db):
    try:
        myquery = { "cmd": {"$regex": ".*"} }
        x = conn.delete_many(myquery)
        print(x.deleted_count, " documents deleted.") 
    except Exception as e:
        print(e)

def exportData(conn):
    try:
        from datetime import date
        today = date.today()
        d1 = today.strftime("%d%m%Y")
        jsonFileName = "Inventory_" + d1 + ".json"
        x = conn.find({},{ "_id": 0 })
        with open(jsonFileName, "a+") as write_file:
            for r in x:
                json.dump(r, write_file,indent=1)
    except Exception as e:
        print(e)

def addDockerfile(conn):
    name = input('Name of the Dockerfile image (ex: impacket): ')
    pathToFile = input('Path to the Dockerfile archive: ')
    if os.path.isfile(pathToFile):
        dFile = open(pathToFile,'rb')
        dContent = dFile.read()
        dContentB64 = base64.b64encode(dContent)
        dFile.close()
    else:
        print("Can't read Dockerfile %s") % (pathToFile)
    newc = {
        "name": name,
        "file": dContentB64
    }
    try:
        x = conn.insert_one(newc)
        print(x.inserted_id, " document added.")
    except Exception as e:
        print(e)
def dropDockerfile(conn,name,tempFilePath):
    try:
        myquery = {
            "name":name
         }
        x = conn.find(myquery)
        for r in x:
            b64Blob = r['file']
    except Exception as e:
        print(e)
    if os.path.isdir(tempFilePath):
        blob = base64.b64decode(b64Blob)
        tempFile = open(tempFilePath + 'Dockerfile','wb')
        tempFile.write(blob)
        tempFile.close()
    else:
        print("Error while accesing to %s") % (tempFilePath)

def delDockerfile(conn):
    value = input('Name of the Dockerfile to delete? ')
    try:
        myquery = {
            "name":value
         }
        x = conn.delete_one(myquery)
        print(x.deleted_count, " documents deleted.")
    except Exception as e:
        print(e)

def dumpDockerfile(conn):
    try:
        x = conn.find()
        for r in x:
            print("----------")
            print("Name: %s" % r['name'])
            print("File: %s" % r['file'])
    except Exception as e:
        print(e)

def initDB(config,col):
    uri = "mongodb+srv://%s:%s@%s/?retryWrites=true&w=majority" % (config['atlas']['username'],config['atlas']['password'],config['atlas']['server'])
    try:
        client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
        db_name = config['atlas']['database']
        col_name = col
        db = client[db_name]
        conn = db[col_name]
        return conn
    except Exception as e:
        print(e)

def searchExec(conn,cmd):
    try:
        exeArray = []
        myquery = {
            "cmd":cmd
         }
        x = conn.find(myquery)
        exeArray.append(x[0]['cmd'])
        exeArray.append(x[0]['image'])
        exeArray.append(x[0]['tags'])
        exeArray.append(x[0]['entrypoint'])
        exeArray.append(x[0]['profile'])
        exeArray.append(x[0]['version'])
        return exeArray
    except Exception as e:
        print(e)
        