"""This script is only for this database."""

import os
import sqlite3

import pandas as pd
import json

from ContentBasedRS.Utils import *


# ----------------------------------------helper functions--------------------------------------------------------------


class ContentDB:

    def __init__(self):
        self.MAIN_TABLE_NAME = 'paper'
        self.TEMP_TABLE_NAME = 'tempTable'
        self.OPENAI_EMBEDDING_TABLE_NAME = "openAI"

        self.EMBEDDING_TABLE = self.OPENAI_EMBEDDING_TABLE_NAME  # a mapping from paper id to embedding
        self.embed_long_text = OpenAIEmbedding.embed_long_text
        self.embed_short_text = OpenAIEmbedding.embed_short_text

        # column names for the main table
        self.COL_PAPER_ID = 'paperId'
        self.COL_TITLE = 'title'
        self.COL_ABSTRACT = 'abstract'
        self.COL_YEAR = 'year'
        self.COL_REF_COUNT = 'referenceCount'
        self.COL_CITE_COUNT = 'citationCount'
        self.COL_INFLUENTIAL_CITE_COUNT = 'influentialCitationCount'
        self.COL_AUTHORS = 'authors'
        self.COL_REFERENCE = 'references'  # cannot name it references
        self.COL_EMBEDDING = 'embedding'

        # the order of columns
        self.columns = [self.COL_PAPER_ID, self.COL_TITLE, self.COL_ABSTRACT,
                        self.COL_YEAR, self.COL_REF_COUNT, self.COL_CITE_COUNT, self.COL_INFLUENTIAL_CITE_COUNT,
                        self.COL_AUTHORS, self.COL_REFERENCE, self.COL_EMBEDDING]

        self.ATTR_AUTHORS_ID = 'authorId'
        self.ATTR_AUTHORS_NAME = 'name'

        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.my_database = os.path.join(current_dir, '../Content.db')
        self.open_connection()

    def __del__(self):
        self.commit_change()
        self.close_connection()

    def get_col_index(self, col_name):
        """assume col_name is legit, else will raise ValueError"""
        return self.columns.index(col_name)

    def commit_change(self):
        # Commit the changes to the database
        self.conn.commit()
        print("content database committed changes")

    def open_connection(self):
        self.conn = sqlite3.connect(self.my_database)
        self.cursor = self.conn.cursor()
        print("content database established connection!")

    def close_connection(self):
        # Close the cursor and the database connection
        self.cursor.close()
        self.conn.close()
        print("content database closed connection")

    def query_database(self, query):
        """
        Note: if input is wrong, will throw exception, if query for empty set, will return empty list.
        return a iterator of queried result, and the column number
        """
        self.cursor.execute(query)
        result, columns = self.cursor.fetchall(), [column[0] for column in self.cursor.description]
        final_result = pd.DataFrame(result, columns=columns)
        final_result = final_result.apply(self._decode, axis=1)
        return final_result

    def _decode(self, row):
        if self.COL_AUTHORS in row:
            row[self.COL_AUTHORS] = BLOB_to_info(row[self.COL_AUTHORS])
        if self.COL_REFERENCE in row:
            row[self.COL_REFERENCE] = BLOB_to_info(row[self.COL_REFERENCE])
        return row

    # ----------------------------------------initialize functions------------------------------------------------------

    def create_main_table(self):
        """
        create a database named MY_DATABASE if not exist,
        create a table named TABLE_MAIN in the database
        """

        # if the table already exists then we will drop it. Caution: if accidentally call this function might delete
        # important details
        query = f'''DROP TABLE IF EXISTS {self.MAIN_TABLE_NAME};'''
        self.cursor.execute(query)

        # Define the SQL query to create the table: note "references is a keyword in sqlite, so use quotation mark
        query = f'''
                CREATE TABLE {self.MAIN_TABLE_NAME} (
                {self.COL_PAPER_ID} TEXT PRIMARY KEY,
                {self.COL_TITLE} TEXT,
                {self.COL_ABSTRACT} TEXT,
                {self.COL_YEAR} INTEGER,
                {self.COL_REF_COUNT} INTEGER,
                {self.COL_CITE_COUNT} INTEGER,
                {self.COL_INFLUENTIAL_CITE_COUNT} INTEGER,
                {self.COL_AUTHORS} BLOB,
                "{self.COL_REFERENCE}" BLOB
                )
                '''

        # Execute the SQL query to create the table
        self.cursor.execute(query)

    # -----------------------------------------------API functions------------------------------------------------------
    def add_papers_to_db(self, raw_source_dir):
        for filename in os.listdir(raw_source_dir):
            with open(os.path.join(raw_source_dir, filename), 'r') as papers_file:
                data = json.load(papers_file)
            papers_df = pd.DataFrame.from_records(data)

            # convert arrays to binary large object because that what sqlite have...
            papers_df[self.COL_REFERENCE] = papers_df[self.COL_REFERENCE].apply(info_to_BLOB)
            papers_df[self.COL_AUTHORS] = papers_df[self.COL_AUTHORS].apply(info_to_BLOB)
            papers_df.set_index(self.COL_PAPER_ID, inplace=True)
            # output directly from pandas to database
            papers_df.to_sql(self.TEMP_TABLE_NAME, self.conn, if_exists='replace')  # handling replicate

            self.cursor.execute(f"SELECT * FROM {self.TEMP_TABLE_NAME}")
            self.cursor.execute(f"INSERT OR IGNORE INTO {self.MAIN_TABLE_NAME} SELECT * FROM {self.TEMP_TABLE_NAME}")
            print(f"{filename} successfully added to content database!")

    def for_each_row_do(self, callback, args, table='paper'):
        """
        the callback's first parameter is row
        the the call back's second parameter is a list of arguments, can be empty list
        """
        query = f'select * from {table}'
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        counter = 0
        while row is not None:
            callback(row, args)
            row = self.cursor.fetchone()
            counter += 1

    def get_papers_by_id_set(self, id_set):
        id_set = {"\"" + paper_id + "\"" for paper_id in id_set}
        id_string = ",".join(id_set)
        query = f"""SELECT * FROM {self.MAIN_TABLE_NAME} 
                    WHERE {self.COL_PAPER_ID} in ({id_string})
                """
        known_papers_df = self.query_database(query)
        return known_papers_df

    def get_row_by_id(self, paper_id):
        result = self.query_database(
            f"select * from {self.MAIN_TABLE_NAME} where {self.COL_PAPER_ID} = {paper_id}")
        if result.empty:
            raise ValueError("This author doesn't exist!")
        return result
