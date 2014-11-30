"""
This class provides the preprocessing functions for the PubMed corpus:
    processFolder(root, target, stemming, min_word_length, remove_numbers, remove_duplicates, ner)
    processString(string, stemming, min_word_length, remove_numbers, remove_duplicates, ner)
"""

import os
import time
import json

from nltk import stem
from adeptner import Adeptner
from graph import Graph

__author__ = "Marcello Benedetti"
__status__ = "Prototype"


DEBUG = False
     
EXCLUDE = ['!', '?', '.', ',', ':', ';', '_', '-', '+', '*', '/', '\\', '^', 
"'", '"', '’' , '(', ')', '[', ']', '=', '°', '|', '{', '}', '\n', '\t',
'%', '¡', '¨', '“', '”', '`', '<', '>', '$', '&', '@', '#', '°']

STOP_WORDS = ['a', 'able', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 
'also', 'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before', 
'being', 'below', 'between', 'both', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do', 
'does', 'doing', 'don', 'down', 'during', 'each', 'either', 'else', 'ever', 'every', 'few', 'for', 
'from', 'further', 'get', 'got', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 
'herself', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 
'itself', 'just', 'least', 'let', 'like', 'likely', 'may', 'me', 'might', 'more', 'most', 'must', 
'my', 'myself', 'neither', 'no', 'nor', 'not', 'now', 'of', 'off', 'often', 'on', 'once', 'only', 
'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'rather', 's', 'said', 'same', 
'say', 'says', 'she', 'should', 'since', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their', 
'theirs', 'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'thus', 
'to', 'too', 'under', 'until', 'up', 'us', 'very', 'wants', 'was', 'we', 'were', 'what', 'when', 
'where', 'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would', 'yet', 'you', 'your', 
'yours', 'yourself', 'yourselves']

