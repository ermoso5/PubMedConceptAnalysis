"""
This module provides the preprocessing function for the PubMed corpus:
    preprocessing(root, target, stemming, min_word_length)

Auxiliary functions are:    
    fileToString(file_path)
    stringToFile(file_path, text)
    removePunctuation(text)
    stemText(text, intensity)
    removeStopwords(text, min_word_length)
"""

import os
import time

from nltk import stem


__author__ = "Marcello Bendetti"
__status__ = "Prototype"


EXCLUDE = ['!', '?', '.', ',', ':', ';', '_', '-', '+', '*', '/', '\\', '^', 
"'", '"', '’' , '(', ')', '[', ']', '=', '°', '|', '{', '}', '\n', '\t',
'%', '¡', '¨', '“', '”', '`', '<', '>', '$', '&', '@', '#', '°']

STOP_WORDS = ['a','able','about','across','after','all','almost','also','am','among',
'an','and','any','are','as','at','be','because','been','but','by','can',
'cannot','could','dear','did','do','does','either','else','ever','every',
'for','from','get','got','had','has','have','he','her','hers','him','his',
'how','however','i','if','in','into','is','it','its','just','least','let',
'like','likely','may','me','might','most','must','my','neither','no','nor',
'not','of','off','often','on','only','or','other','our','own','rather','said',
'say','says','she','should','since','so','some','than','that','the','their',
'them','then','there','these','they','this','those','to','too','thus','us',
'wants','was','we','were','what','when','where','which','while','who',
'whom','why','will','with','would','yet','you','your']

#currently prefixes are not used
PREFIXES = ['von', 'de', 'vant', 'van', 'der', 'vom', 'vander', 'zur',
'ten', 'la', 'du', 'ter', 'dos', 'al', 'del', 'st', 'le', 'dos', 'da', 
'do', 'mc', 'des', 'den', 'di', 'abu', 'vander', 'den', 'della', 'vande', 
'dit', 'bin', 'ibn', 'el', 'los', 'dello', 'vanden', 'ap', 'las', 'delli', 
'mac', 'mrs', 'mr', 'miss', 'jr', 'sr', 'II', 'III', 'IV', 'in']

DEBUG = False


def preprocessing(root="corpus", target="processed", stemming='medium', min_word_length=1):
    """
    Creates a target folder and related subdirectories according to the structure of the root folder. 
    Then, processes all the textual files in the root structure and store the results in the target structure.
    
    :root               The root folder contains years subfolders that in turn contain the '.txt' documents.
    :target             The name of the folder where preprocessed files will be stored. It may not exist.
    :stemming           Choose whether or not applying stemming. It may be None, 'light', 'medium', 'heavy'. 
    :min_word_length    Minimum number of characters for a word to be kept. 
    :return             None
    """
    if not os.path.isdir(root):
        raise Exception("'{0}' folder doesn't exist".format(root))
    
    if not os.path.isdir(target):       #create 'target' folder if it doesn't exist
        os.mkdir(target)
        
    for dir in os.listdir(root):                #visit year subdirectories of 'root' folder
        dir_origin = os.path.join(root, dir)     
        
        if os.path.isdir(dir_origin):
            dir_dest = os.path.join(target, dir)
            if not os.path.isdir(dir_dest):     #create year subfolders if they don't exist in 'target'
                os.mkdir(dir_dest)
   
            for file in os.listdir(dir_origin):     #open textual files under year folder and process them
                if file.endswith(".txt"):               
                    text = fileToString(os.path.join(dir_origin, file))     #put file into string
                    text = text.lower()                                     #convert to lower case
                    text = removePunctuation(text)                          #remove the punctuation in EXCLUDE
                    if stemming:
                        text = stemText(text, intensity=stemming)           #perform stemming
                    text = removeStopwords(text, min_word_length)           #remove the stopwords in STOP_WORDS
                    text = text.strip()                                     #remove trailing spaces
                    if DEBUG:
                        print(text)                                         #display the results
                    stringToFile(os.path.join(dir_dest, file), text)        #save string to file
                    

def fileToString(file_path):
    """Take the content of a file and put it in a string."""
    text = ""
    if file_path:
        with open(file_path, "r") as f:
            text = f.read() #omit size to read all
    return text
 
 
def stringToFile(file_path, text):
    """Take the content of a string and put it in a '.txt' file."""
    if file_path and text:
        with open(file_path, "w") as text_file:
            text_file.write(text)


def removePunctuation(text):
    """Remove the punctuation specified in EXCLUDE from the string."""
    new_text = ""
    for c in text:
        if c in EXCLUDE:
            new_text = new_text + " "
        else:
            new_text = new_text + c
    return ' '.join(new_text.split())       #this removes double spaces
    

def stemText(text, intensity='medium'):    
    """Apply stemming to a string according to :intesity."""
    #select nltk stemmer
    if intensity is 'light':
        s = stem.PorterStemmer()       
    elif intensity is 'medium':
        s = stem.snowball.EnglishStemmer()   
    elif intensity is 'heavy':
        s = stem.LancasterStemmer()
    else:
        return text
    bow = text.split(" ")       #this creates a bag of words
    result = []
    for word in bow:
        result.append(s.stem(word))
    return ' '.join(result)


def removeStopwords(text, min_word_length=1):
    """Remove the stopwords specified in STOP_WORDS and the words shorter than :min_word_length."""
    bow = text.split(" ")       #this creates a bag of words
    result = []
    for word in bow:
        if len(word)>=min_word_length and word not in STOP_WORDS:
            result.append(word)
    return ' '.join(result)
    
    
if __name__=="__main__":
    preprocessing()
