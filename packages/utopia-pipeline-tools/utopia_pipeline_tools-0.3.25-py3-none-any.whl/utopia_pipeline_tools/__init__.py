"""
utopia_pipeline_tools: a set of modules to streamline the process of converting
raw IFCB data to CNN-classified and validated datasets. 
"""
import os
import json

# a bit of metadata
__version__ = '0.3.25'
__author__ = 'Claire Berschauer'
__credits__ = 'Applied Physics Laboratory - UW'

# global attributes
label_dict = {'Chloro': 0,
              'Cilliate': 1,
              'Crypto': 2,
              'Diatom': 3,
              'Dictyo': 4,
              'Dinoflagellate': 5,
              'Eugleno': 6,
              'Unidentified_Living': 7,
              'Prymnesio': 8,
              'Inoperative': 9
             }

label_list = list(label_dict.keys())

aphiaID_dict = {0: ['Chlorophyta', 801],
                1: ['Ciliophora', 11],
                2: ['Cryptophyceae', 17639],
                3: ['Bacillariophyceae', 148899],
                4: ['Dictyochophyceae', 157256],
                5: ['Dinophyceae', 19542],
                6: ['Euglenoidea', 582177],
                7: ['Biota', 1],
                8: ['Prymnesiophyceae', 115057],
                9: ['Inoperative', -9999]
                }

calibration_ratio = 2.7488  # pixels/um (feature extraction v4 value)
# or 3.4 if using the feature extraction v2

config_info= {"blob_storage_name": None,
              "connection_string": None,
              "server": None,
              "database": None,
              "db_user": None,
              "db_password": None,
              'subscription_id':  None,
              'resource_group': None,
              'workspace_name': None,
              'experiment_name': None,
              'api_key': None,
              'model_name': None,
              'endpoint_name': None,
              'deployment_name': None
              }

default_investigators = {"Firstname_Lastname": ['Organization', 
                                                'email@org.com'],
                         "Firstname_Lastname": ['Organization', 
                                                'email@org.com'],
                         }

# config functions

def set_config_vars(calibration, config_dict, investigators):
    """Updates utopia_pipeline_tools calibration, configuration, and 
    investigator variables
    
    :param calibration: The ratio of pixels to micrometers of the IFCB images.
    :type calibration: float
    :param config_dict: Dictionary of information needed to configure blob 
        access, SQL server access, and cloud model registration.
    :type config_dict: Dict
    :param investigators: Dictionary containing investigator names, 
        organizations, and emails. 
    :type investigators: Dict
    """
    import utopia_pipeline_tools as upt

    upt.calibration_ratio = calibration
    upt.config_info = config_dict
    upt.default_investigators = investigators
