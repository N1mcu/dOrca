#!/usr/bin/env python3

import json
import sys
import os

def fixPath(path):
      return(os.path.abspath(path))

def main():
      if len(sys.argv) == 1 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print("dOrca usage:     positional argument: mode")
            print("     exec:       To execute commands registered at the inventory file from a container")
            print("     dev:        For develop new images and containers")
            print("     config:     For manage the database")
            sys.exit()
      mode = sys.argv[1]
      if mode == "dev":
            from modules import dev
            dev.dev(configs)
      elif mode == "config":
            from modules import config
            config.config(configs)
      elif mode == "exec":
            from modules import exec
            exec.exec(configs)
            
 
if __name__=="__main__":
      jsonConfigFile = "/etc/dOrca/config.json"
      with open(fixPath(jsonConfigFile),"r") as file:
            configs = json.load(file)
      main()
      