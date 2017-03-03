"""
This file contains intent class for CHOTestMonkey
Author: you@onlab.us
"""
from threading import Lock

class Controller:
    def __init__( self, index ):
        self.default = ''
        self.index = index
        self.ip = main.ONOSip[ index - 1 ]
        self.CLI = None
        self.CLILock = Lock()
        self.status = 'up'

    def setCLI( self, CLI ):
        self.CLI = CLI

    def startCLI( self ):
        return self.CLI.startOnosCli( self.ip )

    def isUp( self ):
        return self.status == 'up'

    def bringDown( self ):
        self.status = 'down'

    def bringUp( self ):
        self.status = 'up'

class Intent:
    def __init__( self, id ):
        self.default = ''
        self.type = 'INTENT'
        self.id = id
        self.expectedState = 'UNKNOWN'

    def isHostIntent( self ):
        return self.type == 'INTENT_HOST'

    def isPointIntent( self ):
        return self.type == 'INTENT_POINT'

    def isFailed( self ):
        return self.expectedState == 'FAILED'

    def isInstalled( self ):
        return self.expectedState == 'INSTALLED'

class HostIntent( Intent ):
    def __init__( self, id, hostA, hostB ):
        Intent.__init__( self, id )
        self.type = 'INTENT_HOST'
        self.hostA = hostA
        self.hostB = hostB
        self.deviceA = hostA.device
        self.deviceB = hostB.device

    def setWithdrawn( self ):
        self.expectedState = 'WITHDRAWN'
        if self.hostB in self.hostA.correspondents:
            self.hostA.correspondents.remove( self.hostB )
        if self.hostA in self.hostB.correspondents:
            self.hostB.correspondents.remove( self.hostA )

    def setFailed( self ):
        self.expectedState = 'FAILED'

    def setInstalled( self ):
        if self.expectedState == 'UNKNOWN':
            self.hostA.correspondents.append( self.hostB )
            self.hostB.correspondents.append( self.hostA )
        self.expectedState = 'INSTALLED'

    def __str__( self ):
        return "ID: " + self.id

class PointIntent( Intent ):
    def __init__( self, id, deviceA, deviceB ):
        Intent.__init__( self, id )
        self.type = 'INTENT_POINT'
        self.deviceA = deviceA
        self.deviceB = deviceB

    def setWithdrawn( self ):
        self.expectedState = 'WITHDRAWN'
        for hostA in self.deviceA.hosts:
            for hostB in self.deviceB.hosts:
                if hostB in hostA.correspondents:
                    hostA.correspondents.remove( hostB )

    def setFailed( self ):
        self.expectedState = 'FAILED'

    def setInstalled( self ):
        if self.expectedState == 'UNKNOWN':
            for hostA in self.deviceA.hosts:
                for hostB in self.deviceB.hosts:
                    hostA.correspondents.append( hostB )
        self.expectedState = 'INSTALLED'

    def __str__( self ):
        return "ID: " + self.id
