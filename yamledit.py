#
# yamledit.py
# github.com/microtodd/yamledit
#
import os
import sys
import getopt
import ruamel.yaml
from ruamel import yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString, DoubleQuotedScalarString

__version__ = '0.5'

# TODO
#
# ) merge two yaml files capability
# ) Support input pipe instead of file
#

## printHelp
#
def printHelp():
    print '''    yamledit.py

    Editor for Commandline for YAML

    Options:
    -h                  Print this help
    -v                  Version
    -f <filename>       Input file
    -o <filename>       Output file, if not specified goes to STDOUT
    -y                  If passed then any user confirmation is assumed 'yes'
    -q                  If passed then everything is silent. This option implies -y.

        You must pick one and only one: -r or -c or -n or -d or -g
        If you pick -r or -c or -d, you must specify -f as well

        <newvalue> can be a comma-separated list, which is treated as a YAML list

    -r <key> <newvalue> Replace.  'key' is of format foo.bar.biz.baz
                        If key does not exist, returns error.
                        If used it must be the last option used.
    
    -c <key> <newvalue> Create. 'key' is of format foo.bar.biz.baz.
                        If key already exists, will prompt to overwrite
                        unless -y is selected.
                        If used it must be the last option used.

    -n <key> <value>    New file with 'key' with value 'value'.

    -d <key>            Delete 'key'

    -g <key>            Print the value of <key>, to STDOUT or to the filename
    '''

## printVersion
#
def printVersion():
    print '    yamledit.py Version ' + str(__version__)

## createFile
#
# @param[in] filename
# @param[in] data
# @param[in] autoConfirm
# @param[in] quiet
#
def createFile(outputFileName, data, autoConfirm, quiet):

    # see if file exists
    if os.path.exists(outputFileName):

        # See if we autoconfirmed
        if autoConfirm or quiet:
            pass
        else:
            userInput = raw_input('File \'' + str(outputFileName) + '\' exists. Overwrite? (y/n): ')
            if userInput != 'y' and userInput != 'Y':
                print 'Aborting.'
                return

    # Create the file
    newFile = open(outputFileName,'w')
    newFile.write( ruamel.yaml.round_trip_dump(data) )
    newFile.close()

## createTxtFile
#
# @param[in] filename
# @param[in] data
# @param[in] autoConfirm
# @param[in] quiet
#
def createTxtFile(outputFileName, data, autoConfirm, quiet):

    # see if file exists
    if os.path.exists(outputFileName):

        # See if we autoconfirmed
        if autoConfirm or quiet:
            pass
        else:
            userInput = raw_input('File \'' + str(outputFileName) + '\' exists. Overwrite? (y/n): ')
            if userInput != 'y' and userInput != 'Y':
                print 'Aborting.'
                return

    # Create the file
    newFile = open(outputFileName,'w')
    newFile.write( data )
    newFile.close()

## replaceValue
#
# @param[in] inputFileName
# @param[in] outputFileName
# @param[in] [keyName,newValue]
# @param[in] autoConfirm
# @param[in] quiet
#
def replaceValue(inputFileName, outputFileName, values, autoConfirm, quiet):
    keyName = values[0]
    newValue = values[1]
    inputFile = None        # Handle to input file data

    # Open file
    try:
        inputFile = open(inputFileName)
    except Exception as e:
        raise Exception('Could not open/parse file \'' + str(inputFileName) + '\': ' + str(e))

    # Load it
    data = ruamel.yaml.round_trip_load(inputFile, preserve_quotes=True)

    # See if the key exists
    # TODO move this piece into a method called 'findNode', and let createValue use it as well
    keyPath = str(keyName).split('.')
    lastNodeName = keyPath.pop()
    currentNode = data
    for nodeName in keyPath:
        if nodeName in currentNode:
            currentNode = currentNode[nodeName]
        else:
            raise Exception('Could not find \'' + str(keyName) + '\' in yaml file')

    # Check that last key
    if lastNodeName not in currentNode:
        raise Exception('Could not find \'' + str(keyName) + '\' in yaml file')

    # Update the value
    if not quiet:
        extra = ''
        if str(newValue).find(',') != -1:
            extra = ' (a list)'
        if isinstance(currentNode[lastNodeName],str):
            print 'Updating \'' + str(keyName) + '\' from \'' + currentNode[lastNodeName] + '\' to \'' + newValue + '\'' + extra
        else:
            print 'Updating \'' + str(keyName) + '\', which is not currently a string, to \'' + newValue + '\'' + extra

    if autoConfirm == False and quiet == False:
        userInput = raw_input('Continue? (y/n): ')
        if userInput != 'y' and userInput != 'Y':
            print 'Aborting.'
            return

    # See if new value is a string or a list
    if str(newValue).find(',') == -1:
        currentNode[lastNodeName] = newValue
    else:
        newValueList = str(newValue).split(',')
        currentNode[lastNodeName] = newValueList

    # Output
    if outputFileName is None:
        print ruamel.yaml.round_trip_dump(data)
    else:
        createFile(outputFileName, data, autoConfirm, quiet)
        
