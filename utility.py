__author__ = 'Nishara'

import sqlite3
import matplotlib.pyplot as plt

SQL_DB = "test_graph.db"


class Utility(object):

    def connect(self):
        self.conn = sqlite3.connect(SQL_DB)

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def select_query(self, query):
        self.connect()
        c = self.cursor()
        result = c.execute(query).fetchall()
        self.close()
        return result

    def update_query(self, query):
        self.connect()
        c = self.cursor()
        c.execute(query)
        self.commit()
        self.close()

    def plot_graph(self, result, concept):
        if len(result) > 0:
            plt.plot([i[0] for i in result], [i[1] for i in result], 'r-o', linewidth=1.0, label=concept)
            plt.legend()
            plt.show()

    def column_exists(self, table_name, column):
        exists = False
        all_columns = "PRAGMA table_info({0})".format(table_name)
        conn = sqlite3.connect('test_graph.db')
        c = conn.cursor()
        result = c.execute(all_columns).fetchall()
        conn.close()
        for col in result:
            if col == column:
                exists = True
        return exists

    def create_column(self, table, column, data_type):
        if not self.column_exists(table, column):
            query = "ALTER TABLE {0} ADD COLUMN {1} {2}".format(table, column, data_type)
            self.update_query(query)