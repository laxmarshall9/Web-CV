import shelve, streamlit, pandas
from datetime import datetime
from streamlit.runtime.uploaded_file_manager import UploadedFile

def upload_tab_function() -> None:
    data_file: UploadedFile | None = streamlit.file_uploader(":green[**Feed me!**]", type="xlsx")

    if data_file is not None:
        # Get data
        inventory_report: pandas.DataFrame = pandas.read_excel(data_file, "Inventory - Prior Month Review").astype(str)
        mdm_report: pandas.DataFrame = pandas.read_excel(data_file, "MDM Report").astype(str)
        data_as_of: str = datetime.now().strftime("%d%b%Y %I:%M%p")

        # Convert data types
        inventory_report["Opening Stock"] = inventory_report["Opening Stock"].astype(float).astype(int)
        inventory_report["Units Received Last Month"] = inventory_report["Units Received Last Month"].astype(float).astype(int)
        inventory_report["Units Sold Last Month"] = inventory_report["Units Sold Last Month"].astype(float).astype(int)
        inventory_report["Closing Stock"] = inventory_report["Closing Stock"].astype(float).astype(int)
        inventory_report["Inventory Value Per Unit (USD)"] = inventory_report["Inventory Value Per Unit (USD)"].astype(float)
        inventory_report["Total Value - Closing Stock (USD)"] = inventory_report["Total Value - Closing Stock (USD)"].astype(float)
        inventory_report["Total Value - Opening Stock (USD)"] = inventory_report["Total Value - Opening Stock (USD)"].astype(float)

        mdm_report["Shelf Life (Years)"] = mdm_report["Shelf Life (Years)"].astype(float).astype(int)
        mdm_report["Dimension: Weight (lbs)"] = mdm_report["Dimension: Weight (lbs)"].astype(float)
        mdm_report["Dimension: Length (in)"] = mdm_report["Dimension: Length (in)"].astype(float)
        mdm_report["Dimension: Width (in)"] = mdm_report["Dimension: Width (in)"].astype(float)
        mdm_report["Dimension: Height (in)"] = mdm_report["Dimension: Height (in)"].astype(float)
        mdm_report["Product Creation Date"] = pandas.to_datetime(mdm_report["Product Creation Date"], errors="coerce").dt.date

        # Store locally
        with shelve.open("shelved_sample_data") as db:
            db["inventory_report"] = inventory_report
            db["mdm_report"] = mdm_report
            db["data_as_of"] = data_as_of


        streamlit.subheader("*:primary[All set!]*", anchor= False)
        streamlit.caption(f"*Data as-of: :blue[**{data_as_of}**]*")