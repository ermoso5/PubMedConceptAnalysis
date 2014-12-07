import math
import sqlite3

__author__ = "Zara"

class termFilter(object):

    def createFilteredViewFrom(self, SQL_DB, nodes, weights, k=5): #graph1_weights
        self.sql_db = SQL_DB
        self.graph_nodes = nodes
        self.graph_weights = weights
        self.nodeView = "filteredNodesView"

        self.connect()
        c = self.conn.cursor()

        count = c.execute("SELECT count(*) FROM {0}".format(self.graph_nodes))
        total = count.fetchone()[0]
        k_percent = math.ceil(total*k/100)

        #drop the view if exists
        c.execute("DROP VIEW IF EXISTS {}".format(self.nodeView))

        #create view from the table discarding top k% and bottom k%
        c.execute("CREATE VIEW {3} AS SELECT id, term, year FROM {0} LIMIT {1}, {2}".format(self.graph_nodes, k_percent, total-2*k_percent, self.nodeView ))

        countBefore = c.execute("SELECT COUNT(*) FROM {0}".format(self.graph_weights)).fetchone()[0]

        c.execute("DELETE FROM {0} WHERE EXISTS (select id from {1} where (id= node1 or id=node2))".format(self.graph_weights, self.nodeView))

        countAfter = c.execute("SELECT COUNT(*) FROM {0}".format(self.graph_weights)).fetchone()[0]

        self.close()
        print(str(k_percent) + " nodes were deleted")
        print(str(countBefore-countAfter) + " edges were deleted")


    def connect(self):
        self.conn = sqlite3.connect(self.sql_db)


    def commit(self):
        self.conn.commit()


    def close(self):
        self.conn.close()

#usage
#termFilter().createFilteredViewFrom("test_graph.db", "graph1_weights")
