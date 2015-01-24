__author__ = 'Nishara'

from _lda.lda import LDA

train_lda_model = True
root="../corpus"


def main():
    lda = LDA()

    if train_lda_model:
        lda.train_lda_model(num_topics=5, chunk_size=1000, passes=5, num_words_per_topic=30, root="../corpus")

    lda.cluster_docs_by_year(root)
    lda.plot_concepts(2)

if __name__=="__main__":
    main()