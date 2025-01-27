import pymongo

def connect(uri):
    """
    Verilen URI ile MongoDB'ye bağlanır ve bağlantıyı döndürür.
    
    :param uri: MongoDB bağlantı URI'si
    :return: MongoClient nesnesi
    """
    try:
        client = pymongo.MongoClient(uri.replace("senticdb://", "mongodb://"))
        return client
    except Exception as error:
        print(f"SenticDB Error: {error}")
        return None
