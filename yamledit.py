#
# yamledit.py
# github.com/microtodd/yamledit
#
import sys
import getopt
import ruamel.yaml
from ruamel import yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString, DoubleQuotedScalarString

__version__ = '0.2'

# TODO
#
# ) remove a key/value
# ) support lists
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
    -f <filename>       (Required), input file
    -o <filename>       (Optional), output file, if not specified goes to STDOUT
    -y                  (Optional), if passed then any user confirmation is assumed "yes"
    -q                  (Optional), if passed then everything is silent. This option implies -y.

        You must pick one and only one: -r or -c

    -r <key> <newvalue> Replace.  'key' is of format foo.bar.biz.baz
                        If key does not exist, returns error.
                        If used it must be the last option used.

    Example: python ecyaml.py -f in.yml -o out.yml -r foo.bar.biz baz
    This will replace:
        foo:
            bar:
                biz: baz

    -c <key> <newvalue> Create. 'key is of format foo.bar.biz.baz.
                        If key already exists, will prompt to overwrite
                        unless -y is selected.
                        If used it must be the last option used.

    Example: python ecyaml.py -f in.yml -o out.yml -c foo.bar.biz baz
    This will create:
        foo:
            bar:
                biz: baz
    '''

## printVersion
#
def printVersion():
    print '    ecyaml.py Version ' + str(__version__)

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
    keyPath = str(keyName).split('.')
    lastNodeName = keyPath.pop()
    currentNode = data
    for nodeName in keyPath:
        if nodeName in currentNode:
            currentNode = currentNode[nodeName]
        else:
            raise Exception('Could not find \'' + str(keyName) + '\' in yaml file')

    # Update the value
    if not quiet:
        if isinstance(currentNode[lastNodeName],str):
            print 'Updating \'' + str(keyName) + '\' from \'' + currentNode[lastNodeName] + '\' to \'' + newValue + '\''
        else:
            print 'Updating \'' + str(keyName) + '\', which is not currently a string, to \'' + newValue + '\''

    if autoConfirm == False and quiet == False:
        userInput = raw_input("Continue? (y/n): ")
        if userInput != 'y' and userInput != 'Y':
            print "Aborting."
            return

    currentNode[lastNodeName] = newValue

    # Output
    if outputFileName is None:
        print ruamel.yaml.round_trip_dump(data)
    else:
        newFile = open(outputFileName,'w')
        newFile.write( ruamel.yaml.round_trip_dump(data) )
        newFile.close()

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
        currentNode[lastNodeName] = {}

    outputMessage = 'Creating '
    if keyAlreadyExists:
        outputMessage = 'Updating existing key '

    if not quiet:
        if isinstance(currentNode[lastNodeName],str):
            print outputMessage + '\'' + str(keyName) + '\' from \'' + currentNode[lastNodeName] + '\' to \'' + newValue + '\''
        else:
            print outputMessage + '\'' + str(keyName) + '\' as \'' + newValue + '\''

    if autoConfirm == False and quiet == False:
        userInput = raw_input("Continue? (y/n): ")
        if userInput != 'y' and userInput != 'Y':
            print "Aborting."
            return

    currentNode[lastNodeName] = newValue

    # Output
    if outputFileName is None:
        print ruamel.yaml.round_trip_dump(data)
    else:
        newFile = open(outputFileName,'w')
        newFile.write( ruamel.yaml.round_trip_dump(data) )
        newFile.close()

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
    opts, args = getopt.getopt(argv, 'hvyqf:o:rc')
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

    # Error checking
    if inputFileName is None:
        print >> sys.stderr, 'ERROR: input file name expected (-f option)'
        sys.exit(3)

    if len(actions) == 0:
        print >> sys.stderr, 'ERROR: no action specified'
        sys.exit(4)

    # Perform whatever action
    for action in actions:
        if action == 'replace':
            try:
                replaceValue(inputFileName,outputFileName,actions[action],autoConfirm,quiet)
            except Exception as e:
                print 'ERROR: ' + str(e)
                sys.exit(5)

        elif action == 'create':
            try:
                createValue(inputFileName,outputFileName,actions[action],autoConfirm,quiet)
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




