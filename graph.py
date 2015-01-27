import os
import sqlite3
import math


__author__ = ["Marcello Benedetti", "Zara Alaverdyan"]
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

        #else:
        #    result = c.execute("SELECT term, id FROM {0}".format(self.graph_nodes))
        #    self.dictionary = dict(result.fetchall())
        #    if self.dictionary:
        #        self.last_uid = max(self.dictionary.values())
        #    else:
        #        self.last_uid = 0
        #    print("last assigned Unique Identifier: {0}".format(self.last_uid))

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
        try:
            result = c.execute(query).fetchall()
        except:
            print("Query error!")
            return []
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


    def finalize(self, filter_top):
        """ Aggregate info into weight table and time series table."""
        self.finalizeWeights()
        print("> nodes finalized")
        
        self.finalizeTimeSeries()
        print("> time series finalized")
        
        self.connect()
        c = self.cursor()
        query = "SELECT node1, SUM(weight) w FROM {0} GROUP BY node1 ORDER BY w DESC LIMIT 0, {1} "\
                .format(self.graph_weights, filter_top)
        delete_nodes = [x[0] for x in c.execute(query).fetchall()]
        query = "SELECT tmp.node1 FROM ( SELECT node1, SUM(weight) w FROM {0} GROUP BY node1 ) tmp WHERE tmp.w<2 "\
                .format(self.graph_weights)
        delete_nodes = delete_nodes + [x[0] for x in c.execute(query).fetchall()]
        print("> irrelevant nodes selected")
        
        i = 0                
        for dn in delete_nodes:
            c.execute("DELETE FROM {0} WHERE node1={1}".format(self.graph_weights, dn))
            c.execute("DELETE FROM {0} WHERE node2={1}".format(self.graph_weights, dn))
            c.execute("DELETE FROM {0} WHERE id={1}".format(self.time_series, dn))
            i+=0
            if i % 1000 == 0:
                self.commit()
        self.commit()
        self.close()
        print("> filters applied")
      

     
    def finalizeWeights(self):
        self.connect()
        c = self.cursor()
        
        query = "DELETE FROM {0}".format(self.graph_weights)
        c.execute(query)
        self.commit() 
        
        query = "DROP INDEX IF EXISTS index_weights"
        c.execute(query)       
        self.commit() 
        
        query = """SELECT a, b, SUM(s) weight FROM ( 
                   SELECT node1 a, node2 b, COUNT() s FROM {0} GROUP BY a, b 
                   UNION SELECT node2 a, node1 b, COUNT() s FROM {0} GROUP BY a, b )
                   GROUP BY a, b """.format(self.graph_edges)
        result = c.execute(query).fetchall()
        i = 0
        for row in result:
            c.execute("INSERT INTO {0} VALUES (?,?,?) ".format(self.graph_weights), row)
            i+=1
            if i % 1000 == 0:
                self.commit()
        self.commit()
        c.execute("CREATE INDEX index_weights ON {0}(node1) ".format(self.graph_weights))
        self.commit()
        self.close()

    
    def finalizeTimeSeries(self):
        self.connect()
        c = self.cursor()
       
        query = "DELETE FROM {0}".format(self.time_series)
        c.execute(query)
        self.commit()
        
        query = "DROP INDEX IF EXISTS index_timeseries"
        c.execute(query)       
        self.commit() 
               
        query = "SELECT id, year, COUNT() FROM {0} GROUP BY id, year"\
                .format(self.temp_time_series)
        result = c.execute(query).fetchall()
        i = 0
        for row in result:
            c.execute("INSERT INTO {0} VALUES (?,?,?) ".format(self.time_series), row)
            i+=1
            if i % 1000 == 0:
                self.commit()
        self.commit()
        c.execute("CREATE INDEX index_timeseries ON {0}(id) ".format(self.time_series))
        self.commit()
        self.close()
        

    
    def normalizeWeights(self):
        self.connect()
        c = self.cursor()
        query = "DELETE FROM {0}".format(self.bigraph_norm)
        c.execute(query)
        self.commit()
        edge = c.execute("""SELECT a.node1, a.node2, a.weight*1.0/b.w 
                            FROM {0} a, 
                                 ( SELECT node1, sum(weight) w FROM {0} GROUP BY node1 ) b
                            WHERE a.node1=b.node1 AND b.w BETWEEN 5 AND 500 """.format(self.graph_weights)).fetchone()
        tuples = [] 
        while edge is not None:
            tuples.append(edge)
            edge = c.fetchone()
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

