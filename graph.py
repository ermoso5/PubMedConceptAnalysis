from encodings.punycode import selective_find
import os
import sqlite3


__author__ = "Marcello Bendetti"
__status__ = "Prototype"


DEBUG = False
SQL_DB = "test_graph.db"


class Graph(object):

    def __init__(self, graph_name):
        """Checks if the graph exists. If not it creates one."""
        self.sql_db = SQL_DB
        self.graph_nodes = graph_name + "_nodes"
        self.graph_edges = graph_name + "_edges"
        self.graph_weights = graph_name + "_weight"
        self.dictionary = {}
        self.last_uid = 0
        self.connect()       
        
        # create tables for nodes and edges if they don't exist
        c = self.conn.cursor() 
        result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_nodes,))  
        if len(result.fetchall()) < 1:
            c.execute("CREATE TABLE {0} (id, value, layer)".format(self.graph_nodes))       #id??
            
            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_edges,))  
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.graph_edges))
            c.execute("CREATE TABLE {0} (node1, node2)".format(self.graph_edges))       #weights??

            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_weights,))
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.graph_weights))
            c.execute("CREATE TABLE {0} (node1, node2, weight)".format(self.graph_weights))       #weights??

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

    def makeFromFolder(self, root):
        if not os.path.isdir(root):
            raise Exception("'{0}' folder doesn't exist".format(root))
        
        print("...building the graph")
        count_nodes = 0 
        count_edges = 0
        
        for dir in os.listdir(root):                #visit year subdirectories of 'root' folder
            dir_origin = os.path.join(root, dir)
            
            if os.path.isdir(dir_origin):
                layer = dir                         #create a layer for each year

                for file in os.listdir(dir_origin):        #open textual files under year folder and add to graph
                    if file.endswith(".txt"):
                        file_path = os.path.join(dir_origin, file)
                        with open(file_path) as f:
                            text = f.read()
                            f.close()
                        cn, ce = self.addToGraph(text, layer)
                        count_nodes += cn
                        count_edges += ce
                        
        print("added {0} nodes to {1} ".format(count_nodes, self.graph_nodes))
        print("added {0} edges to {1} ".format(count_edges, self.graph_edges))
                    

    def addToGraph(self, text, layer):
        """Add nodes and edges to graph."""
        # bag of words
        bow = text.split(" ")      
        # add new words
        count_nodes = self.updateNodes(bow, layer)
        # add new edges
        count_edges = self.updateEdges(bow)
        return count_nodes, count_edges
        
    
    def updateNodes(self, bow, layer):
        """Update in-memory dictionary and database node table with new nodes."""
        c = self.conn.cursor()
        query = "INSERT INTO {0} VALUES (?, ?, ?) ".format(self.graph_nodes)
        row_count = 0
        tuples = []
        for i in range(len(bow)):
            if not self.dictionary.get(bow[i]):
                row_count += 1
                uid = self.getNewUid()                   #assign a new sequential id
                self.dictionary[bow[i]] = uid           #keep it in memory
                tuples.append((uid, bow[i], layer))     #save it to database (id, name, layer)
        c.executemany(query, tuples)
        return row_count    #return number of inserted nodes


    def updateEdges(self, bow):
        """Update edge table with new edges."""
        c = self.conn.cursor()
        query = "INSERT INTO {0} VALUES (?, ?) ".format(self.graph_edges)
        row_count = 0
        tuples = []
        for i in range(0, len(bow)-1):          #create edges among all the words in the file
            fromUid = self.dictionary.get(bow[i])      #get the first id
            for j in range(i+1, len(bow)):
                toUid = self.dictionary.get(bow[j])
                row_count += 1
                tuples.append((fromUid, toUid))           #(bow[i], bow[j]))
                if DEBUG:
                    print("{0}[{1}] -> {2}[{3}]".format(bow[i], fromUid, bow[j], toUid))
        c.executemany(query, tuples)            #weight??
        return row_count        #return number of inserted edges

    def updateWeights(self):
        """ update weight table with new weight of the edge."""
        tuples = []
        c = self.conn.cursor()
        query = "DELETE FROM {0}".format(self.graph_weights)
        c.execute(query)
        query = "SELECT node1,node2,COUNT(*) FROM {0} GROUP BY node1,node2".format(self.graph_edges)
        result = c.execute(query)
        for row in result:
            tuples.append(row)
        query = "INSERT INTO {0} VALUES (?,?,?)".format(self.graph_weights)
        c.executemany(query, tuples)
       
    def testGraph(self):
        """Print some rows from the graph table."""
        conn = sqlite3.connect(self.sql_db)
        c = conn.cursor()
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
        print("SOME EDGES WEIGHTS")
        query = "SELECT * FROM {0} LIMIT 20".format(self.graph_weights)
        result = c.execute(query)
        for row in result:
            print(row)
        conn.close()
                
    
if __name__=="__main__":
    g = graph()
    g.addToGraph()
    g.testGraph()
