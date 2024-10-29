# dOrca
Python script to manage Docker in the execution of tools used in pentesting and Red Teaming

Modules:
- Dev: Develop new tools in images/containers
- Config: Manage the tool databases
- Exec: Execute commands registered at the inventory file from a container

Instalation:

First is needed to create a free account/database in https://www.mongodb.com/products/platform/atlas-database
After the database creation, two collections are needed:
One for the commands with this format:
{"_id":
      {"$oid":"652e...0e38f"},  -> Atlas internal ID
      "cmd":"GetNPUsers.py",    -> Command to execute inside the docker image
      "image":"n1mcu/impacket", -> Name of the docker image where the command lives
      "tags":"interna",         -> Tag to identify the purpose of the tool (currently not in use)
      "entrypoint":"",          -> Path of the tool inside the Docker image. If the location is in the PATH, it can be set to blank
      "profile":"normal",       -> Profile (set of docker run options) to use with the command. The profiles can be configured in the config.json file
      "version":"latest"        -> Tag of the Docker image
}

And the other one for the Dockerfiles used to update the tools:
{"_id":
      {"$oid":"666...3c8c"}, -> Atlas internal ID
      "name":"impacket",     -> Name of the image
      "file":{"$binary":     -> Dockerfile content in Base64
            {"base64":"UmxKUFRTQXR...mRDZz09","subType":"00"}
      }
}

Next, copy files to desire location. dOrca.py and module folder must be on the same directory.
Create the folder where the initial config file will be (/etc/dOrca/) and copy config_example.json.
Fill the config file (config_example.json) with the credentials for Atlas and Dockerhub, update the working directory and set up the profiles.
After that, edit dOrca.py to update the new config file location if needed.

Two modules need to be instaled:
- python3-pymongo
- python3-certifi

The dOrca_proxy.sh script use the tool tun2proxy (https://github.com/xjasonlyu/tun2socks) to route an specific network subnet to a previously established proxy socks through a tun0 interface.
In that way, using docker --network=host option, the command run from the docker image can reach the desire target without the use of proxychains.
