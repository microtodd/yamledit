# yamledit
Python command line YAML file editor

# Options:
    -h                  Print this help
    -v                  Version
    -f <filename>       (Required), input file
    -o <filename>       (Optional), output file, if not specified goes to STDOUT
    -y                  (Optional), if passed then any user confirmation is assumed "yes"
    -q                  (Optional), if passed then everything is silent. This option implies -y.
    -r <key> <newvalue> 'key' is of format foo.bar.biz.baz
                        If used it must be the last option used.

# Example:
    python ecyaml.py -f in.yml -o out.yml -f foo.bar.biz baz
    
This will set:

        foo:
            bar:
                biz: baz

# Installation:

Needs python 2.7

    pip install ruamel.yaml