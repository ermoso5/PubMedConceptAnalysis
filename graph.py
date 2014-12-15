import os
import sqlite3
import math


__author__ = ["Marcello Benedetti", "Zara Alaverdyan", "Falitokiniaina Rabearison"]
__status__ = "Prototype"

DEBUG = False
SQL_DB = "test_graph.db"


class Graph(object):
    def __init__(self, graph_name):
        """Checks if the graph exists. If not it creates one."""
        self.sql_db = SQL_DB
        self.graph_nodes = graph_name + "_nodes"
        self.graph_edges = graph_name + "_edges"
        self.graph_weights = graph_name + "_weights"
        self.temp_time_series = graph_name + "_temp_time_series"
        self.time_series = graph_name + "_time_series"
        self.filtered_nodes_view = graph_name + "_filtered_nodes_view"
        self.filtered_edges_view = graph_name + "_filtered_edges_view"
        self.bigraph_norm = graph_name + "_bi_norm"

        self.dictionary = {}
        self.last_uid = 0

        # create tables for nodes, edges and weights if they don't exist
        self.connect()
        c = self.cursor()
        result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_nodes,))

        if len(result.fetchall()) < 1:
            c.execute("CREATE TABLE {0} (id, term, year)".format(self.graph_nodes))

            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_edges,))
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.graph_edges))
            c.execute("CREATE TABLE {0} (node1, node2)".format(self.graph_edges))

            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_weights,))
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.graph_weights))
            c.execute("CREATE TABLE {0} (node1, node2, weight)".format(self.graph_weights))

            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.temp_time_series,))
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.temp_time_series))
            c.execute("CREATE TABLE {0} (id, year)".format(self.temp_time_series))

            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.time_series,))
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.time_series))
            c.execute("CREATE TABLE {0} (id, year, frequency)".format(self.time_series))

            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.bigraph_norm,))
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.bigraph_norm))
            c.execute("CREATE TABLE {0} (node1, node2, weight)".format(self.bigraph_norm))

            self.conn.commit()

        else:
            result = c.execute("SELECT term, id FROM {0}".format(self.graph_nodes))
            self.dictionary = dict(result.fetchall())
            if self.dictionary:
                self.last_uid = max(self.dictionary.values())
            else:
                self.last_uid = 0
            print("last assigned Unique Identifier: {0}".format(self.last_uid))

        self.close()


    def connect(self):
        self.conn = sqlite3.connect(self.sql_db)


    def commit(self):
        self.conn.commit()


    def cursor(self):
        return self.conn.cursor()


    def close(self):
        self.conn.close()


    def sendQuery(self, query):
        self.connect()
        c = self.cursor()
        result = c.execute(query).fetchall()
        self.close()
        return result


    def getNewUid(self):
        self.last_uid += 1
        return self.last_uid


    def addToGraph(self, entities, year):
        """Add nodes and edges to graph. Entities is a list, year is an integer."""
        # add new words
        count_nodes = self.updateNodes(entities, year)
        # add new edges
        count_edges = self.updateEdges(entities)
        # add time series
        self.updateTimeSeries(entities, year)
        return count_nodes, count_edges


    def updateNodes(self, entities, year):
        """Update in-memory dictionary and database node table with new nodes."""
        c = self.cursor()
        query = "INSERT INTO {0} VALUES (?, ?, ?) ".format(self.graph_nodes)
        row_count = 0
        tuples = []
        for i in range(len(entities)):
            if not self.dictionary.get(entities[i]):
                row_count += 1
                uid = self.getNewUid()  # assign a new sequential id
                self.dictionary[entities[i]] = uid  # keep it in memory
                tuples.append((uid, entities[i], year))  # save it to database (id, name, year)
        c.executemany(query, tuples)
        return row_count  # return number of inserted nodes


    def updateEdges(self, entities):
        """Update edge table with new edges."""
        c = self.cursor()
        query = "INSERT INTO {0} VALUES (?, ?) ".format(self.graph_edges)
        row_count = 0
        tuples = []
        for i in range(0, len(entities) - 1):  # create edges among all the entities
            fromUid = self.dictionary.get(entities[i])  #get the first id
            for j in range(i + 1, len(entities)):
                toUid = self.dictionary.get(entities[j])
                row_count += 1
                tuples.append((fromUid, toUid))
                if DEBUG:
                    print("{0}[{1}] -> {2}[{3}]".format(entities[i], fromUid, entities[j], toUid))
        c.executemany(query, tuples)
        return row_count  # return number of inserted edges


    def updateTimeSeries(self, entities, year):
        """Update temp time series table."""
        c = self.cursor()
        query = "INSERT INTO {0} VALUES (?, ?) ".format(self.temp_time_series)
        row_count = 0
        tuples = []
        for i in range(len(entities)):
            uid = self.dictionary.get(entities[i])  # get the id
            tuples.append((uid, year))
        c.executemany(query, tuples)
        return row_count  # return number of occurrences


    def compressTables(self):
        """ Aggregate info into weight table and time series table."""
        self.connect()
        c = self.cursor()
        tuples = []
        query = "DELETE FROM {0}".format(self.graph_weights)
        c.execute(query)
        query = "SELECT node1, node2, COUNT() FROM {0} GROUP BY node1, node2 ".format(self.graph_edges)
        result = c.execute(query)
        for row in result:
            tuples.append(row)
        query = "INSERT INTO {0} VALUES (?,?,?) ".format(self.graph_weights)
        c.executemany(query, tuples)
        self.commit()

        tuples = []
        query = "DELETE FROM {0}".format(self.time_series)
        c.execute(query)
        query = "SELECT id, year, COUNT() FROM {0} GROUP BY id, year ".format(self.temp_time_series)
        result = c.execute(query)
        for row in result:
            tuples.append(row)
        query = "INSERT INTO {0} VALUES (?,?,?) ".format(self.time_series)
        c.executemany(query, tuples)
        self.commit()
        
        #c.execute("DROP TABLE {0}".format(self.graph_edges))
        #c.execute("DROP TABLE {0}".format(self.temp_time_series))
        #self.commit()     
        self.close()


    def createFilteredView(self, percentage=5):
        self.connect()
        c = self.cursor()
        
        # drop the view if exists
        c.execute("DROP VIEW IF EXISTS {}".format(self.filtered_nodes_view))
        c.execute("DROP VIEW IF EXISTS {}".format(self.filtered_edges_view))
        self.commit()

        count = c.execute("SELECT count(*) FROM {0}".format(self.graph_nodes))
        total = count.fetchone()[0]
        k_percent = math.ceil(total * percentage / 100)

        #create view of node frequencies discarding top k% and bottom k%
        c.execute(
            "CREATE VIEW {0} AS SELECT node, sum(weight) as weight FROM ((SELECT node1 as node, sum(weight) as weight FROM {1} GROUP BY node1 UNION SELECT node2 as node, sum(weight) as weight FROM {1} GROUP BY node2)) GROUP BY node ORDER BY weight DESC LIMIT {2}, {3}"
            .format(self.filtered_nodes_view, self.graph_weights, k_percent, total - 2* k_percent)) #??????????
        self.commit()

        c.execute(
            "CREATE VIEW {0} AS SELECT n1.node, n2.node, w.weight FROM {1} w JOIN {2} n1 ON w.node1 = n1.node JOIN {2} n2 ON w.node2 = n2.node"
            .format(self.filtered_edges_view, self.graph_weights, self.filtered_nodes_view))
        self.commit()
        ## "CREATE VIEW {0} AS SELECT DISTINCr2 =T * FROM (SELECT n1.node1, n1.node2, w.weight FROM {1} w JOIN {2} n1 ON w.node1 = n1.node UNION SELECT n2.node1, n2.node2, w.weight FROM {1} w JOIN {2} n2 on w.node2 = n2.node)".format(
            
            

        countBefore = c.execute("SELECT COUNT(*) FROM {0}".format(self.graph_weights)).fetchone()[0]
        countAfter = c.execute("SELECT COUNT(*) FROM {0}".format(self.filtered_edges_view)).fetchone()[0]

        self.commit()
        self.close()
        print(str(k_percent) + " nodes are not relevant")
        print(str(countBefore - countAfter) + " edges are not relevant")

    
    def normalizeWeights(self):
        self.connect()
        c = self.cursor()
        result = c.execute("SELECT node, weight FROM {0}".format(self.filtered_nodes_view))
        outweights = dict(result.fetchall())
        edges = c.execute("SELECT * FROM {0}".format(self.filtered_edges_view)).fetchall()
        tuples = [] 
        for edge in edges:
            if edge[0] in outweights and edge[1] in outweights:
                norm_weight1 = edge[2] / float(outweights[edge[0]])
                norm_weight2 = edge[2] / float(outweights[edge[1]])
                tuples.append((edge[0], edge[1], norm_weight1))
                tuples.append((edge[1], edge[0], norm_weight2))
            else:
                print(edge[0], " - ", edge[1])
        query = "INSERT INTO {0} VALUES (?,?,?) ".format(self.bigraph_norm)
        c.executemany(query, tuples)
        self.commit()
        self.close()


    def testGraph(self):
        """Print some rows from the graph table."""
        self.connect()
        c = self.cursor()
        query = "SELECT * FROM {0} LIMIT 20".format(self.graph_nodes)
        result = c.execute(query)
        print("SOME NODES")
        for row in result:
            print(row)
        print("-" * 80)
        print("SOME NORMALIZED WEIGHTS")
        query = "SELECT * FROM {0} LIMIT 20".format(self.bigraph_norm)
        result = c.execute(query)
        for row in result:
            print(row)
        print("-" * 80)
        print("SOME TIME SERIES")
        query = "SELECT * FROM {0} LIMIT 20".format(self.time_series)
        result = c.execute(query)
        for row in result:
            print(row)
        self.close()
        
        
# if __name__=="__main__":
#    debug()