PREFIXES = ['von', 'de', 'vant', 'van', 'der', 'vom', 'vander', 'zur',
'ten', 'la', 'du', 'ter', 'dos', 'al', 'del', 'st', 'le', 'dos', 'da', 
'do', 'mc', 'des', 'den', 'di', 'abu', 'vander', 'den', 'della', 'vande', 
'dit', 'bin', 'ibn', 'el', 'los', 'dello', 'vanden', 'ap', 'las', 'delli', 
'mac', 'mrs', 'mr', 'miss', 'jr', 'sr', 'II', 'III', 'IV', 'in']  
     
     
class Processor(object):

    def __init__(self):
        self.exclude = EXCLUDE
        self.stop_words = STOP_WORDS
        self.prefixes = PREFIXES    #currently prefixes are not used
        self.ner = Adeptner()
            
    
    def folderToGraph(self, root="corpus", target_folder=None, graph=None, ner=False, lemmatize=True, stemming='medium', min_word_length=1):
        """
        Creates a target folder and related subdirectories according to the structure of the root folder. 
        Then, processes all the textual files in the root structure and store the results in the target structure.
        
        :root               The root folder contains years subfolders that in turn contain the '.txt' documents.
        :target_folder      The folderwhere to store the processed files.
        :graph              The graph object.
        :ner                Use named entity recognition.
        :stemming           Choose whether or not applying stemming. It may be None, 'light', 'medium', 'heavy'. 
        :min_word_length    Minimum number of characters for a word to be kept. 
        :return             None
        """
        if not os.path.isdir(root):
            raise Exception("'{0}' folder doesn't exist".format(root))
        if graph:
            if not isinstance(graph, Graph):
                raise Exception("The graph object is non valid")
            graph.connect()
        if target_folder and not os.path.isdir(target_folder):       #create 'target' folder if it doesn't exist
            os.mkdir(target_folder)            
            
        print("...preprocessing documents and building the graph")
        count_nodes = 0 
        count_edges = 0
              
        for dir in os.listdir(root):                            #visit year subdirectories of 'root' folder
            dir_origin = os.path.join(root, dir)
            if os.path.isdir(dir_origin) and dir.isdigit():     #don't visit directories whose name is not a year
                year = int(dir)                               
                
                if target_folder:
                    dir_dest = os.path.join(target_folder, dir)
                    if not os.path.isdir(dir_dest):             #create year subfolders if they don't exist in 'target' 
                        os.mkdir(dir_dest)
       
                for file in os.listdir(dir_origin):             #open textual files under year folder and process them
                    if file.endswith(".txt"):               
                        string = self.fileToString(os.path.join(dir_origin, file))              #put file into string
                        entities = self.processString(string, ner, lemmatize, stemming, min_word_length)
                        
                        if entities: 
                            if DEBUG:
                                print(entities)
                            if graph:                               
                                cn, ce = graph.addToGraph(entities, int(year))             
                                count_nodes += cn
                                count_edges += ce
                            if target_folder:
                                self.stringToFile(os.path.join(dir_dest, file), entities)   #save string to file
                graph.commit()
        graph.close()
        print("added {0} nodes to {1} ".format(count_nodes, graph.graph_nodes))
        print("added {0} edges to {1} ".format(count_edges, graph.graph_edges))   


    def processString(self, string, ner=False, lemmatize=True, stemming=None, min_word_length=1):
        """ 
        Apply prerpocessing to a string.
        :ner                Use named entity recognition (if True) or text preprocessing (if False) to extract entities.
        :stemming           Choose whether or not applying stemming. It may be None, 'light', 'medium', 'heavy'. 
        :min_word_length    Minimum number of characters for a word to be kept. 
        :return             Cleaned up string
        """
        entities = []
        result = []
        
        if ner:
            entities = self.getEntities(string)                     #perform named entity recognition 
        else:
            string = self.removeStopwords(string)                   #remove the stopwords in STOP_WORDS
            entities = string.split(" ")                            #this creates a bag of words        
        
        if entities:    
            for ent in entities:
                ent = self.cleanText(ent)                             #remove punctuation and numbers
                if lemmatize:
                    ent = self.lemmatizeText(ent)                       #perform lemmatization
                if stemming:
                    ent = self.stemText(ent, intensity=stemming)        #perform stemming
                if min_word_length > 0:
                    ent = self.removeShortWords(ent, min_word_length)   #remove short words
                ent = ent.strip()                                       #remove trailing spaces
                if ent:
                    result.append(ent)
            
        result = list(set(result))                                  #remove duplicates
        return result


    def fileToString(self, file_path):
        """Take the content of a file and put it in a string."""
        text = ""
        if file_path:
            with open(file_path, "r") as f:
                text = f.read() #omit size to read it all
                f.close()
        return text
     
     
    def stringToFile(self, file_path, text):
        """Take the content of a string and put it in a '.txt' file."""
        if file_path and text:
            with open(file_path, "w") as f:
                f.write(text)
                f.close()

    
    def getEntities(self, text):
        """Apply Named Entity Recognition from Stanford's web service ADEPTA."""
        return self.ner.getTerms(text).get('MEDTERM')


    def lemmatizeText(self, text):
        """Apply lemmatization to a string."""
        l = stem.WordNetLemmatizer()
        bow = text.split(" ")           #this creates a bag of words
        result = []
        for word in bow:
            result.append(l.lemmatize(word))
        return ' '.join(result)
         

    def stemText(self, text, intensity):    
        """Apply stemming to a string according to :intesity."""
        #select nltk stemmer
        if intensity is 'light':
            s = stem.PorterStemmer()       
        elif intensity is 'medium':
            s = stem.snowball.EnglishStemmer()   
        elif intensity is 'heavy':
            s = stem.LancasterStemmer()
        else:
            raise Exception("'{0}' is not a correct intensity parameter. Must be light, medium or heavy.".format(intensity))
        bow = text.split(" ")       #this creates a bag of words
        result = []
        for word in bow:
            result.append(s.stem(word))
        return ' '.join(result)


    def cleanText(self, text):
        """
        1. remove the punctuation specified in EXCLUDE 
        2. remove numbers
        3. transform to lowercase
        4. remove multiple spaces
        """
        new_text = ""
        for c in text:
            if c in self.exclude or c.isdigit():
                new_text = new_text + " "
            else:
                new_text = new_text + c
        new_text = new_text.lower()
        return ' '.join(new_text.split())       #this removes double spaces
        
        
    def removeShortWords(self, text, min_word_length):
        """Remove words that are shorter than :min_word_length."""
        bow = text.split(" ")       #this creates a bag of words
        result = []
        for word in bow:
            if len(word)>=min_word_length:
                result.append(word)
        return ' '.join(result)


    def removeStopwords(self, text):
        """Remove the stopwords specified in STOP_WORDS."""
        bow = text.split(" ")       #this creates a bag of words
        result = []
        for word in bow:
            if word not in self.stop_words:
                result.append(word)
        return ' '.join(result)


#if __name__=="__main__":
#    debug()
