import argparse

def getOptions():
    parser = argparse.ArgumentParser(description="dOrca inventory module")
    parser.add_argument("mode", type=str, help="Mode")
    parser.add_argument("-a", "--add", action="store_true", help="Add an entry to the inventory database")
    parser.add_argument("-f", "--file", type=str, help="Load a file into the inventory database")
    parser.add_argument("-s", "--search", action="store_true", help="Search data in the inventory database")
    parser.add_argument("-r", "--remove", action="store_true", help="Remove an entry from the inventory database")
    parser.add_argument("-u", "--update", action="store_true", help="Update an entry from the inventory database")
    parser.add_argument("-d", "--dump", action="store_true", help="Dump all the data from the inventory database")
    parser.add_argument("-p", "--purge", action="store_true", help="Setup/purge the inventory database")
    parser.add_argument("-e", "--export", action="store_true", help="Export the database to a CSV file")
    parser.add_argument("-c", "--collection", action="store_true", help="Use Dockerfile database collection")
    options = parser.parse_args()
    return options

def config(config):
    if config['general']['database_file'] == "atlas":
        from modules.atlas_db import initDB,addData, addFromFile, searchData, removeData, updateData, dumpData, purgeData, exportData, addDockerfile, dropDockerfile, dumpDockerfile, delDockerfile
    else:
        from modules.local_db import initDB,addData, addFromFile, searchData, removeData, updateData, dumpData, purgeData, exportData
    options = getOptions()
    if options.collection:
        col = config['atlas']['collection_dockerfile']
    else:
        col = config['atlas']['collection_cmd']
    conn = initDB(config,col)
    if options.add:
        if options.collection:
            addDockerfile(conn)
        else:
            addData(conn)
    elif options.file:
        addFromFile(conn,options.file)
    elif options.search:
        searchData(conn)
    elif options.remove:
        if options.collection:
            delDockerfile(conn)
        else:
            removeData(conn)
    elif options.update:
        updateData(conn)
    elif options.dump:
        if options.collection:
            dumpDockerfile(conn)
        else:
            dumpData(conn)
    elif options.purge:
        purgeData(conn,config['general']['database_file'])
    elif options.export:
        if options.collection:
            name = input('Name of the Dockerfile image (ex: impacket): ')
            tempFilePath = input('Path to drop the Dockerfile: ')
            dropDockerfile(conn,name,tempFilePath)
        else:
            exportData(conn)