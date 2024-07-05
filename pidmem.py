import matplotlib.pyplot
import psutil
import time
import argparse
import json
import signal
import sys
import matplotlib

class MemParser:
    def __init__(self, json=False, output=False, graphname=""):
        self.json = json
        self.output = output
        self.mem_stats = {
            'vms': [],
            'rss': [],
            'time': []
        }
        self.start_time = time.time()
        self.graphname = graphname

    def __call__(self, meminfo):
        if self.output:
            print(str((int)(time.time() - self.start_time)) + ":", meminfo.vms, file=sys.stderr)
        self.mem_stats['vms'].append(meminfo.vms)
        self.mem_stats['rss'].append(meminfo.rss)
        self.mem_stats['time'].append(time.time() - self.start_time)
    
    def graph(self):
        mem_sizes = [1, 1024, 1024*1024, 1024*1024*1024]
        mem_names = ['B', 'KB', 'MB', 'GB']
        max_size = max(self.mem_stats['vms'])
        factor = 1
        name = "B"
        for i in range(len(mem_sizes)):
            if max_size >= mem_sizes[i]:
                factor = mem_sizes[i]
                name = mem_names[i]
            else:
                break
        matplotlib.pyplot.plot(self.mem_stats['time'], [i / factor for i in self.mem_stats['vms']])
        y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)
        ax = matplotlib.pyplot.gca()
        ax.yaxis.set_major_formatter(y_formatter)
        matplotlib.pyplot.xlabel('Time (s)')
        matplotlib.pyplot.ylabel('Virtual Memory Usage (' + name + ')')
        matplotlib.pyplot.subplots_adjust(bottom=.12, left=.18)
        matplotlib.pyplot.title('Memory Usage Over Time')
        matplotlib.pyplot.savefig(self.graphname)

    def flush(self):
        if self.json:
            print(json.dumps(self.mem_stats))
        else:
            print(self.mem_stats)
        if self.graphname != "":
            self.graph()

class Exiter:
    def __init__(self, parser):
        self.parser = parser
    
    def __call__(self, signum, frame):
        self.parser.flush()
        exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='pidmem',
        description='A program that logs memory usage of a running process id'
    )
    parser.add_argument('pid', type=int, help='Process ID')
    parser.add_argument('-d', '--delay', type=float, default=1, help='Delay between samples in seconds (can be a float value)')
    parser.add_argument('-o', '--output', action='store_true', help='Output the memory usage to stderr')
    parser.add_argument('-j', '--json', action='store_true', help='Output the memory usage in json format')
    parser.add_argument('-g', '--graph', type=str, default="", metavar="FILENAME", help='Output a graph of the memory usage')
    args = parser.parse_args()
    pid = int(args.pid)
    process = psutil.Process(pid)
    memparser = MemParser(args.json, args.output, args.graph)
    signal.signal(signal.SIGINT, Exiter(memparser))
    start_time = time.time_ns()
    ticks = 0
    while True:
        time.sleep(max(start_time + ticks * int(args.delay * 1000000000) - time.time_ns(), 0) / 1000000000)
        memory_info = process.memory_info()
        memparser(memory_info)
        ticks += 1