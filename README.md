# PIDMEM

A program that logs memory usage of a running process id

positional arguments:
  pid                   Process ID

options:
  -h, --help            show this help message and exit
  -d DELAY, --delay DELAY
                        Delay between samples in seconds (can be a float value)
  -o, --output          Output the memory usage to stderr
  -j, --json            Output the memory usage in json format
  -g FILENAME, --graph FILENAME
                        Output a graph of the memory usage