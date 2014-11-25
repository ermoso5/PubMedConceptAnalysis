import os
import sqlite3


__author__ = ["Marcello Benedetti", "Falitokiniaina Rabearison"]
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
        
        self.dictionary = {}
        self.last_uid = 0
        
        # create tables for nodes, edges and weights if they don't exist
        self.connect() 
        c = self.conn.cursor() 
        result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_nodes,)) 
        
        if len(result.fetchall()) < 1:
            c.execute("CREATE TABLE {0} (id, value, layer)".format(self.graph_nodes)) 
            
            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_edges,)) 
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.graph_edges))
            c.execute("CREATE TABLE {0} (node1, node2)".format(self.graph_edges)) 

            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_weights,))
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.graph_weights))
            c.execute("CREATE TABLE {0} (node1, node2, weight)".format(self.graph_weights))

            self.conn.commit()
       
        else:
            result = c.execute("SELECT value, id FROM {0}".format(self.graph_nodes)) 
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
        
        
    def close(self):
        self.conn.close() 


    def getNewUid(self):
        self.last_uid += 1 
        return self.last_uid


    def addToGraph(self, entities, layer):
        """Add nodes and edges to graph. Entities is a list, layer is a value that is in common among the entities"""            
        # add new words
        count_nodes = self.updateNodes(entities, layer)
        # add new edges
        count_edges = self.updateEdges(entities)
        return count_nodes, count_edges
        
    
    def updateNodes(self, entities, layer):
        """Update in-memory dictionary and database node table with new nodes."""
        c = self.conn.cursor()
        query = "INSERT INTO {0} VALUES (?, ?, ?) ".format(self.graph_nodes)
        row_count = 0
        tuples = []
        for i in range(len(entities)):
            if not self.dictionary.get(entities[i]):
                row_count += 1
                uid = self.getNewUid()                   #assign a new sequential id
                self.dictionary[entities[i]] = uid           #keep it in memory
                tuples.append((uid, entities[i], layer))     #save it to database (id, name, layer)
        c.executemany(query, tuples)
        return row_count    #return number of inserted nodes


    def updateEdges(self, entities):
        """Update edge table with new edges."""
        c = self.conn.cursor()
        query = "INSERT INTO {0} VALUES (?, ?) ".format(self.graph_edges)
        row_count = 0
        tuples = []
        for i in range(0, len(entities)-1):          #create edges among all the entities
            fromUid = self.dictionary.get(entities[i])      #get the first id
            for j in range(i+1, len(entities)):
                toUid = self.dictionary.get(entities[j])
                row_count += 1
                tuples.append((fromUid, toUid)) 
                if DEBUG:
                    print("{0}[{1}] -> {2}[{3}]".format(entities[i], fromUid, entities[j], toUid))
        c.executemany(query, tuples)
        return row_count        #return number of inserted edges


    def compressGraph(self):
        """ Update the weight table and compress the edges."""
        self.connect()
        c = self.conn.cursor()
        tuples = []
        query = "DELETE FROM {0}".format(self.graph_weights)
        c.execute(query)
        query = "SELECT node1, node2, COUNT(*) FROM {0} GROUP BY node1, node2 ".format(self.graph_edges)
        result = c.execute(query)
        for row in result:
            tuples.append(row)
        query = "INSERT INTO {0} VALUES (?,?,?) ".format(self.graph_weights)
        c.executemany(query, tuples)
        self.commit()
        self.close()
        
  
       
    def testGraph(self):
        """Print some rows from the graph table."""
        self.connect()
        c = self.conn.cursor()
        query = "SELECT * FROM {0} LIMIT 20".format(self.graph_nodes)
        result = c.execute(query)
        print("SOME NODES")
        for row in result: 
            print(row)
        print("-" * 80)
        print("SOME EDGES")
        query = "SELECT * FROM {0} LIMIT 20".format(self.graph_edges)
        result = c.execute(query)
        for row in result: 
            print(row)
        print("SOME WEIGHTS")
        query = "SELECT * FROM {0} LIMIT 20".format(self.graph_weights)
        result = c.execute(query)
        for row in result:
            print(row)
        self.close()
                
    

#if __name__=="__main__":
#    debug()
