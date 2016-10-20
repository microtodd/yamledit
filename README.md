# yamledit
Python command line YAML file editor

# Version

0.3

# Options:

    -h                  Print this help
    -v                  Version
    -f <filename>       Input file
    -o <filename>       Output file, if not specified goes to STDOUT
    -y                  If passed then any user confirmation is assumed "yes"
    -q                  If passed then everything is silent. This option implies -y.

        You must pick one and only one: -r or -c or -n
        If you pick -r or -c or -d, you must specify -f as well

    -r <key> <newvalue> Replace.  'key' is of format foo.bar.biz.baz
                        If key does not exist, returns error.
                        If used it must be the last option used.

    -c <key> <newvalue> Create. 'key is of format foo.bar.biz.baz.
                        If key already exists, will prompt to overwrite
                        unless -y is selected.
                        If used it must be the last option used.

    -n <key> <value>    New yaml file with 'key' with value 'value'.

    -d <key>            Delete 'key'


# Examples:
    python yamledit.py -f in.yml -o out.yml -f foo.bar.biz baz
    
This will set the following, and report an error if the key doesn't exist:

        foo:
            bar:
                biz: baz

# Another example:
    python yamledit.py -f in.yml -o out.yml -c foo.bar.biz baz

This will create, or optionally update if it exists:

        foo:
            bar:
                biz: baz

# Installation:

Needs python 2.7

    pip install ruamel.yaml

# Future

- Delete nodes

- Support lists

- Given two files, "merge" them together

