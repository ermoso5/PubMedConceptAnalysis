__author__ = 'Nishara'

from gensim import models, corpora  # http://radimrehurek.com/gensim/models/ldamodel.html
from processor import *
from _lda.fetch_terms import FetchTerms
import ast
import matplotlib.pyplot as plt


processor = Processor()


class LDA(object):
    def train_lda_model(self, num_topics, chunk_size, passes, num_words_per_topic, root):

        # To train the model if lda.model does not exist in the directory.

        # Extract the medterms from from each document in the corpus. Calling NER again to get the frequency of
        # each term in each doc.
        #****
        #**** ADEPT does not return the repetitions of terms
        texts = []
        for dir in os.listdir(root):
            dir_origin = os.path.join(root, dir)
            if os.path.isdir(dir_origin) and dir.isdigit():
                for file in os.listdir(dir_origin):
                    entities = processor.processString(string=self.fileToString(os.path.join(dir_origin, file)),
                                                       ner=True, lemmatize=True, stemming=None, min_word_length=1)
                    texts.append(entities)

        tokens = sum(texts, [])
        processed_texts = [[word for word in text if word in tokens] for text in texts]

        # Fetch distinct medterms from DB
        medterm_tuples = FetchTerms().fetch_all_medterms()

        # Create Dictionary (id->word). # Better to save the dictionary.
        # dictionary = corpora.Dictionary(list(medterm_tuples))       # Use this if the terms are imported from the graph.
        dictionary = corpora.Dictionary(processed_texts)
        dictionary.save('dictionary.dict')
        # Creates the Bag of Word corpus
        corpus = [dictionary.doc2bow(text) for text in texts]
        # corpus = dictionary.doc2bow(corpus)

        # Trains the LDA model
        # chunksize = update the model once every chunksize
        # passes = how many passes over the document set(given corpus)
        lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, update_every=1,
                              chunksize=chunk_size, passes=passes)
        lda.save('lda.model')
        # Print the topics
        # self.topic_models(lda, num_words_per_topic)

    # Print the topics
    def topic_models(self, lda_model, num_words_per_topic):
        for top in lda_model.print_topics(num_words=num_words_per_topic):
            print(top)
            print()

    def cluster_docs_by_year(self, root):
        topic_dictionary = {}

        lda_model = models.LdaModel.load('lda.model')
        dictionary = corpora.Dictionary.load('dictionary.dict')
        i = 0
        if not os.path.isdir(root):
            raise Exception("'{0}' folder doesn't exist".format(root))

        for dir in os.listdir(root):
            dir_origin = os.path.join(root, dir)
            if os.path.isdir(dir_origin) and dir.isdigit():
                year = int(dir)

                for file in os.listdir(dir_origin):
                    entities = processor.processString(string=self.fileToString(os.path.join(dir_origin, file)),
                                                       ner=True, lemmatize=True, stemming=None, min_word_length=1)
                    i += 1
                    vec = dictionary.doc2bow(entities)
                    topics = lda_model[vec]
                    top = max(topics, key=lambda sim: sim[1])[0]
                    # print("doc_", i, max(topics, key=lambda sim: sim[1]))
                    year_dictionary = {}
                    if (top in topic_dictionary.keys()):
                        year_dictionary = topic_dictionary.get(top)
                        if (year in year_dictionary.keys()):
                            year_dictionary[year] += 1
                        else:
                            year_dictionary[year] = 1
                    else:
                        year_dictionary[year] = 1
                        topic_dictionary[top] = year_dictionary

        file = open('output.txt', 'w')
        for topic in topic_dictionary.keys():
            s = "{0} -> {1}\n".format(topic, topic_dictionary.get(topic))
            file.write(s)


    def fileToString(self, file_path):
        """Take the content of a file and put it in a string."""
        text = ""
        if file_path:
            with open(file_path, "r") as f:
                text = f.read()
                f.close()
        return text

    def plot_concepts(self, concept):
        result = self.reading(concept)
        if len(result) > 0:
            plt.plot([i for i in result.keys()], [v for v in result.values()], 'r-o', linewidth=1.0, label=concept)
            plt.legend()
            plt.show()


    def reading(self, concept):
        with open('output.txt', 'r') as file:
            for line in file:
                line1 = line.split("->")[0]
                line2 = line.split("->")[1].rstrip('\n')
                if line1.startswith(str(concept)):
                    return eval(line2)
