#!/bin/python
import os
import glob
import re
from HTMLParser import HTMLParser

def split_array(arr, size):
     arrs = []
     while len(arr) > size:
         pice = arr[:size]
         arrs.append(pice)
         arr   = arr[size:]
     arrs.append(arr)
     return arrs

def cleanhtml(raw_html):
    cleanr =re.compile('<.*?>')
    cleantext = re.sub(cleanr,'', raw_html)
    return cleantext

def print_portrait_table(newfilename, protocol, controller, type, table):
    file = open(newfilename, "w")
    num_colums = len(table[0])
    
    file.write("\\begin{table}\n\\centering\n\\begin{adjustbox}{max width=\\textwidth}\n\\begin{tabular}{" + ("|l"*num_colums) +"|} \n\hline\n")
    for line in table:
        file.write((" & ".join(line)) + " \\\\ \n\hline\n")
    
    file.write("\\end{tabular}\n\\end{adjustbox}\n\\caption{"+ protocol.replace("_", "\\_") + " - " + controller + " - " + type + "}\n")
    file.write("\\end{table}")
    file.close()

def print_landscape_table(newfilename, protocol, controller, type, table):
    file = open(newfilename, "w")
    num_colums = len(table[0])
    n = 200/int(num_colums) # max chars per cell
    blocks = split_array(table[1:], 20)
    num_blocks = len(blocks)
    index = 0
    for block in blocks:
        index += 1
        title_line = table[0][:]
        file.write("\\begin{sidewaystable}\n\\centering\n\\begin{adjustbox}{max width=\\textwidth}\n\\begin{tabular}{" + ("|l"*num_colums) +"|} \n\hline\n")
        for line in ([title_line] + block):
            for k in range(0, len(line)):
                entry = line[k]
                split_entry = [entry[i * n:i * n+n] for i,blah in enumerate(entry[::n])]
                if not entry.startswith("\\cellcolor[gray]{0.8}"):
                    line[k] = "\\makecell[l]{" + "\\\\".join(split_entry) + "}"
            file.write((" & ".join(line)) + " \\\\ \n\hline\n")

        file.write("\\end{tabular}\n\\end{adjustbox}\n")
        file.write("\\caption{" + protocol.replace("_", "\\_") + " - " + controller + " - " + type + ("" if num_blocks==1 else ("- part " + str(index) + "/" + str(num_blocks))) + "}\n")
        file.write("\\end{sidewaystable}\n")
        
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
                self.data = "\cellcolor[gray]{0.8}"
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
    
    print_portrait_table(newfilename, protocol, controller, type, table)
    return protocol + "/"+controller+"_"+type+".tex"

def convert_table(protocol, controller):
    file = open(protocol + "/" + controller + "_table.html", 'r')
    parser = MyHTMLParser()
    parser.feed(file.read())
    file.close()
    table =  parser.get_table()
    for i in range(1, len(table)-1):
        table[i] = table[i][0:len(table[i])-1]
    table = table[0:len(table)-1]
    
    newfilename = "out/" + protocol + "/"+controller+"_table.tex"
    print_landscape_table(newfilename, protocol, controller, "table", table) 
    return protocol + "/"+controller+"_table.tex"

dirs = [x[1] for x in os.walk('.')][0]
dirs = [x for x in dirs if not x.startswith('.')]
dirs = [x for x in dirs if not x=="out"]

if not os.path.isdir("out"):
    os.makedirs("out")


file = open("out/main.tex", "w")
file.write('''\documentclass[11pt,a4paper]{report}\n
\\usepackage[utf8]{inputenc}
\\usepackage[english]{babel}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{graphicx}
\\usepackage{lmodern}
\\usepackage{tabularx}
\\usepackage[table]{xcolor}
\\usepackage[left=2cm,right=2cm,top=2cm,bottom=2cm]{geometry}
\\usepackage{makecell}
\\usepackage{rotating}
\\usepackage{adjustbox}
\\begin{document}\n''')    
    
for protocol in dirs:
    print "- Parsing files for protocol " + protocol
    if not os.path.isdir("out/"+protocol):
        os.makedirs("out/"+protocol)
    file.write("\\chapter{"+ protocol.replace("_", "\\_") +"}")
    for controller in ["Directory", "DMA", "L0Cache", "L1Cache", "L2Cache"]:
        file_list = glob.glob(protocol + "/" + controller + "*")
        if len(file_list) != 0:
            print "---> Parsing "+ controller + " files"
            filename = make_table(protocol, controller, "State")
            file.write("\\input{"+ filename + "}")
            filename = make_table(protocol, controller, "action")
            file.write("\\input{"+ filename + "}")
            filename = make_table(protocol, controller, "Event")
            file.write("\\input{"+ filename + "}")
            filename = convert_table(protocol, controller)
            file.write("\\input{"+ filename + "}")
    

file.write("\\end{document}")
file.close()
# Now generate one common file    
