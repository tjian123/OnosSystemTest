#!/usr/bin/env python
"""
Modified 2016 by ON.Lab

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>
"""

import json
import os
import re
import subprocess
from docker import Client
from docker import errors
from drivers.common.apidriver import API

class DockerApiDriver( API ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        super( API, self ).__init__()

    def connect( self, **connectargs ):
        """
        Create Client handle to connnect to Docker server
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
            for key in self.options:
                if key == "home":
                    self.home = self.options[ 'home' ]
                    break
            if self.home is None or self.home == "":
                self.home = "/var/tmp"

            self.handle = super( DockerApiDriver, self ).connect()
            self.dockerClient = Client(base_url='unix://var/run/docker.sock')
            return self.handle
        except Exception as e:
            main.log.exception( e )

    def getListOfImages( self, repo="onosproject/onos" ):
        """
        Get the list of image tags
        """
        try:
            imageList = list( self.dockerClient.images( name=repo ) )
            imageListToSend = []
            duplicateTagDetected = 0
            for imageDict in imageList:
                if imageDict[ 'RepoTags' ] is not None:
                    if len( imageDict[ 'RepoTags' ] ) > 1:
                        duplicateTagDetected = 1
                    imageListToSend.append( imageDict['RepoTags'][0].encode('UTF8').split(':')[1] )
            return imageListToSend, duplicateTagDetected
        except Exception as e:
            main.log.exception( e )

    def dockerPull( self, onosRepo ="onosproject/onos", onosTag="latest" ):
        """
        Pulls Docker image from repository
        """
        try:
            main.log.info( self.name +
                           ": Pulling Docker image " + onosRepo + ":"+ onosTag )
            for line in self.dockerClient.pull( repository = onosRepo, \
                    tag = onosTag, stream = True ):
                    print "#",
            main.log.info(json.dumps(json.loads(line), indent =4))

            #response = json.dumps( json.load( pullResult ), indent=4 )
            if re.search( "for onosproject/onos:" + onosTag, line ):
                main.log.info( "onos docker image pulled is: " + line )
                return main.TRUE
            else:
                main.log.error( "Failed to download image from: " + onosRepo +":"+ onosTag )
                main.log.error( "Error respone: " )
                main.log.error( line )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerCreateCT( self, onosImage="onosproject/onos:latest", onosNode="onos1" ):
        """
            Create a Docker container with a specific image
        """
        try:
            main.log.info( self.name +
                           ": Creating Docker container for node: " + onosNode )
            response = self.dockerClient.create_container( image=onosImage, \
                    tty=True, name=onosNode, detach=True )
            #print response
            #print response.get("Id")
            #print response.get("Warnings")
            if( str( response.get("Warnings") ) == 'None' ):
                main.log.info( "Created container for node: " + onosNode + "; container id is: " + response.get("Id") )
                return ( main.TRUE, response.get("Id") )
            else:
                main.log.info( "Noticed warnings during create" )
                return ( main.FALSE, null)
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerStartCT( self, ctID ):
        """
            Start Docker container
        """
        try:
            main.log.info( self.name +
                           ": Starting Docker conatiner Id " + ctID )
            response = self.dockerClient.start( container = ctID )
            if response is None:
                main.log.info( "Started container for Id: " + ctID )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during start" )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerStopCT( self, ctName ):
        """
            Stop docker container
        """
        try:
            main.log.info( self.name +
                           ": Stopping Docker conatiner for node " + ctName )
            response = self.dockerClient.stop( ctName )
            if response is None:
                main.log.info( "Stopped container for node: " + ctName )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during stop" )
                return main.FALSE
        except errors.NotFound:
            main.log.info( ctName + " not found! Continue on tests...")
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            #main.cleanup()
            #main.exit()

    def dockerRestartCT( self, ctName ):
        """
            Restart Docker container
        """
        try:
            main.log.info( self.name +
                           ": Restarting Docker conatiner for node " + ctName )
            response = self.dockerClient.restart( ctName )
            if response is None:
                main.log.info( "Restarted container for node: " + ctName )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during Restart" )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerCheckCTName( self, ctName):
        """
            Check Docker conatiner status
        """
        try:
            main.log.info( self.name +
                           ": Checking Docker Status for CT with 'Names'  " + ctName )
            namelist = [response["Names"] for response in self.dockerClient.containers(all=True) if not []]
            main.log.info("Name list is: " + str(namelist) )
            if( [ctName] in namelist):
                main.log.info( "Container " + ctName + " exists" )
                return main.TRUE
            else:
                main.log.info( "Container " + ctName + " does not exist" )
                return main.FALSE
        except errors.NotFound:
            main.log.warn( ctName + "not found! Continue with the tests...")
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception! Continue tests..." )
            #main.cleanup()
            #main.exit()

    def dockerRemoveCT( self, ctName ):
        """
            Remove Docker conatiner
        """
        try:
            main.log.info( self.name +
                           ": Removing Docker container for node " + ctName )
            response = self.dockerClient.remove_container( ctName, force=True )
            if response is None:
                main.log.info( "Removed container for node: " + ctName )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during Remove " + ctName)
                return main.FALSE
            main.log.exception(self.name + ": not found, continuing...")
        except errors.NotFound:
            main.log.warn( ctName + "not found! Continue with the tests...")
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception! Continuing..." )
            #main.cleanup()
            #main.exit()

    def dockerRemoveImage( self, imageRepoTag=None ):
        """
            Remove Docker image
        """
        rmResult = main.TRUE
        if self.dockerClient.images() is []:
            main.log.info( "No docker image found" )
            return rmResult
        else:
            imageList = [ image["Id"] for image in self.dockerClient.images()
                                        if image["RepoTags"] is None
                                           or imageRepoTag in image["RepoTags"] ]
            for id in imageList:
                try:
                    main.log.info( self.name + ": Removing Docker image " + id )
                    response = self.dockerClient.remove_image(id, force = True)
                    if response is None:
                        main.log.info( "Removed Docker image: " + id )
                        rmResult = rmResult and main.TRUE
                    else:
                        main.log.info( "Noticed warnings during Remove " + id )
                        rmResult = rmResult and main.FALSE
                except errors.NotFound:
                    main.log.warn( image + "not found! Continue with the tests...")
                    rmResult = rmResult and main.TRUE
                except Exception:
                    main.log.exception( self.name + ": Uncaught exception! Continuing..." )
                    rmResult = rmResult and main.FALSE
                    #main.cleanup()
                    #main.exit()
        return rmResult

    def fetchLatestClusterFile( self, branch="master" ):
        """
            Fetch onos-form-cluster file from a particular branch
        """
        try:
            command = "wget -N https://raw.githubusercontent.com/opennetworkinglab/\
                    onos/" + branch + "/tools/package/bin/onos-form-cluster"
            subprocess.call( command ) # output checks are missing for now
            command = "chmod u+x " + "onos-form-cluster"
            subprocess.call( command )
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosFormCluster( self, onosIPs, cmdPath, user="karaf", passwd="karaf" ):
        """
            From ONOS cluster for IP addresses in onosIPs list
        """
        try:
            onosIPs = " ".join(onosIPs)
            command = "{}/onos-form-cluster -u {} -p {} {}".format( cmdPath,
                                                                    user,
                                                                    passwd,
                                                                    onosIPs )
            result = subprocess.call( command, shell=True )
            if result == 0:
                return main.TRUE
            else:
                main.log.info("Something is not right in forming cluster>")
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerIP( self, ctName ):
        """
            Fetch IP address assigned to specified node/container
        """
        try:
            output = self.dockerClient.inspect_container( ctName )
            nodeIP = output['NetworkSettings']['IPAddress']
            main.log.info( " Docker IP " + str(nodeIP) )
            return str(nodeIP)

        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

