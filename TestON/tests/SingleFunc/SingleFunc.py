
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import json

time.sleep( 1 )

class SingleFunc:

    def __init__( self ):
        self.default = ''

    def CASE10( self, main ):
        import time
        import os
        """
        Startup sequence:
        cell <name>
        onos-verify-cell
        onos-remove-raft-log
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        """
        global init
        try:
            if type(init) is not bool:
                init = False
        except NameError:
            init = False
        #Local variables
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        apps = main.params[ 'ENV' ][ 'cellApps' ]
        main.ONOS1ip = main.params[ 'CTRL' ][ 'ip1' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.ONOS1port = main.params[ 'CTRL' ][ 'port1' ]
        benchIp = main.params[ 'BENCH' ][ 'ip1' ]
        benchUser = main.params[ 'BENCH' ][ 'user' ]
        main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
        main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
        main.numCtrls = main.params[ 'CTRL' ][ 'num' ]
        topology = main.params[ 'MININET' ][ 'topo' ]
        maxNodes = int( main.params[ 'availableNodes' ] )
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        main.case( "Setting up test environment" )
        main.CLIs = []
        for i in range( 1, int( main.numCtrls ) + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            init = True
            global nodeCount             #number of nodes running
            global ONOSIp                   #list of ONOS IP addresses
            global scale

            ONOSIp = [ ]
            scale = ( main.params[ 'SCALE' ] ).split( "," )
            nodeCount = int( scale[ 0 ] )

            if PULLCODE:
                main.step( "Git checkout and pull " + gitBranch )
                main.ONOSbench.gitCheckout( gitBranch )
                gitPullResult = main.ONOSbench.gitPull()
                if gitPullResult == main.ERROR:
                    main.log.error( "Error pulling git branch" )
                main.step( "Using mvn clean & install" )
                cleanInstallResult = main.ONOSbench.cleanInstall()
                stepResult = cleanInstallResult
                utilities.assert_equals( expect=main.TRUE,
                                         actual=stepResult,
                                         onpass="Successfully compiled " +
                                                "latest ONOS",
                                         onfail="Failed to compile " +
                                                "latest ONOS" )
            else:
                main.log.warn( "Did not pull new code so skipping mvn " +
                               "clean install" )
            # Populate ONOSIp with ips from params
            for i in range( 1, maxNodes + 1):
                ONOSIp.append( main.params[ 'CTRL' ][ 'ip' + str( i ) ] )

        nodeCount = int( scale[ 0 ] )
        scale.remove( scale[ 0 ] )
        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )
        for i in range( maxNodes ):
            main.ONOSbench.onosDie( ONOSIp[ i ] )
        """
        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )
        """
        """main.step( "Removing raft logs" )
        removeRaftResult = main.ONOSbench.onosRemoveRaftLogs()
        stepResult = removeRaftResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully removed raft logs",
                                 onfail="Failed to remove raft logs" )
        """
        print "NODE COUNT = ", nodeCount
        main.log.info( "Creating cell file" )
        cellIp = []
        for i in range( nodeCount ):
            cellIp.append( str( ONOSIp[ i ] ) )
        print cellIp
        main.ONOSbench.createCellFile( benchIp, cellName, "",
                                       str( apps ), *cellIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        stepResult = packageResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )

        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.TRUE
        for i in range( nodeCount):
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=ONOSIp[ i ] )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )
        time.sleep( 5 )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for i in range( nodeCount):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=ONOSIp[ i ] )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        time.sleep( 5 )
        main.step( "Starting ONOS service" )
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.TRUE
        for i in range( nodeCount ):
            onosIsUp = onosIsUp and main.ONOSbench.isup( ONOSIp[ i ] )
        if onosIsUp == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up, stop and " +
                             "start ONOS again " )
            for i in range( nodeCount ):
                stopResult = stopResult and \
                        main.ONOSbench.onosStop( ONOSIp[ i ] )
            for i in range( nodeCount ):
                startResult = startResult and \
                        main.ONOSbench.onosStart( ONOSIp[ i ] )
        stepResult = onosIsUp and stopResult and startResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )
        
        main.step( "Start ONOS cli" )
        cliResult = main.TRUE
        for i in range( nodeCount ):
            cliResult = cliResult and main.CLIs[i].startOnosCli( ONOSIp[ i ] )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

    def CASE11( self, main ):
        """
            Assign mastership to controllers
        """
        import re
        main.log.report( "Assigning switches to controllers" )
        main.log.case( "Assigning swithes to controllers" )

        main.step( "Starting Mininet Topology" )
        topoResult = main.Mininet1.startNet( topoFile=topology )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

        main.step( "Assigning switches to controllers" )
        assignResult = main.TRUE
        for i in range( 1, ( main.numSwitch + 1 ) ):
            main.Mininet1.assignSwController( sw=str( i ),
                                              count=1,
                                              ip1=main.ONOS1ip,
                                              port1=main.ONOS1port )
        for i in range( 1, ( main.numSwitch + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOS1ip, response ):
                assignResult = assignResult and main.TRUE
            else:
                assignResult = main.FALSE
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switches" +
                                        "to controller",
                                 onfail="Failed to assign switches to " +
                                        "controller" )


    def CASE1001( self, main ):
        """
            Add host intents between 2 host:
                - Discover hosts
                - Add host intents
                - Check intents
                - Check flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Ping hosts
                    - Link up
                    - Ping hosts
                - Remove intents
        """
        import time
        import json
        import re
        """
            Create your item(s) here
            item = { 'name': '', 'host1':
                     { 'name': '', 'MAC': '00:00:00:00:00:0X',
                       'id':'00:00:00:00:00:0X/-X' } , 'host2':
                     { 'name': '', 'MAC': '00:00:00:00:00:0X',
                       'id':'00:00:00:00:00:0X/-X'}, 'link': { 'switch1': '',
                       'switch2': '', 'num':'' } }
        """
        # Local variables
        items = []
        ipv4 = { 'name': 'IPV4', 'host1':
                 { 'name': 'h1', 'MAC': '00:00:00:00:00:01',
                   'id':'00:00:00:00:00:01/-1' } , 'host2':
                 { 'name': 'h9', 'MAC': '00:00:00:00:00:09',
                   'id':'00:00:00:00:00:01/-1'}, 'link': { 'switch1': 's5',
                   'switch2': 's2', 'num':'18' } }
        dualStack1 = { 'name': 'DUALSTACK1', 'host1':
                 { 'name': 'h3', 'MAC': '00:00:00:00:00:03',
                   'id':'00:00:00:00:00:03/-1' } , 'host2':
                 { 'name': 'h11', 'MAC': '00:00:00:00:00:0B',
                   'id':'00:00:00:00:00:0B/-1'}, 'link': { 'switch1': 's5',
                   'switch2': 's2', 'num':'18' } }
        items.append( ipv4 )
        items.append( dualStack1 )
        # Global variables
        
        main.log.case( "Add host intents between 2 host" )
        
        for item in items:
            stepResult = main.TRUE
            h1Name = item[ 'host1' ][ 'name' ]
            h2Name = item[ 'host2' ][ 'name' ]
            h1Mac = item[ 'host1' ][ 'MAC' ]
            h2Mac = item[ 'host2' ][ 'MAC' ]
            h1Id = item[ 'host1' ][ 'id']
            h2Id = item[ 'host2' ][ 'id']
            # Link down/up for rerouting
            sw1 = item[ 'link' ][ 'switch1' ]
            sw2 = item[ 'link' ][ 'switch2' ]
            remLink = item[ 'link' ][ 'num' ]
            intentsId = []
            main.step( item[ 'name' ] + ": Add host intents between " + h1Name
                        + " and " + h2Name )
            main.log.info( item[ 'name' ] + ": Discover host using arping" )
            main.Mininet1.arping( host=h1Name )
            main.Mininet1.arping( host=h2Name )
            host1 = main.ONOScli1.getHost( mac=h1Mac )
            host2 = main.ONOScli1.getHost( mac=h2Mac )
            print host1
            print host2
            # Adding intents
            main.log.info( item[ 'name' ] + ": Adding host intents" )
            intent1 = main.ONOScli1.addHostIntent( hostIdOne=h1Id,
                                                   hostIdTwo=h2Id )
            intentsId.append( intent1 )
            time.sleep( 5 )
            intent2 = main.ONOScli1.addHostIntent( hostIdOne=h2Id,
                                                   hostIdTwo=h1Id )
            intentsId.append( intent2 )
            # Checking intents
            main.log.info( item[ 'name' ] + ": Check host intents state" )
            time.sleep( 20 )
            intentResult = main.ONOScli1.checkIntentState( intentsId=intentsId )
            if not intentResult:
                main.log.info( item[ 'name' ] +  ": Check host intents state" +
                               " again")
                intentResult = main.ONOScli1.checkIntentState(
                                                          intentsId=intentsId )
            # Ping hosts
            time.sleep( 10 )
            main.log.info( item[ 'name' ] + ": Ping " + h1Name + " and " +
                           h2Name )
            pingResult1 = main.Mininet1.pingHost( src=h1Name , target=h2Name )
            if not pingResult1:
                main.log.info( item[ 'name' ] + ": " + h1Name + " cannot ping "
                               + h2Name )
            pingResult2 = main.Mininet1.pingHost( src=h2Name , target=h1Name )
            if not pingResult2:
                main.log.info( item[ 'name' ] + ": " + h2Name + " cannot ping "
                               + h1Name )
            pingResult = pingResult1 and pingResult2
            if pingResult:
                main.log.info( item[ 'name' ] + ": Successfully pinged " +
                               "both hosts" )
            else:
                main.log.info( item[ 'name' ] + ": Failed to ping " +
                               "both hosts" )
            # Rerouting ( link down )
            main.log.info( item[ 'name' ] + ": Bring link down between " +
                           sw1 + " and " + sw2 )
            main.Mininet1.link( end1=sw1,
                                end2=sw2,
                                option="down" )
            time.sleep( 5 )

            # Check onos topology
            main.log.info( item[ 'name' ] + ": Checking ONOS topology " )
            topologyResult = main.ONOScli1.topology()
            statusResult = main.ONOSbench.checkStatus( topologyResult,
                                                       main.numSwitch,
                                                       remLink )
            if not statusResult:
                main.log.info( item[ 'name' ] + ": Topology mismatch" )
            else:
                main.log.info( item[ 'name' ] + ": Topology match" )

            # Ping hosts
            main.log.info( item[ 'name' ] + ": Ping " + h1Name + " and " +
                           h2Name )
            pingResult1 = main.Mininet1.pingHost( src=h1Name , target=h2Name )
            if not pingResult1:
                main.log.info( item[ 'name' ] + ": " + h1Name + " cannot ping "
                               + h2Name )
            pingResult2 = main.Mininet1.pingHost( src=h2Name , target=h1Name )
            if not pingResult2:
                main.log.info( item[ 'name' ] + ": " + h2Name + " cannot ping "
                               + h1Name )
            pingResult = pingResult1 and pingResult2
            if pingResult:
                main.log.info( item[ 'name' ] + ": Successfully pinged " +
                               "both hosts" )
            else:
                main.log.info( item[ 'name' ] + ": Failed to ping " +
                               "both hosts" )
            # link up
            main.log.info( item[ 'name' ] + ": Bring link up between " +
                           sw1 + " and " + sw2 )
            main.Mininet1.link( end1=sw1,
                                end2=sw2,
                                option="up" )
            time.sleep( 5 )

            # Check onos topology
            main.log.info( item[ 'name' ] + ": Checking ONOS topology " )
            topologyResult = main.ONOScli1.topology()
            statusResult = main.ONOSbench.checkStatus( topologyResult,
                                                       main.numSwitch,
                                                       main.numLinks )
            if not statusResult:
                main.log.info( item[ 'name' ] + ": Topology mismatch" )
            else:
                main.log.info( item[ 'name' ] + ": Topology match" )

            # Ping hosts
            main.log.info( item[ 'name' ] + ": Ping " + h1Name + " and " +
                           h2Name )
            pingResult1 = main.Mininet1.pingHost( src=h1Name , target=h2Name )
            if not pingResult1:
                main.log.info( item[ 'name' ] + ": " + h1Name + " cannot ping "
                               + h2Name )
            pingResult2 = main.Mininet1.pingHost( src=h2Name , target=h1Name )
            if not pingResult2:
                main.log.info( item[ 'name' ] + ": " + h2Name + " cannot ping "
                               + h1Name )
            pingResult = pingResult1 and pingResult2
            if pingResult:
                main.log.info( item[ 'name' ] + ": Successfully pinged " +
                               "both hosts" )
            else:
                main.log.info( item[ 'name' ] + ": Failed to ping " +
                               "both hosts" )

            # Remove intents
            for intent in intentsId:
                main.ONOScli1.removeIntent( intentId=intent, purge=True )

            print main.ONOScli1.intents()
            stepResult = pingResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass=item[ 'name' ] +
                                            " host intent successful",
                                     onfail=item[ 'name' ] +
                                            "Add host intent failed" )
    def CASE1002( self, main ):
        """
            Add point intents between 2 hosts:
                - Get device ids
                - Add point intents
                - Check intents
                - Check flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Ping hosts
                    - Link up
                    - Ping hosts
                - Remove intents
        """

    def CASE1003( self, main ):
        """
            Add single point to multi point intents
                - Get device ids
                - Add single point to multi point intents
                - Check intents
                - Check flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Ping hosts
                    - Link up
                    - Ping hosts
                - Remove intents
        """

    def CASE1004( self, main ):
        """
            Add multi point to single point intents
                - Get device ids
                - Add multi point to single point intents
                - Check intents
                - Check flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Ping hosts
                    - Link up
                    - Ping hosts
                - Remove intents
        """
