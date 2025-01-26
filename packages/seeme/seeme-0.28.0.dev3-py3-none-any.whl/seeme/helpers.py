import os
import zipfile
import pathlib
import pickle
import json
from typing import Union

class OptionalDependencyError(Exception):
        pass

def package_version(package_name, include_name=True):
    package = __import__(package_name)
    try:
        package_version = package.__version__
    except:
        from importlib.metadata import version  
        package_version = version(package_name)

    if include_name:
        return f"{package_name}: {package_version}" 
    
    return package_version

def compress_files(path=".", files=[], compression=zipfile.ZIP_DEFLATED, zip_filename="my.zip"):
    with zipfile.ZipFile(zip_filename, mode="w") as zf:
        try:
            for filename in files:
                file_to_zip = f"{path}/{filename}"
                zf.write(file_to_zip, compress_type=compression)
        except FileNotFoundError:
            print("FileNotFoundError:")
            print(file_to_zip)
        finally:
            zf.close()

def compress_folder(path=".", compression=zipfile.ZIP_DEFLATED, zip_filename="my.zip"):
    path = pathlib.Path(path)

    with zipfile.ZipFile(zip_filename, mode="w") as archive:
        for file_path in path.iterdir():
            archive.write(file_path, arcname=file_path.name, compress_type=compression)

def save_pickle(data_folder, filename, contents, mode="wb"):
    os.makedirs(data_folder, exist_ok=True)
    full_filename = f"{data_folder}/{filename}"
    pickle.dump(contents, open(full_filename, mode))

def load_pickle(data_folder, filename, mode="rb"):
    full_filename = f"{data_folder}/{filename}"
    return pickle.load(open(full_filename, mode))

def save_dill(folder, filename, contents, mode="wb"):
    required_package = "dill"
    try:
        package = __import__(required_package)
    except ImportError:

        raise OptionalDependencyError(f"Optional dependency '{required_package}' is not installed.")
    full_filename = f"{folder}/{filename}"
    
    with open(full_filename, mode) as f:
        package.dump(contents, f)


def load_dill(folder, filename, mode="r"):
    required_package = "dill"
    try:
        package = __import__(required_package)
    except ImportError:

        raise OptionalDependencyError(f"Optional dependency '{required_package}' is not installed.")

    full_filename = f"{folder}/{filename}"
    
    with open(full_filename, mode) as f:
    # Load the object from the file using dill.load()
        return  package.load(f)


def save_anything(data_folder, filename, contents, mode="wb", protocol:Union["pkl", "dill"]="pkl"):
    if protocol == "pkl":
        save_pickle(data_folder, filename, contents, mode)
        
    elif protocol == "dill":
        save_dill(data_folder, filename, contents, mode)
    
    else:
        raise ValueError(f"Protocol: {protocol} not supported")

def load_anything(data_folder, filename, mode="wb",protocol:Union["pkl", "dill"]="pkl"):
    if protocol == "pkl":
        load_pickle(data_folder, filename, mode)
        
    elif protocol == "dill":
        load_dill(data_folder, filename, mode)
    else:
        raise ValueError(f"Protocol: {protocol} not supported") 


def save_json(data_folder, filename, contents, mode="w", options={"indent": 4}):
    """
    Saves a dictionary as a JSON file.
    
    :param data: Dictionary to be saved.
    :param filename: Name of the output file.
    """
    full_filename = f"{data_folder}/{filename}"
    with open(full_filename, mode) as f:
        json.dump(contents, f, **options)

def load_json(data_folder, filename, mode='r', options={}):
    """
    Loads a JSON file into a dictionary.
    
    :param filename: Name of the input file.
    :return: Dictionary loaded from the JSON file.
    """
    try:
        full_filename = f"{data_folder}/{filename}"
        with open(full_filename, mode) as f:
            return json.load(f, **options)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Failed to parse JSON in {filename}.")
        return None

def save_jsonl(data_list, filename):
    """
    Saves a list of dictionaries as a JSONL file.
    
    :param data_list: List of dictionaries to be saved.
    :param filename: Name of the output file.
    """
    with open(filename, 'w') as f:
        for data in data_list:
            json.dump(data, f)
            f.write('\n')

def load_jsonl(filename):
    """
    Loads a JSONL file into a list of dictionaries.
    
    :param filename: Name of the input file.
    :return: List of dictionaries loaded from the JSONL file.
    """
    data_list = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.strip():  # Ignore empty lines
                    data_list.append(json.loads(line))
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except json.JSONDecodeError as e:
        print(f"Failed to parse a line in {filename}: {e}")
    return data_list