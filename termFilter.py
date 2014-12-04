import math
import sqlite3

__author__ = "Zara"

class termFilter(object):

    def createFilteredViewFrom(self, SQL_DB, tableName, k=5): #graph1_weights
        self.sql_db = SQL_DB
        self.graph_weights = tableName

        self.connect()
        c = self.conn.cursor()

        count = c.execute("SELECT count(*) FROM {0}".format("graph1_weights"))
        total = count.fetchone()[0]
        k_percent = math.ceil(total*k/100)

        #drop the view if exists
        c.execute("DROP VIEW IF EXISTS filteredWeightsView")

        #create view from the table dsicarding top k% and bottom k%
        c.execute("CREATE VIEW filteredWeightsView AS SELECT node1, node2, weight FROM {0} LIMIT {1}, {2}".format(self.graph_weights, k_percent, total-2*k_percent ))

        self.close()
        return "filteredWeightsView"


    def connect(self):
        self.conn = sqlite3.connect(self.sql_db)


    def commit(self):
        self.conn.commit()


    def close(self):
        self.conn.close()

#usage
#termFilter().createFilteredViewFrom("test_graph.db", "graph1_weights")