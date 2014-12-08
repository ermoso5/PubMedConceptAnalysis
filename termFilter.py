import math
import sqlite3

__author__ = "Zara"

class termFilter(object):

    def createFilteredViewFrom(self, SQL_DB, nodes, weights, k=5):
        self.sql_db = SQL_DB
        self.graph_nodes = nodes
        self.graph_weights = weights
        self.nodeView = "filteredNodeView"

        self.connect()
        c = self.conn.cursor()

        count = c.execute("SELECT count(*) FROM {0}".format(self.graph_nodes))
        total = count.fetchone()[0]
        k_percent = math.ceil(total*k/100)

        #drop the view if exists
        c.execute("DROP VIEW IF EXISTS {}".format(self.nodeView))

        #create view of node frequencies discarding top k% and bottom k%
        c.execute("CREATE VIEW {0} AS SELECT node, sum(weight) as weight FROM ((SELECT node1 as node, sum(weight) as weight FROM {1} GROUP BY node1 UNION SELECT node2 as node, sum(weight) as weight FROM {1} GROUP BY node2)) GROUP BY node ORDER BY weight DESC LIMIT {2}, {3}"
                    .format(self.nodeView, self.graph_weights, k_percent, total-2*k_percent))

        countBefore = c.execute("SELECT COUNT(*) FROM {0}".format(self.graph_weights)).fetchone()[0]

        c.execute("DELETE FROM {0} WHERE NOT EXISTS (select node from {1} where (node= node1 or node=node2))".format(self.graph_weights, self.nodeView))

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
#termFilter().createFilteredViewFrom("test_graph.db", "graph1_nodes", "graph1_weights")
