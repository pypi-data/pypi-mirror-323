from typing import Union

import pandas as pd


def detect_paths(data: Union[dict, list], parent_path: list = None) -> list:
    """
    Recursively detect paths in JSON data.
    """
    paths = []
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = parent_path + [key] if parent_path else [key]
            if isinstance(value, (dict, list)):
                paths.extend(detect_paths(value, current_path))
            else:
                paths.append(current_path)
    elif isinstance(data, list):
        # Assume uniform schema and analyze the first item
        if len(data) > 0 and isinstance(data[0], (dict, list)):
            paths.extend(detect_paths(data[0], parent_path))
    return paths


def analyze_json_for_normalize(data: Union[dict, list]) -> dict:
    if isinstance(data, dict):
        # Assume the JSON starts as a list of records
        top_level = [data]
    else:
        # If it's a dict, treat it as a single record in a list
        top_level = data
    record_paths = set()
    meta_keys = []
    # Detect paths for each record
    if len(top_level) > 0:
        # Analyze the first item in the list or dictionary
        paths = detect_paths(top_level[0])
        for path in paths:
            # Navigate the data to determine if the path leads to a list
            current = top_level[0]
            is_record_path = False
            for part in path:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list):
                    # If we encounter a list, add the parent path to record_paths
                    if len(path) > 1:
                        path = path[:-1]
                    record_paths.add(tuple(path))
                    is_record_path = True
                    break
                else:
                    break
            if not is_record_path:
                # If we traverse the entire path without hitting a list, add to meta
                meta_keys.append(path)
    # Convert meta keys into the desired format
    formatted_meta_keys = []
    for key in meta_keys:
        if len(key) == 1:
            formatted_meta_keys.append(key[0])
        else:
            formatted_meta_keys.append(key)
    return {
        "record_paths": [list(x) for x in record_paths],
        "meta": formatted_meta_keys,
    }


def json_to_dataframe(
    data: Union[dict, list],
    record_path_column_name: str = "record_path",
    sep: str = "_",
) -> pd.DataFrame:
    schema = analyze_json_for_normalize(data)
    dataframes = []
    for record_path in schema["record_paths"]:
        record_data = pd.json_normalize(
            data, record_path=record_path, meta=schema["meta"], sep=sep
        )
        if len(schema["record_paths"]) > 1:
            record_data[record_path_column_name] = sep.join(record_path)
        dataframes.append(record_data)
    return pd.concat(dataframes, ignore_index=True)
