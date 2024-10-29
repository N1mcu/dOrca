import argparse
import subprocess
from dOrca import fixPath

def getOptions():
      parser = argparse.ArgumentParser(description="dOrca exec module")
      parser.add_argument("mode", type=str, help="Mode")
      parser.add_argument("-a", "--append", type=str, help="Append directory to working_base_dir config")
      parser.add_argument("-v", "--verbose", action="store_true", help="Instead of executing the command, prints out the docker commando to the console")
      parser.add_argument("-p", "--proxy", action="store_true", help="After running dOrca_proxy.sh, use tun99 as proxy")
      parser.add_argument("-w", "--workingdir", type=str, help="Working directory inside the container")
      parser.add_argument("cmd", type=str, nargs='*', help="Command to execute")
      options = parser.parse_args()
      return options

def exec(configs):
    options = getOptions()
    try:
        if configs['general']['database_file'] == "atlas":
            from modules.atlas_db import initDB,searchExec
            conn = initDB(configs,configs['atlas']['collection_cmd'])
        else:
            from modules.local_db import initDB,searchExec
            conn = initDB(configs)
        if options.append:
            workDir = fixPath(configs['general']['working_base_dir'] + options.append)
        else:
            workDir = fixPath(configs['general']['working_base_dir'])
        # Seting up the registered profiles with the working directory
        profiles = configs['profiles']
        for profileName in profiles:
            profiles[profileName] = profiles[profileName].replace("WORKINGDIR",workDir)
        # Looking for the image that contains the command to run
        cmd = options.cmd[0].split(" ",1)[0]
        cursor = searchExec(conn,cmd)
        profile = profiles[cursor[4]]
        # Checking if we need to use proxy (--network=host)
        if options.proxy:
            profile = profile + "--network=host "
        if options.workingdir:
            profile = profile + "-w " + options.workingdir + " "
        # Preparing and executing the command in the container
        # Checking if the executable is configured as entrypoint in the picture
        if cursor[3] == 'na':
            dCmd = "docker run" + profile + cursor[1] + ':' + cursor[5] + ' ' + options.cmd[0].split(" ",1)[1:][0]
        else:
            dCmd = "docker run" + profile + cursor[1] + ':' + cursor[5] + ' ' + cursor[3] + options.cmd[0]
        # In verbose mode only show the docker command to execute
        if options.verbose:
            print(dCmd)
        else:
            subprocess.run(dCmd.split(" "))
    except Exception as e:
        print(e)
