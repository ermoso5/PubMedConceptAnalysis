
import os
import re
from chardet import detect

class Parser:
    outputdir = "output"

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

                year_dir = self.outputdir + "/" + year
                if not os.path.exists(year_dir):
                    os.makedirs(year_dir)

                with open(year_dir+ "/"+pmid+".txt","w+") as newPub:
                    newPub.write(block[l-2])
                    newPub.close()
                    count+=1
                    print(count)
            if length > 1:
                rest = parts[length-1]
            else:
                rest = ""


#usage
# parser().split("corpus/test_corpus.txt")