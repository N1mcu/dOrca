import argparse
import subprocess
import os.path
import re
from modules.atlas_db import initDB,dropDockerfile

def getOptions():
      parser = argparse.ArgumentParser(description="dOrca dev module. To create a new container,use -n and the name of the container. Options -b, -p and -v are optional")
      parser.add_argument("mode", type=str, help="Mode")
      parser.add_argument("-b", "--base", type=str, help="Base image for the container: debian, kali. By default alpine will be used")
      parser.add_argument("-n", "--name", type=str, help="Name for the container")
      parser.add_argument("-p", "--publish", type=str, help="Publish a container's port(s) to the host")
      parser.add_argument("-v", "--volume", type=str, help="Bind mount a volume")
      parser.add_argument("-c", "--commit", type=str, help="Convert a container into an image")
      parser.add_argument("-u", "--upload", type=str, help="Upload a given image to Dockerhub")
      parser.add_argument("-l", "--login", action="store_true", help="Login to DockerHub with the config stored credentials")
      parser.add_argument("-r", "--remove", type=str, help="Remove a given container from the system")
      parser.add_argument("-d", "--dockerfile", type=str, help="Give the path to a Dockerfile for image building  (use with --imagename)")
      parser.add_argument("-i", "--imagename", type=str, help="Name for the image builded with Dockerfile (use with --dockerfile)")
      parser.add_argument("-e", "--exec", type=str, nargs='*', help="Execute command at the a given running container")
      parser.add_argument("--update", action="store_true", help="Update image from a Dockerfile storage in the DB")
      parser.add_argument("-s", "--search", type=str, help="Search an image at Dockerhub.")
      parser.add_argument("-o", "--logs", type=str, help="Extract history logs from a running container to create a Dockerfile.")
      options = parser.parse_args()
      return options

def login(conf):
    dockerLogin = "docker login --username %s --password %s" % (conf['username'],conf['password'])
    try:
        subprocess.run(dockerLogin.split(" "))
    except Exception as e:
        print(e)

def commitContainer(name):
    imageAuthor = input('Add author for the image? (no spaces) Enter to skip: ')
    imageTag = input('Add tag/version for the image? Enter to skip (latest): ')
    if imageTag == "":
        imageTag = "latest"
    try:
        commitContainer = 'docker commit -a "%s" %s %s:%s' % (imageAuthor,name,name,imageTag)
        subprocess.run(commitContainer.split(" "))
        print("Image created")
    except Exception as e:
        print(e)

def pushImage(name,imageTag,username):
    try:
        taggingImage = "docker tag %s:%s %s/%s:%s" % (name,imageTag,username,name,imageTag)
        removeLocalImage = "docker image rm %s" % (name)
        pushImage = "docker push %s/%s:%s" % (username,name,imageTag)
        subprocess.run(taggingImage.split(" "))
        subprocess.run(removeLocalImage.split(" "))
        subprocess.run(pushImage.split(" "))
        print("Image pushed to Docker Hub")
    except Exception as e:
        print(e)

def removeContainer(container):
    dockerInspect = "docker inspect -f '{{.State.Running}}' %s" % container
    dockerInspect = dockerInspect.split(" ")
    status = subprocess.check_output(dockerInspect)
    if 'true' in status.decode("utf-8"):
        print("Stopping container")
        containerStop = "docker stop %s" % container
        subprocess.run(containerStop.split(" "))
    dockerRemove =  "docker container rm %s" % container
    try:
        subprocess.run(dockerRemove.split(" "))
        print("Container " + container + " removed")
    except Exception as e:
        print(e)

def execContainer(container,cmd):
    dockerInspect = "docker inspect -f '{{.State.Running}}' %s" % container
    dockerInspect = dockerInspect.split(" ")
    status = subprocess.check_output(dockerInspect)
    if 'false' in status.decode("utf-8"):
        print("Starting container")
        containerStart = "docker start %s" % container
        subprocess.run(containerStart.split(" "))
    dockerExec = "docker container exec -it %s %s" % (container, cmd[0])
    subprocess.run(dockerExec.split(" "))

