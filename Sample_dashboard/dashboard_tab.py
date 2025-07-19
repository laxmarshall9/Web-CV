from Backend.backend_codebase import *
import streamlit, pandas, shelve, random
import plotly.express as pxs

def dashboard_tab_function() -> None:
    try:
        with shelve.open("shelved_sample_data") as db:
            inventory_report: pandas.DataFrame = db["inventory_report"]
            data_as_of: str = db["data_as_of"]
    except KeyError:
        inventory_report: pandas.DataFrame = pandas.DataFrame()
        data_as_of: str = ""

    streamlit.title("Planning Dashboard", anchor=False)

    overview_tab, sku_tab = streamlit.tabs(["KPI Oversight","Plan by SKU"])

    with overview_tab:
        pass

    with sku_tab:
        sku_list: tuple[str] = tuple(set(inventory_report["Product ID"]))

        if streamlit.button("Load SKU"):
            if sku_list:
                sku_selection: str = random.choice(sku_list)
            else:
                sku_selection: str = ""
            
            if sku_selection:
                filtered_inv_dataframe: pandas.DataFrame = inventory_report.loc[inventory_report["Product ID"] == sku_selection]
                streamlit.dataframe(filtered_inv_dataframe)
                