""" IFCB Data Tools Module

Contains funcitons to work with locally hosted IFCB images before CNN-
classification. 

(Probably adapted from functions in ifcb tools repo (add link))

- retrieve_filepaths_from_local(folder_location): Creates a list of IFCB .png
  filepaths from a local 'ml' folder. 
"""

# imports
import os
import re

def retrieve_filepaths_from_local(folder_location):
    """ Retrieves filepaths of all IFCB images in the specified processed data 
    folder location (local). Returns a list of all image filepaths in the ml 
    sub-folders.

    :param folder_location: Filepath to the ml folder location
    :type folder_location: str
    """
    # list all folders in the ml folder
    sub_folders = os.listdir(folder_location)
    image_list = []

    # loop over sub-folder locations to retrieve all images
    for folder in sub_folders:
        sub_folder_loc = folder_location + '\\' + folder
        if 'C:\\\\' in sub_folder_loc: 
            # Encountered an error when using with marimo notebooks where the 
            # filepaths duplicated the backslashes. This condition has been
            # added to fix that. 
            sub_folder_loc = re.sub(r'\\+', r'\\', sub_folder_loc)
        
        images = os.listdir(sub_folder_loc)

        # loop over all images in each sub-folder and append the full filepaths 
        # to the list
        for image in images:
            im_filepath = folder_location + '\\' + folder + '\\' + image
            if 'C:\\\\' in im_filepath: 
            # Included again to fix duplicate backslashes 
                im_filepath = re.sub(r'\\+', r'\\', im_filepath)

                image_list.append(im_filepath)
    
    return image_list