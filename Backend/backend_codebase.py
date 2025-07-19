import shelve, pandas, random

class Material_SKU():
    """
    This class manages the various data attributes and functions required to analyze SKU-level insights in the Sample Dashboard.

    ### The following attributes are assigned in this class:
        
        self.sku: str

    """
    try:
        with shelve.open("shelved_sample_data") as db:
            inventory_report: pandas.DataFrame = db["inventory_report"]
            data_as_of: str = db["data_as_of"]
    except KeyError:
        inventory_report: pandas.DataFrame = pandas.DataFrame()
        data_as_of: str = ""

    def __init__(self, sku: str) -> None:
        self.sku: str = sku