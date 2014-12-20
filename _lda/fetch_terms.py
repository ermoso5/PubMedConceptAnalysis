__author__ = 'Nishara'

import re
import utility

SQL_DB = "test_graph.db"
graph_node = "graph1_nodes"

utils = utility.Utility()


class FetchTerms(object):

    def get_concepts_by_year(self, year):
        query = "SELECT term FROM {0} WHERE year={1}".format(graph_node, year)
        result = utils.select_query(query)
        return result

    def get_distinct_years(self):
        query = "SELECT DISTINCT year FROM {0}".format(graph_node)
        result = utils.select_query(query)
        a = ''.join(re.split(r"[(),']", str(result)))
        return a.strip('[]').split()

    def fetch_all_medterms(self):
        query = "SELECT term FROM {0}".format(graph_node)
        result = utils.select_query(query)
        return result

    def db_update_with_clusters(self, query):
        utils.update_query(query)

    def fetch_time_series(self, term, concept):
        select_query = "SELECT year, probability from {0} WHERE term = '{1}' and cluster = {2}".format(graph_node, term,
                                                                                                       concept)
        result = utils.select_query(select_query)
        utils.plot_graph(result, concept)

# if __name__ == "__main__":
    # FetchTerms().get_distinct_years()
    # FetchTerms().get_concepts_by_year(year=1985)