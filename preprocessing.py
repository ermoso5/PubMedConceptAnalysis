"""
TODO: Docstring
"""

import os
import time

from nltk import stem


__author__ = "Marcello Bendetti"
__status__ = "Prototype"


###
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

#currently prefixes are not removed 
PREFIXES = ['von', 'de', 'vant', 'van', 'der', 'vom', 'vander', 'zur',
'ten', 'la', 'du', 'ter', 'dos', 'al', 'del', 'st', 'le', 'dos', 'da', 
'do', 'mc', 'des', 'den', 'di', 'abu', 'vander', 'den', 'della', 'vande', 
'dit', 'bin', 'ibn', 'el', 'los', 'dello', 'vanden', 'ap', 'las', 'delli', 
'mac', 'mrs', 'mr', 'miss', 'jr', 'sr', 'II', 'III', 'IV', 'in']

DEBUG = False

###
def preprocessing(root="corpus", target="processed", stemming=True, min_word_length=1):

    if not os.path.isdir(root):
        raise Exception("'{0}' folder doesn't exist".format(root))

    if not os.path.isdir(target):
        os.mkdir(target)

    for dir in os.listdir(root):
        dir_origin = os.path.join(root, dir)
        if os.path.isdir(dir_origin):
        
            dir_dest = os.path.join(target, dir)
            if not os.path.isdir(dir_dest):
                os.mkdir(dir_dest)
   
            for file in os.listdir(dir_origin):
                
                if file.endswith(".txt"):
                    
                    #read a txt file from the current directory 
                    text = fileToString(os.path.join(dir_origin, file))
                    
                    #to lower case
                    text = text.lower()
                    
                    #remove the punctuation
                    text = removePunctuation(text)
                    
                    #perform medium stemming
                    if stemming:
                        text = stemText(text, intensity='medium')
                    
                    #remove the stopwords
                    text = removeStopwords(text)
                    
                    #remove trailing spaces
                    text = text.strip()
    
                    #debug
                    if DEBUG:
                        print(text)
                    
                    #save to file with the same name and path but in taget directory
                    stringToFile(os.path.join(dir_dest, file), text)
   
                    
###
def fileToString(file_path):
    text = ""
    if file_path:
        with open(file_path, "r") as f:
            text = f.read() #omit size to read all
    return text
 
 
###
def stringToFile(file_path, text):
    if file_path and text:
        with open(file_path, "w") as text_file:
            text_file.write(text)


###
def removePunctuation(text):
    new_text = ""
    for c in text:
        if c in EXCLUDE:
            new_text = new_text + " "
        else:
            new_text = new_text + c
    
    return ' '.join(new_text.split())   #remove double spaces
    

###
def stemText(text, intensity='medium'):
    #select stemmer
    if intensity is 'light':
        s = stem.PorterStemmer()       
    elif intensity is 'medium':
        s = stem.snowball.EnglishStemmer()   
    elif intensity is 'heavy':
        s = stem.LancasterStemmer()
    else:
        return text
    
    #bag of words
    bow = text.split(" ")
    
    #stemming
    result = []
    for word in bow:
        result.append(s.stem(word))

    return ' '.join(result)


###
def removeStopwords(text, min_word_length=1):
    #bag of words
    bow = text.split(" ")
    
    #remove stop words and short words
    result = []
    for word in bow:
        if len(word)>=min_word_length and word not in STOP_WORDS:
            result.append(word)
        
    return ' '.join(result)
    
    
###
if __name__=="__main__":
    preprocessing()