def buildImage(dockerfile,imagename,tag):
    if os.path.isdir(dockerfile):
        dockerBuild = "docker build %s -t %s:%s" % (dockerfile, imagename,tag)
        subprocess.run(dockerBuild.split(" "))
    else:
        print("Can't read Dockerfile from %s directory") % (dockerfile)

def updateFromDockerfile(configs):
    name = input('Name of the Dockerfile image (ex: impacket): ')
    tempFilePath = input('Path to drop the Dockerfile (the user MUST OWN the directory to work properly): ')
    conn = initDB(configs,configs['atlas']['collection_dockerfile'])
    dropDockerfile(conn,name,tempFilePath)
    tag = input('Tag of the image (ex: latest, 2.11, etc...): ')
    buildImage(tempFilePath,name,tag)
    upload = input('Upload image to Dockerhub (Y/N): ')
    if upload == 'Y':
        pushImage(name,tag,configs['dockerhub']['username'])
    os.remove(tempFilePath)

def searchImages(image):
      try:
            dSearch = "docker search %s" % image
            subprocess.run(dSearch.split(" "))
      except Exception as e:
            print(e)
def logContainer(container):
    try:
        tmpFile = "/tmp/logs_%s" % container
        tmpBase = "/tmp/base_%s" % container
        fTmpFile = open(tmpFile, "w")
        fTmpBase = open(tmpBase, "w")
        lcontainer = "docker logs %s" % (container)
        subprocess.run(lcontainer.split(" "),stdout=fTmpFile)
        lcontainerFrom = "docker container inspect %s" % container
        subprocess.run(lcontainerFrom.split(" "),stdout=fTmpBase)
        with open(tmpBase, "r") as inspect:
            lines = inspect.readlines()
            for line in lines:
                if "Image" in line and "sha" not in line:
                    print("Base image for the container: %s" % line.split('"')[3])
        with open(tmpFile, "r") as log:
            lines = log.readlines()
        with open(tmpFile, "w") as log:
            for line in lines:
                log.write(re.sub(r'[^ .-_#:;@!"$%&/()=\nA-Za-z0-9/]+', '', line))
        print("Container log extrated to %s" % tmpFile)
        print("Please, review and clean it to generate a valid Dockefile")
        fTmpFile.close()
        fTmpBase.close()
        os.remove(tmpBase)
    except Exception as e:
        print(e)

def dev(configs):
    options = getOptions()
    if options.commit:
        commitContainer(options.commit)
        upload = input('Upload image to Dockerhub (Y/N): ')
        if upload == 'Y':
            tag = input('Tag of the image (ex: latest, 2.11, etc...): ')
            pushImage(options.commit,tag,configs['dockerhub']['username'])
    elif options.remove:
        removeContainer(options.remove)
    elif options.upload:
        tag = input('Tag of the image (ex: latest, 2.11, etc...): ')
        pushImage(options.upload,tag,configs['dockerhub']['username'])
    elif options.name:
        if options.exec:
            execContainer(options.name,options.exec)
            exit()
        if options.base:
            image = options.base
        else:
            image = "alpine"
        try:
            dockerPull = "docker pull --platform amd64 %s" % image
            subprocess.run(dockerPull.split(" "))
            print("Image " + image + " installed")
            profile = ""
            if options.volume:
                profile = " -v " + options.volume
            if options.publish:
                profile += " -p " + options.publish
            createContainer = "docker container run --name " + options.name + profile + " -it " + image 
            print("Creating and spawning container " + options.name + " using " + image)
            if len(profile) > 1:
                print("with options: " + options)
            subprocess.run(createContainer.split(" "))
        except Exception as e:
            print(e)
    elif options.login:
        login(configs['dockerhub'])
    elif options.imagename or options.dockerfile:
        if options.dockerfile and options.imagename:
            tag = input('Tag of the image (ex: latest, 2.11, etc...): ')
            buildImage(options.dockerfile,options.imagename,tag)
            upload = input('Upload image to Dockerhub (Y/N): ')
            if upload == 'Y':
                pushImage(options.imagename,tag,configs['dockerhub']['username'])
        else:
            print("-d/--dockerfile [Path_Containing_The_Dockerfile] and -i/--image [Name_of_new_image] needed")
    elif options.update:
        updateFromDockerfile(configs)
    elif options.search:
        searchImages(options.search)
    elif options.logs:
        logContainer(options.logs)
        