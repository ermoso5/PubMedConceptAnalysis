__author__ = 'Zara'

import os
import re

DEBUG = False

class Parser:
    def __init__(self, outputdir):
        self.outputdir = outputdir
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

    def split(self, filename, chunksize=4024):
        rest = ''
        file = open(filename, encoding="utf-8")
        count=0

        while 1:
            chunk = file.read(chunksize)

            if not chunk and not rest:
                break

            parts = re.split("\[PubMed.*?\]", (rest+chunk))
            length = len(parts)
            if length >= 2:
                r = range(0, length-1)
            else:
                r = range(0, length)

            for i in r:
                block = parts[i].strip().split('\n\n')
                l = len(block)
                skipIndex = block[0].find('.')
                str = ' '.join(block[0:l-2])
                try:
                    year = re.search(r'\d{4}', str[skipIndex:]).group()
                except:
                    year = "unknown"
                try:
                    pmid = (re.search(r'PMID: [\d]+', block[l-1]).group())[6:]
                except:
                    pmid = "not_found_in_"+''.join(block[0][0:skipIndex])

                year_dir =  os.path.join(self.outputdir, year)

                if not os.path.exists(year_dir):
                    os.makedirs(year_dir)

                with open(os.path.join(year_dir, pmid+".txt"),"w+", encoding="utf-8") as newPub:
                    newPub.write(block[l-2])
                    newPub.close()
                    count+=1
                    print(count)
            if length > 1:
                rest = parts[length-1]
            else:
                rest = ""

    def splitMedline(self, filename, chunksize=4024):
        rest = ''
        file = open(filename, encoding="utf-8")
        yearField = ['DP  -', 'DP -', 'DP-']
        abstractField = ['AB  -', 'AB -', 'AB-']
        keywordField = ['MH  -', 'MH -', 'MH-' ]

        print("...splitting corpus into documents")
         
        while 1:
            chunk = file.read(chunksize)
            if not chunk and not rest:
                break

            docs = re.split("PMID-", (rest+chunk).strip())
            length = len(docs)
            if length > 1:
                medLineLength = length-1
            else:
                medLineLength = length

            field = re.compile(r'\n(\b\w{2,4}\b\s{0,2}-)')
            for d in range(0, medLineLength):
                doc = re.split(field, docs[d])
                keywordsFound = False

                #find pmid
                #skip medlines with no pmid
                if not doc[0]:
                    continue
                pmid = doc[0].strip()

                index = self.findOneOf(doc, keywordField)
                if index != -1:
                    abstract = ""
                    i = index
                    while doc[i].startswith("MH"):
                        abstract += doc[i+1]
                        i+=2
                    keywordsFound = True

                if not keywordsFound:
                    index = self.findOneOf(doc, abstractField)
                    if index == -1:
                        continue
                    else:
                        abstract = doc[index+1]

                index = self.findOneOf(doc, yearField)
                if index > -1:
                    year = doc[index+1].strip()[0:4]
                else:
                    year = "unknown"
                    if DEBUG:
                        print(docs[d])
                        print("-------------------------")

                year_dir = os.path.join(self.outputdir, year)

                if not os.path.exists(year_dir):
                    os.makedirs(year_dir)

                with open(os.path.join(year_dir, pmid+".txt"),"w+", encoding="utf-8") as newPub:
                    newPub.write(abstract)
                    newPub.close()

            if length > 1:
                rest = docs[length-1]
            else:
                rest = ""

    def findOneOf(self, list, listToFind):
        for l in listToFind:
            if l in list:
                return list.index(l)
        return -1

#usage
#Parser("D:/corpus/output").splitMedline("C:/Users/Zara/Downloads/medline.txt")
