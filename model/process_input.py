import json
import numpy as np
import pandas as pd
import pickle
import sklearn


def process_input(request_data: str) -> pd.DataFrame:
    """
    asserts that the request data is correct.
    :param request_data: data gotten from the request made to the API
    :return: the values from the dataframe 
    """
    
    parsed_body = json.loads(request_data)["inputs"]
    assert len(parsed_body) >= 1 #"'inputs' must be a dictionary (or dictionaries) with  features"
    data = {'neighbourhood':[],
            'Area':[],
            'Number_of_rooms':[],
            'Build_year':[],
            'Floor':[],
            'Nearest_educational_institution':[],
            'Nearest_shop':[],
            'Public_transport_stop':[],
            'Heating_system':[],
            'energy_class':[],
            'Building_type':[],
            'No_of_floors':[]
            }

    for item in range(len(parsed_body)):
        data["neighbourhood"].append(parsed_body[item]["neighbourhood"])
        data["Area"].append(parsed_body[item]["Area"])
        data["Number_of_rooms"].append(parsed_body[item]["Number_of_rooms"])
        data["Build_year"].append(parsed_body[item]["Build_year"])
        data["Floor"].append(parsed_body[item]["Floor"])
        data["Nearest_educational_institution"].append(parsed_body[item]["Nearest_educational_institution"])
        data["Nearest_shop"].append(parsed_body[item]["Nearest_shop"])
        data["Public_transport_stop"].append(parsed_body[item]["Public_transport_stop"])
        data["Heating_system"].append(parsed_body[item]["Heating_system"])
        data["energy_class"].append(parsed_body[item]["energy_class"])
        data["Building_type"].append(parsed_body[item]["Building_type"])
        data["No_of_floors"].append(parsed_body[item]["No_of_floors"])
    data_to_be_modelled = pd.DataFrame(data)
    return data_to_be_modelled