import csv
import sqlite3
import subprocess

def addFromFile(conn,file):
    try:
        with open(file,'r') as fin:
            # csv.DictReader uses first line in file for column headings by default
            dr = csv.DictReader(fin) # comma is default delimiter
            to_db = [(i['CMD'], i['IMAGE'], i['TAGS'], i['ENTRYPOINT'], i['PROFILE']) for i in dr]
        conn.executemany("INSERT INTO INVENTORY (CMD,IMAGE,TAGS,ENTRYPOINT,PROFILE) VALUES (?, ?, ?, ?, ?);", to_db)
        conn.commit()
        print("Total number of rows added : %i" % conn.total_changes)
        conn.close()
    except Exception as e:
        print(e)

def addData(conn):
    cmd = input('Name of the command to register (ex: msfvenom): ')
    image = input('Name of the image containing the command: ')
    tags = input('Tags for the image (ex: web, externa, interna, etc...): ')
    entrypoint = input('Entrypoint of the container (ex: /usr/bin/): ')
    profile = input('Docker run profile name (ex: normal, C2, neo4j): ')
    try:
        conn.execute("INSERT INTO INVENTORY (CMD,IMAGE,TAGS,ENTRYPOINT,PROFILE) \
            VALUES (?, ?, ?, ?, ? )", (cmd, image, tags, entrypoint, profile))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)

def searchData(conn):
    field = input('Field to search for? ')
    value = input('Value of the field? ')
    try:
        cursor = conn.execute('SELECT * FROM INVENTORY WHERE ' + field + ' LIKE "%' + value + '%"')
        print("Search results:\n")
        for row in cursor:
            print("Command: %s" % row[0])
            print("Image: %s" % row[1])
            print("Tags: %s" % row[2])
            print("Entrypoint: %s" % row[3])
            print("Profile: %s" % row[4])
            print("----------")
        conn.close()
    except Exception as e:
        print(e)

def searchExec(conn,cmd):
    try:
        exeArray = []
        cursor = conn.execute('SELECT * FROM INVENTORY WHERE CMD = "' + cmd + '"').fetchall()
        conn.close()
        exeArray.append(cursor[0][0])
        exeArray.append(cursor[0][1])
        exeArray.append(cursor[0][2])
        exeArray.append(cursor[0][3])
        exeArray.append(cursor[0][4])
        return exeArray
    except Exception as e:
        print(e)

def removeData(conn):
    field = input('Field to search and delete for? ')
    value = input('Value of the field? ')
    try:
        conn.execute("DELETE from INVENTORY WHERE " + field + " = '"+ value + "'")
        conn.commit()
        print("Total number of rows deleted : %i" % conn.total_changes)
        conn.close()
    except Exception as e:
        print(e)

def updateData(conn):
    cmd = input('Name of the command to update (ex: msfvenom): ')
    field = input('Field to update? ')
    value = input('New value? ')
    try:
        conn.execute('UPDATE INVENTORY SET ' + field + ' = ? WHERE cmd = ?', (value, cmd))
        conn.commit()
        print("Total number of rows updated: %i" % conn.total_changes)
        conn.close()
    except Exception as e:
        print(e)

def dumpData(conn):
    try:
        cursor = conn.execute("SELECT * FROM INVENTORY")
        for row in cursor:
            print("Command: %s" % row[0])
            print("Image: %s" % row[1])
            print("Tags: %s" % row[2])
            print("Entrypoint: %s" %row[3])
            print("Profile: %s" % row[4])
            print("----------")
        conn.close()
    except Exception as e:
        print(e)

def purgeData(conn,db):
    try:
        removeDB = "rm %s" % db
        subprocess.run(removeDB.split(" "))
        conn = sqlite3.connect(db)
        conn.execute('''CREATE TABLE INVENTORY
             (CMD    TEXT    PRIMARY KEY NOT NULL,
             IMAGE  TEXT   NOT NULL,
             TAGS   TEXT,
             ENTRYPOINT TEXT NOT NULL,
             PROFILE TEXT   NOT NULL);''')
        conn.close()
    except Exception as e:
        print(e)

def exportData(conn):
    from datetime import date
    today = date.today()
    d1 = today.strftime("%d%m%Y")
    csvFileName = "Inventory_" + d1 + ".csv"
    try:
        cursor = conn.execute("SELECT * FROM INVENTORY")
        csvFile = open(csvFileName,'a+')
        csvFile.write("CMD,IMAGE,TAGS,ENTRYPOINT,PROFILE\n")
        for row in cursor:
            csvFile.write(row[0] + "," + row[1]+ "," + row[2] + "," + row[3] + "," + row[4] + "\n")
        csvFile.close()
        print("CSV file %s created" % csvFileName)
        conn.close()
    except Exception as e:
        print(e)

def initDB(config):
    conn = sqlite3.connect(config['general']['database_file'])
    return conn