## createValue
#
# @param[in] inputFileName
# @param[in] outputFileName
# @param[in] [keyName,newValue]
# @param[in] autoConfirm
# @param[in] quiet
#
def createValue(inputFileName, outputFileName, values, autoConfirm, quiet):
    keyName = values[0]
    newValue = values[1]
    inputFile = None        # Handle to input file data

    # Open file
    try:
        inputFile = open(inputFileName)
    except Exception as e:
        raise Exception('Could not open/parse file \'' + str(inputFileName) + '\': ' + str(e))

    # Load it
    data = ruamel.yaml.round_trip_load(inputFile, preserve_quotes=True)

    # See if the key exists, create the new path if necessary
    keyAlreadyExists = True
    keyPath = str(keyName).split('.')
    lastNodeName = keyPath.pop()
    currentNode = data
    for nodeName in keyPath:
        if nodeName in currentNode:
            currentNode = currentNode[nodeName]
        else:
            keyAlreadyExists = False
            currentNode[nodeName] = {}
            currentNode = currentNode[nodeName]

    if lastNodeName not in currentNode:
        keyAlreadyExists = False
        currentNode[lastNodeName] = {}

    outputMessage = 'Creating '
    if keyAlreadyExists:
        outputMessage = 'Updating existing key '

    if not quiet:
        extra = ''
        if str(newValue).find(',') != -1:
            extra = ' (a list)'
        if isinstance(currentNode[lastNodeName],str):
            print outputMessage + '\'' + str(keyName) + '\' from \'' + currentNode[lastNodeName] + '\' to \'' + newValue + '\'' + extra
        else:
            print outputMessage + '\'' + str(keyName) + '\' as \'' + newValue + '\'' + extra

    if autoConfirm == False and quiet == False:
        userInput = raw_input('Continue? (y/n): ')
        if userInput != 'y' and userInput != 'Y':
            print 'Aborting.'
            return

    # See if new value is a string or a list
    if str(newValue).find(',') == -1:
        currentNode[lastNodeName] = newValue
    else:
        newValueList = str(newValue).split(',')
        currentNode[lastNodeName] = newValueList

    # Output
    if outputFileName is None:
        print ruamel.yaml.round_trip_dump(data)
    else:
        createFile(outputFileName, data, autoConfirm, quiet)

