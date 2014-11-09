# -*- coding: ISO-8859-1 -*-
import os
import re


class Parser:
    outputdir = "output"

    def split(self, filename, chunksize=4024):
        rest = ''
        file = open(filename)

        while 1:
            chunk = file.read(chunksize)
            if not chunk and not rest:
                break

            parts = re.split("\[PubMed -.*?\]", (rest+chunk))
            length = len(parts)
            if length >= 2:
                r = range(0, length-1)
            else:
                r = range(0, length)

            for i in r:
                block = parts[i].strip().split('\n\n')
                l = len(block)
                skipIndex = block[0].find('.')
                year = re.search(r'\d{4}', block[0][skipIndex:]).group()
                pmid = (re.search(r'PMID: [\d]+', block[l-1]).group())[6:]
                year_dir = self.outputdir + "/" + year
                if not os.path.exists(year_dir):
                    os.makedirs(year_dir)

                with open(year_dir+ "/"+pmid+".txt","w+") as newPub:
                    newPub.write(block[l-2])
                    newPub.close()
                    print(pmid)
            if length > 1:
                rest = parts[length-1]
            else:
                rest = ""


#usage
# parser().split("corpus/test_corpus.txt")