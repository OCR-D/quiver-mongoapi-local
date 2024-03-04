from pymongo import collection

def get_all_releases(coll: collection.Collection):
    """
    Returns a list of all releases for which Quiver provides data.
    """
    return coll.distinct('metadata.release_info')