## newFile
#
# @param[in] outputFileName
# @param[in] [keyName,newValue]
# @param[in] autoConfirm
# @param[in] quiet
#
def newFile(outputFileName, values, autoConfirm, quiet):
    keyName = values[0]
    newValue = values[1]

    # New data
    newData = ''

    # See if the key exists, create the new path if necessary
    numTabs = 0
    keyPath = str(keyName).split('.')
    lastNodeName = keyPath.pop()
    for nodeName in keyPath:

        # Build out the data
        if numTabs == 0:
            newData += str(nodeName) + ':'

        # Make sure we put the applicable number of tabs in
        else:
            newData += '\n'
            for x in range(0, numTabs):
                newData += '   '
            newData += str(nodeName) + ':'
        numTabs += 1


    # Last node, again make sure we do the applicable number of tabs
    newData += '\n'
    for x in range(0, numTabs):
        newData += '   '
    newData += lastNodeName + ': ' + newValue + '\n'

    # Confirm
    if autoConfirm == False and quiet == False:
        userInput = raw_input('Create new yaml? (y/n): ')
        if userInput != 'y' and userInput != 'Y':
            print 'Aborting.'
            return

    # Prep the yaml object
    data = ruamel.yaml.round_trip_load(newData, preserve_quotes=True)

    # Output
    if outputFileName is None:
        print ruamel.yaml.round_trip_dump(data)
    else:
        createFile(outputFileName, data, autoConfirm, quiet)

## deleteKey
#
# @param[in] inputFileName
# @param[in] outputFileName
# @param[in] keyName
# @param[in] autoConfirm
# @param[in] quiet
#
def deleteKey(inputFileName, outputFileName, keyName, autoConfirm, quiet):
    inputFile = None        # Handle to input file data

    # Open file
    try:
        inputFile = open(inputFileName)
    except Exception as e:
        raise Exception('Could not open/parse file \'' + str(inputFileName) + '\': ' + str(e))

    # Load it
    data = ruamel.yaml.round_trip_load(inputFile, preserve_quotes=True)

    # See if the key exists
    # TODO move this piece into a method called 'findNode', and let createValue use it as well
    keyPath = str(keyName).split('.')
    lastNodeName = keyPath.pop()
    currentNode = data
    for nodeName in keyPath:
        if nodeName in currentNode:
            currentNode = currentNode[nodeName]
        else:
            raise Exception('Could not find \'' + str(keyName) + '\' in yaml file')

    # Check that last key
    if lastNodeName not in currentNode:
        raise Exception('Could not find \'' + str(keyName) + '\' in yaml file')

    # Update the value
    if not quiet:
        if isinstance(currentNode[lastNodeName],str):
            print 'Removing key \'' + str(keyName) + '\' which has value \'' + currentNode[lastNodeName] +'\''
        else:
            print 'Removing key \'' + str(keyName) + '\', which is not currently a string'

    if autoConfirm == False and quiet == False:
        userInput = raw_input('Continue? (y/n): ')
        if userInput != 'y' and userInput != 'Y':
            print 'Aborting.'
            return

    del currentNode[lastNodeName]

    # Output
    if outputFileName is None:
        print ruamel.yaml.round_trip_dump(data)
    else:
        createFile(outputFileName, data, autoConfirm, quiet)

## getValue
#
# @param[in] inputFileName
# @param[in] outputFileName
# @param[in] keyName
# @param[in] autoConfirm
# @param[in] quiet
#
def getValue(inputFileName, outputFileName, keyName, autoConfirm, quiet):
    inputFile = None        # Handle to input file data

    # Open file
    try:
        inputFile = open(inputFileName)
    except Exception as e:
        raise Exception('Could not open/parse file \'' + str(inputFileName) + '\': ' + str(e))

    # Load it
    data = ruamel.yaml.round_trip_load(inputFile, preserve_quotes=True)

    # See if the key exists
    # TODO move this piece into a method called 'findNode', and let createValue use it as well
    keyPath = str(keyName).split('.')
    lastNodeName = keyPath.pop()
    currentNode = data
    for nodeName in keyPath:
        if nodeName in currentNode:
            currentNode = currentNode[nodeName]
        else:
            raise Exception('Could not find \'' + str(keyName) + '\' in yaml file')

    # Check that last key
    if lastNodeName not in currentNode:
        raise Exception('Could not find \'' + str(keyName) + '\' in yaml file')

    # Get the value
    if outputFileName is None:
        if isinstance(currentNode[lastNodeName],str):
            print currentNode[lastNodeName]
        else:
            print ruamel.yaml.round_trip_dump(currentNode[lastNodeName])
    else:
        if isinstance(currentNode[lastNodeName],str):
            createTxtFile(outputFileName, currentNode[lastNodeName], autoConfirm, quiet)
        else:
            createFile(outputFileName, currentNode[lastNodeName], autoConfirm, quiet)

