#!/bin/python
import os
import glob
import re
from HTMLParser import HTMLParser

def cleanhtml(raw_html):
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr,'', raw_html)
    return cleantext

def print_table(newfilename, protocol, controller, type, table):
    file = open(newfilename, "w")
    num_colums = len(table[0])
    
    file.write("\\begin{tabular}{" + ("|l"*num_colums) +"|} \n\hline\n")
    for line in table:
        file.write((" & ".join(line)) + " \\\\ \n\hline\n")
    
    file.write("\\end{tabular}")
    file.close()

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.table = []
        self.cur_line = []
        self.data = ""
        
    def handle_starttag(self, tag, attrs):
        if tag in ['td', 'th']:
            if ("bgcolor", "lightgrey") in attrs:
                self.data = "\cellcolor{gray}{0.8}"
            else:
                self.data = ""
        elif tag=='tr':
            self.cur_line = []

    def handle_endtag(self, tag):
        if tag in ["td", "th"]:
            self.cur_line.append(" ".join(self.data.split()))
        elif tag=="tr":
            self.table.append(self.cur_line)

    def handle_data(self, data):
        self.data += data
        
    def get_table(self):
        return self.table
    
def make_table(protocol, controller, type):
    prefix = protocol + "/" + controller + "_" + type + "_"
    first_line = ["\\bf " + type, "\\bf Function name", "\\bf Description"] if type=="action" else ["\\bf " + type, "\\bf Description"]
    table = [first_line]
    newfilename = "out/" + protocol + "/"+controller+"_"+type+".tex"
    for filename in glob.glob(prefix + "*"):
        file = open(filename, 'r')
        desc = cleanhtml(file.read()).strip().split(":")[1]
        cols = desc.split("-")
        col0 = cols[0].strip().replace("_", "\\_")
        col1 = cols[1].strip().replace("_", "\\_")
        col05 = filename[len(prefix):-5].replace("_", "\\_")  if type == "action" else ""
        table.append([col0, col05, col1] if type=="action" else [col0, col1])
        file.close()
    
    print_table(newfilename, protocol, controller, type, table)

def convert_table(protocol, controller):
    file = open(protocol + "/" + controller + "_table.html", 'r')
    parser = MyHTMLParser()
    parser.feed(file.read())
    file.close()
    table =  parser.get_table()
    for i in range(1, len(table)-1):
        table[i] = table[i][0:len(table[i])-1]
    table = table[0:len(table)-1]
    
    print_table("out/" + protocol + "/"+controller+"_table.tex", protocol, controller, "table", table)    

dirs = [x[1] for x in os.walk('.')][0]
dirs = [x for x in dirs if not x.startswith('.')]
dirs = [x for x in dirs if not x=="out"]

if not os.path.isdir("out"):
    os.makedirs("out")

for protocol in dirs:
    print "- Parsing files for protocol " + protocol
    if not os.path.isdir("out/"+protocol):
        os.makedirs("out/"+protocol)
    for controller in ["Directory", "DMA", "L0Cache", "L1Cache", "L2Cache"]:
        file_list = glob.glob(protocol + "/" + controller + "*")
        if len(file_list) != 0:
            print "---> Parsing "+ controller + " files"
            make_table(protocol, controller, "State")
            make_table(protocol, controller, "action")
            make_table(protocol, controller, "Event")
            convert_table(protocol, controller)
            
