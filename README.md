PubMedConceptAnalysis
=====================

DMKM 2014 - Natural Language Processing case study

Analysis of the appearance of new concepts and of the change of the meaning of existing concepts in the PubMed corpus

Required packages:
  - python 3.4.0
  - nltk 3.0.0
  - networkx
  - numpy
  - scipy
  - matplotlib
  - pyner
  - gensim

Additional requirements:
  - run the Stanford Named Entity Recognition local server using the "ner.sh" file in Linux or the "ner.bat" in Windows.
  - run nltk.download() in the python shell and download the WordNet corpus.
  
To test the program, download the abstracts from PubMed in MEDLINE format.
The following test set covers 10 years of publications:
http://www.ncbi.nlm.nih.gov/pubmed/?term=%28%28%221990%2F01%2F01%22[PDAT]%20%3A%20%221999%2F01%2F01%22[PDAT]%29%20AND%20%22humans%22[MeSH%20Terms]%29%20AND%20%22english%22[Language]%20AND%20%28hasabstract[text]%20AND%20%22humans%22[MeSH%20Terms]%20AND%20jsubsetaim[text]%29  
 
With the Stanford NER running in the background you can build the persistent graph:
    
    python make_graph.py

This creates a sqlite3 database out of the MEDLINE file and may take some time. Also, make sure you play with the parameters.
Finally, you can collect some statistics and run an analysis of the paths between medical terms:

    python make_graph.py

