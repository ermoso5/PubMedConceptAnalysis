PubMedConceptAnalysis
=====================

DMKM 2014 - Natural Language Processing case study

Analysis of the appearance of new concepts and of the change of the meaning of existing concepts in the PubMed corpus

Required packages:
  - python 3.4.0
  - nltk 3.0.0
  - pyner
  
Setting up the Stanford Named Entity Recognition server:
Linux
    java -mx1000m -cp stanford-ner.jar: edu.stanford.nlp.ie.NERServer -loadClassifier adept.ser.gz -port 9191 -outputFormat inlineXML
Windows
    java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer \ -loadClassifier adept.ser.gz -port 9191 -outputFormat inlineXML
