"""
Functions used by several modules.
"""

def remove_mongodb_id_from_result(json_data, result_type) -> list:
    """
    When retrieving results from MongoDB, the Mongo ID is included by the DB.
    This function removes this ID from the result.
    """
    purged_list = []
    for obj in json_data:
        d = dict(obj)
        remove_keys_from_dict(d)
        del d['_id']
        if result_type == 'gt':
            d = d['gt_workspace']
        purged_list.append(d)
    return purged_list

def remove_keys_from_dict(d: dict) -> dict:
    """
    This function removes keys with the value of null from the result.
    """
    if isinstance(d, dict):
        for key in list(d.keys()):
            if d[key] == None:
                del d[key]
            else:
                remove_keys_from_dict(d[key])
