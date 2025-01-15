# Custom JSON encoder for ObjectId
def str_objectId(Object):
    return str(Object) if Object else None