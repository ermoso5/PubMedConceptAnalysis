__author__ = 'Nishara'

from gensim import models, corpora
from processor import *


num_topics = 5
chunk_size = 10000
passes = 5
threshold = 1/num_topics     # This is yet to decide.

# Uses the same document set for training and testing
class LDA(object):
    def iterator(self):

        processor = Processor()

        # Read the corpus and split it into words - This is used in testing.
        # small_medline_formatted.txt represents a document in one line.
        texts = [[word for word in document.lower().split() if word not in STOP_WORDS] for document in
                 open("small_medline_formatted.txt")]

        # Extract the MEDTERMS for lda model training
        med_terms = [[word.split() for word in
                     processor.processString(string=document, ner=True, lemmatize=True, stemming=None,
                                             min_word_length=5)] for document in
                    open("small_medline_formatted.txt")]

        # Flatten the nested list
        all_tokens_1 = sum(med_terms, [])
        all_tokens_2 = sum(all_tokens_1, [])

        # Remove words that appear only once - Should think about this again.....
        tokens_once = list(set(word for word in set(all_tokens_2) if all_tokens_2.count(word) == 1))
        processed_texts = [[word for word in text if word not in tokens_once] for text in med_terms]
        processed_texts = sum(processed_texts, [])

        # Create Dictionary (id->word)
        dictionary = corpora.Dictionary(processed_texts)

        # Creates the Bag of Word corpus
        corpus = [dictionary.doc2bow(text) for text in texts]

        # Trains the LDA model
        # chunksize = update the model once every chunksize
        # passes = how many passes over the document set(given corpus)
        lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, update_every=1,
                               chunksize=chunk_size, passes=passes)
        # Print the topics
        self.topic_models(lda)

        # Assign the topics to the documents in corpus
        self.clusters(dictionary, lda)

    def clusters(self, dictionary, lda_model):
        i = 0
        for document in open("small_medline_formatted.txt"):
            i += 1
            vec = dictionary.doc2bow(document.split())
            topics = lda_model[vec]
            for t in topics:
                print("doc_", i, t)

    def topic_models(self, lda_model):
        for top in lda_model.print_topics():
            print(top)
            print()


if __name__ == "__main__":
    LDA().iterator()