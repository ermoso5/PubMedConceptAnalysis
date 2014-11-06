# -*- coding: ISO-8859-1 -*-
import os
import re

class parser:
    outputdir = "output"

    def split(self, filename, chunksize=4024):
        rest = ''
        file = open(filename)

        while 1:
            chunk = file.read(chunksize)
            if not chunk:
                break
            parts = (rest+chunk).split('[PubMed - indexed for MEDLINE]\n\n')
            length = len(parts)
            for i in range(0, length-1):
                block = parts[i].split('\n\n')

                l = len(block)
                skipIndex = block[0].find('.')
                year = re.search(r'\d{4}', block[0][skipIndex:]).group()
                pmid = re.search(r'[\d]+', block[l-1]).group()
                year_dir = self.outputdir + "/" + year
                if not os.path.exists(year_dir):
                    os.makedirs(year_dir)

                with open(year_dir+ "/"+pmid+".txt","a+") as newPub:
                    newPub.write(block[l-3])
                    newPub.close()
                    print(pmid)
            rest = parts[length-1]


#usage
# parser().split("corpus/test_corpus.txt")