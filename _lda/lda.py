__author__ = 'Nishara'

from gensim import models, corpora  # http://radimrehurek.com/gensim/models/ldamodel.html
from processor import *
from _lda.fetch_terms import FetchTerms


num_topics = 5
chunk_size = 10000
passes = 5
num_words_per_topic = 30

SQL_DB = "test_graph.db"
graph_node = "graph1_nodes"

train_lda_model = False
test_lda_model = True
update_clusters = False
processor = Processor()
fetch_terms = FetchTerms()


class LDA(object):
    def iterator(self):

        if train_lda_model:  # To train the model if lda.model does not exist in the directory.
            # Extract the medterms from from each document in the corpus. Calling NER again to get the frequency of
            # each term in each doc. Have to find an easy method for this using the medterms already stored in the DB
            texts = [[word for word in processor.processString(string=document, ner=True, lemmatize=True, stemming=None,
                                                               min_word_length=1)] for document in
                     open("small_medline_formatted.txt")]


            # Fetch distinct medterms from DB
            medterm_tuples = FetchTerms().fetch_all_medterms()
            # list_medterms = [element for tuple in medterm_tuples for element in tuple]


            # texts_1 = [[any(word in document.lower() for word in listt)] for document in open("small_medline_formatted.txt")]

            # Create Dictionary (id->word). # Better to save the dictionary.
            dictionary = corpora.Dictionary(list(medterm_tuples))
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
            # self.topic_models(lda)

            # Assign the topics to the documents in corpus
            # self.cluster_new_corpus()

    # Print the topics
    def topic_models(self, lda_model):
        for top in lda_model.print_topics(num_words=num_words_per_topic):
            print(top)
            print()

    # Cluster a new dataset called "testset.txt" using the trained lda model
    def cluster_new_corpus(self):
        lda_model = models.LdaModel.load('lda.model')
        dictionary = corpora.Dictionary.load('dictionary.dict')
        i = 0
        for document in open("testset.txt"):
            i += 1
            vec = dictionary.doc2bow(document.split())
            topics = lda_model[vec]
            print("doc_", i, max(topics, key=lambda sim: sim[1]))

    # Assign each medical term appeared in each year to a cluster with the highest probability.
    def cluster_by_years(self):
        if update_clusters:
            years = fetch_terms.get_distinct_years()
            for year in years:
                med_line = fetch_terms.get_concepts_by_year(year=year)
                print(med_line)
                lda = models.LdaModel.load('lda.model')
                dictionary = corpora.Dictionary.load('dictionary.dict')
                for document in med_line:
                    doc2word = dictionary.doc2bow(document[0].split())
                    topics = lda[doc2word]
                    top = max(topics, key=lambda sim: sim[1])
                    update_query = "UPDATE {0} SET cluster = {1}, probability = {2} WHERE year = {3} and term = '{4}'".format(
                        graph_node, top[0],
                        top[1], year, str(document[0]))
                    fetch_terms.db_update_with_clusters(update_query)


if __name__ == "__main__":
    LDA().iterator()
    LDA().cluster_by_years()
    FetchTerms().fetch_time_series('chronic', 1)
    # LDA().check_column_exists(graph_node, 'cluster')
