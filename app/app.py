
import sys
sys.path.insert(0, 'C:\\Users\\USER\\Projects\\Lithuanian-house-price-prediction')
from database.database import Database
from flask import Flask
from flask import request
import json
from model.process_input import process_input
import pickle

database = Database()
saved_model_path ="C:\\Users\\USER\\Projects\\Lithuanian-house-price-prediction\\model\\model.pkl"
with open(saved_model_path, "rb") as file:
    model = pickle.load(file)
    
app = Flask(__name__)

@app.route('/')
def home()-> str:
    return "This is a price prediction"
      
@app.route("/predict", methods=["POST"])
def predict() -> str:
    '''
    loads the data acquired from request to the model and returns the predicted value
    :return: prediction
    '''
    try:
        input_params = process_input(request.data)
        predictions = model.predict(input_params)
        input_params["price_per_month"] = predictions
        database.add_prediction_result_to_database(input_params)
        return json.dumps({"predicted price": predictions.tolist()}),200
    except (KeyError, json.JSONDecodeError, AssertionError):
        return json.dumps({"error": "CHECK INPUT"}), 400
    except Exception as error:
        print(error)
        return json.dumps({"error": "PREDICTION FAILED"}), 500

@app.route("/recent_predictions", methods=["GET"])
def recent_predictions():
    """
        fetches recently predicted details available in the database.
        :return: predicted price for the request
    """
    try:
        recent_ten = database.extract_predictions_from_database()
        return json.dumps({"recent_predictions": recent_ten})
    except Exception as error:
        return json.dumps({"error": f"REQUEST FAILED because {error}"}), 400  
    
if __name__ == '__main__':
    app.run()    