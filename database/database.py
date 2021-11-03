import os
import json
import pandas as pd
import psycopg2
import psycopg2.extras as extras


class Database:   
    connection = psycopg2.connect(
    host=os.environ.get("host"),
    user=os.environ.get("user"),
    port=os.environ.get("port"),
    database=os.environ.get("database"),
    password=os.environ.get("password"))
    connection.autocommit = True
    cursor = connection.cursor()
  
    def setup_table(self):
        input_and_output_table_query = """ CREATE TABLE IF NOT EXISTS PricePredictions(id SERIAL PRIMARY KEY, 
                                neighbourhood TEXT,Area FLOAT, Number_of_rooms INTEGER,
                                Build_year TEXT, Floor INTEGER, Nearest_educational_institution FLOAT,
                                Nearest_shop FLOAT,Public_transport_stop FLOAT,Heating_system TEXT,
                                energy_class TEXT,Building_type TEXT,No_of_floors INTEGER,
                                Predicted_Price FLOAT)"""
        try:
            self.cursor.execute(input_and_output_table_query)
            print("Prediction table successfully created in database")
        
        except Exception as error:
            raise error
    def add_prediction_result_to_database(self, df: pd.DataFrame) -> None:
        
        """
        Adds  predictions to the database
        :return: None
        """
       
        try:
            tuples = [tuple(x) for x in df.to_numpy()]
            cols = ','.join(list(df.columns))
            query = "INSERT INTO %s(%s) VALUES(%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s,%%s, %%s, %%s, %%s, %%s)" % ('predictions', cols)
            extras.execute_batch(self.cursor, query, tuples, len(df))
            print("Record successfully added to Price Predictions table in database")
        except  Exception as error:
        
            raise error  
          
    def extract_predictions_from_database(self):
        
        """
        Gets the last 10 predictions from the database
        :return: List of tuples containing the last 10 predictions.
        """
        extract_output_and_input_query ="SELECT * FROM predictions ORDER BY id DESC LIMIT 10"
        try:
            self.cursor.execute(extract_output_and_input_query)
            return self.cursor.fetchall()
        except Exception as error:
            raise error   
        