"""
This class provides the preprocessing functions for the PubMed corpus:
    processFolder(root, target, stemming, min_word_length, remove_numbers, remove_duplicates, ner)
    processString(string, stemming, min_word_length, remove_numbers, remove_duplicates, ner)
    
Auxiliary functions are:    
    fileToString(file_path)
    stringToFile(file_path, text)    
    stemText(text, intensity)
    removeShortWords(text, min_word_length)
    removePunctuation(text)
    removeStopwords(text)
    removeDuplicates(text)
    removeNumbers(text)
    ner(string)
"""

import os
import time
import requests
import json

from nltk import stem
from adeptner import Adeptner
from graph import Graph

__author__ = "Marcello Bendetti"
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
     
     
class Preprocessor(object):

    def __init__(self):
        self.exclude = EXCLUDE
        self.stop_words = STOP_WORDS
        self.prefixes = PREFIXES    #currently prefixes are not used
        try:
            self.ner = Adeptner()
            self.ner_mode = 'offline'
        except:
            print("WARNING: you are using an online NER!")
            self.ner_mode = 'online'
            
    
    def processFolder(self, root="corpus", graph=None, target_folder=None, ner=False, stemming='medium', min_word_length=1, remove_numbers=False, remove_duplicates=False):
        """
        Creates a target folder and related subdirectories according to the structure of the root folder. 
        Then, processes all the textual files in the root structure and store the results in the target structure.
        
        :root               The root folder contains years subfolders that in turn contain the '.txt' documents.
        :target             The name of the folder where preprocessed files will be stored. It may not exist.
        :ner                Use named entity recognition.
        :stemming           Choose whether or not applying stemming. It may be None, 'light', 'medium', 'heavy'. 
        :min_word_length    Minimum number of characters for a word to be kept. 
        :remove_numbers     Remove lonely numbers. Keep numbers when together with characters.  
        :remove_duplicates  Remove the duplicates from the text.
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
            
        print("...preprocessing documents")
              
        for dir in os.listdir(root):                #visit year subdirectories of 'root' folder
            layer = dir                             #layer contains the year
            dir_origin = os.path.join(root, dir)
            
            if os.path.isdir(dir_origin):
                if target_folder:
                    dir_dest = os.path.join(target_folder, dir)
                    if not os.path.isdir(dir_dest):             #create year subfolders if they don't exist in 'target' 
                        os.mkdir(dir_dest)
       
                for file in os.listdir(dir_origin):             #open textual files under year folder and process them
                    if file.endswith(".txt"):               
                        string = self.fileToString(os.path.join(dir_origin, file))        #put file into string
                        string = self.processString(string, ner, stemming, min_word_length, remove_numbers, remove_duplicates)
                        
                        if string:
                            if DEBUG:
                                print(string)
                            if graph:                               
                                graph.addToGraph(string, layer)                                #add to graph 
                            if target_folder:
                                self.stringToFile(os.path.join(dir_dest, file), string)           #save string to file otherwise
                     
                graph.commit()
        graph.close()   


    def processString(self, string, ner=False, stemming='medium', min_word_length=1, remove_numbers=False, remove_duplicates=False):
        """ 
        Apply prerpocessing to a string.
        :ner                Use named entity recognition.
        :stemming           Choose whether or not applying stemming. It may be None, 'light', 'medium', 'heavy'. 
        :min_word_length    Minimum number of characters for a word to be kept. 
        :remove_numbers     Remove lonely numbers. Keep numbers when together with characters.  
        :remove_duplicates  Remove the duplicates from the text.
        :return             Cleaned up string
        """
        string = self.removePunctuation(string)                     #remove the punctuation in EXCLUDE
        string = self.removeStopwords(string)                       #remove the stopwords in STOP_WORDS
        if ner:
            string = self.getEntities(string)                       #perform named entity recognition 
        string = string.lower()                                     #convert to lower case                 
        if stemming:
            string = self.stemText(string, intensity=stemming)      #perform stemming
        if min_word_length > 0:
            string = self.removeShortWords(string, min_word_length)  #remove short words
        if remove_duplicates:
            string = self.removeDuplicates(string)                  #remove duplicate words
        if remove_numbers:
            string = self.removeNumbers(string)                     #remove numbers
        string = string.strip()                                     #remove trailing spaces
        return string


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


    def removePunctuation(self, text):
        """Remove the punctuation specified in EXCLUDE from the string."""
        new_text = ""
        for c in text:
            if c in self.exclude:
                new_text = new_text + " "
            else:
                new_text = new_text + c
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
        

    def removeDuplicates(self, text):
        """Remove words that appear more than one."""
        bow = text.split(" ")
        result = set(bow)
        return ' '.join(result)
        

    def removeNumbers(self, text):
        """Remove numbers that appear alone in the text. Keep the numbers inside words."""
        bow = text.split(" ")
        result = [word for word in bow if not word.isdigit()]
        return ' '.join(result)
    
    
    def getEntities(self, text):
        """Apply Named Entity Recognition from Stanford's web service ADEPTA."""
        if self.ner_mode == 'online':
            ADEPT_url="http://dust.stanford.edu:8080/ADEPTRest/rest/annotate"
            payload = {"adeptifyThis" : text}
            r=requests.post(ADEPT_url, data=payload)
            data = json.loads(r.text)
            result = []
            for row in data[0]["tokens"]:
                if row["label"] == "MEDTERM":
                    result.append(row["token"])
                    print(row["token"])
            return ' '.join(result)
        else:
            result = self.ner.getTerms(text).get('MEDTERM')
            if result:
                return ' '.join(result)
            else:
                return ''
            
    
if __name__=="__main__":
    pp = preprossor()
    result = pp.preprocessString("Test string")
    print(result)
