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
        self.dictionary = {}

        conn = sqlite3.connect(self.sql_db)
        c = conn.cursor()        
        
        # create tables for nodes and edges if they don't exist
        result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_nodes,))  
        if len(result.fetchall()) < 1:
            c.execute("CREATE TABLE {0} (value, layer)".format(self.graph_nodes))       #id??
            
            result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.graph_edges,))  
            if len(result.fetchall()) > 0:
                c.execute("DROP TABLE {0}".format(self.graph_edges))
                
            c.execute("CREATE TABLE {0} (node1, node2)".format(self.graph_edges))       #weights??
            conn.commit()
       
        else:
            result = c.execute("SELECT * FROM {0}".format(self.graph_nodes))  
            self.dictionary = dict(result.fetchall())
            
        conn.close()   


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
        conn = sqlite3.connect(self.sql_db)
        c = conn.cursor()
        query = "INSERT INTO {0} VALUES (?, ?) ".format(self.graph_nodes)
        row_count = 0
        tuples = []
        for i in range(len(bow)):
            if bow[i] not in self.dictionary.keys():
                row_count += 1
                self.dictionary[bow[i]] = layer
                tuples.append((bow[i], layer))      #id??
        c.executemany(query, tuples)
        conn.commit()
        conn.close()
        if DEBUG:
            print("Added {0} nodes to {1} ".format(row_count, self.graph_nodes))
        return row_count    #return number of inserted nodes


    def updateEdges(self, bow):
        """Update edge table with new edges."""
        conn = sqlite3.connect(self.sql_db)
        c = conn.cursor()
        query = "INSERT INTO {0} VALUES (?, ?) ".format(self.graph_edges)
        row_count = 0
        tuples = []
        for i in range(0, len(bow)-1):          #create edges among all the words in the file
            for j in range(i+1, len(bow)):
                row_count += 1
                tuples.append((bow[i], bow[j]))
        c.executemany(query, tuples)                #weight??
        conn.commit()
        conn.close()
        if DEBUG:
            print("Added {0} edges to {1} ".format(row_count, self.graph_edges))
        return row_count        #return number of inserted edges
   
       
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
        conn.close()
                
    
if __name__=="__main__":
    g = graph()
    g.addToGraph()
    g.testGraph()
