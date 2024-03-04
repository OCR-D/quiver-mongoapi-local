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
        del d['_id']
        if result_type == 'gt':
            d = d['gt_workspace']
        purged_list.append(d)
    return purged_list