## main
#
def main(argv):

    # Set up some variables
    inputFileName = None
    outputFileName = None
    actions = {}
    autoConfirm = False
    quiet = False

    # Grab and process the command line arguments
    opts, args = getopt.getopt(argv, 'hvyqnrcf:o:d:g:')
    for opt, arg in opts:
        if opt == '-f':
            inputFileName = str(arg)

        if opt == '-o':
            outputFileName = str(arg)

        if opt == '-y':
            autoConfirm = True

        if opt == '-q':
            quiet = True

        if opt == '-v':
            printVersion()
            sys.exit(0)

        if opt == '-h':
            printHelp()
            sys.exit(0)

        # For delete, only one value, the key
        if opt == '-d':
            actions['delete'] = str(arg)

        # For get, only one value, the key
        if opt == '-g':
            actions['get'] = str(arg)

        # If -r is used, we assume two arguments
        if opt == '-r':
            if len(args) != 2:
                print >> sys.stderr, 'ERROR: -r expects 2 arguments'
                sys.exit(2)

            sourceKey = None
            newValue = None
            if args[0]:
                sourceKey = str(args[0])
            if args[1]:
                newValue = str(args[1])
            actions['replace'] = [sourceKey,newValue]

        # If -c is used, we assume two arguments
        if opt == '-c':
            if len(args) != 2:
                print >> sys.stderr, 'ERROR: -c expects 2 arguments'
                sys.exit(2)

            sourceKey = None
            newValue = None
            if args[0]:
                sourceKey = str(args[0])
            if args[1]:
                newValue = str(args[1])
            actions['create'] = [sourceKey,newValue]

        # If -n is used, we assume two arguments
        if opt == '-n':
            if len(args) != 2:
                print >> sys.stderr, 'ERROR: -n expects 2 arguments'
                sys.exit(2)

            sourceKey = None
            newValue = None
            if args[0]:
                sourceKey = str(args[0])
            if args[1]:
                newValue = str(args[1])
            actions['new'] = [sourceKey,newValue]


    # Error checking
    if len(actions) == 0:
        print >> sys.stderr, 'ERROR: no action specified'
        sys.exit(4)

    # Perform whatever action
    for action in actions:
        if action == 'replace':
            if inputFileName is None:
                print >> sys.stderr, 'ERROR: input file name expected (-f option)'
                sys.exit(3)
            try:
                replaceValue(inputFileName,outputFileName,actions[action],autoConfirm,quiet)
            except Exception as e:
                print 'ERROR: ' + str(e)
                sys.exit(5)

        elif action == 'create':
            if inputFileName is None:
                print >> sys.stderr, 'ERROR: input file name expected (-f option)'
                sys.exit(3)
            try:
                createValue(inputFileName,outputFileName,actions[action],autoConfirm,quiet)
            except Exception as e:
                print 'ERROR: ' + str(e)
                sys.exit(5)

        elif action == 'new':
            try:
                newFile(outputFileName,actions[action],autoConfirm,quiet)
            except Exception as e:
                print 'ERROR: ' + str(e)
                sys.exit(5)

        elif action == 'delete':
            try:
                deleteKey(inputFileName,outputFileName,actions[action],autoConfirm,quiet)
            except Exception as e:
                print 'ERROR: ' + str(e)
                sys.exit(5)

        elif action == 'get':
            try:
                getValue(inputFileName,outputFileName,actions[action],autoConfirm,quiet)
            except Exception as e:
                print 'ERROR: ' + str(e)
                sys.exit(5)

        # Unknown action
        else:
            print >> sys.stderr, 'ERROR: unknown action: ' + str(action)

    if not quiet:
        print 'Successfully completed'

## Run
if __name__ == '__main__':
    main(sys.argv[1:])




