import shelve, streamlit, pandas
from datetime import datetime
from streamlit.runtime.uploaded_file_manager import UploadedFile

def upload_tab_function() -> None:
    data_file: UploadedFile | None = streamlit.file_uploader(":green[**Feed me!**]", type="xlsx")

    if data_file is not None:
        # Get data
        inventory_report: pandas.DataFrame = pandas.read_excel(data_file, "Inventory Report").astype(str)
        data_as_of: str = datetime.now().strftime("%d%b%Y %I:%M%p")

        # Convert data types
        inventory_report["Opening Stock"] = inventory_report["Opening Stock"].astype(int)
        inventory_report["Units received this month"] = inventory_report["Units received this month"].astype(int)
        inventory_report["Units sold this month"] = inventory_report["Units sold this month"].astype(int)
        inventory_report["Current Stock"] = inventory_report["Current Stock"].astype(int)
        inventory_report["Cost Price Per Unit (USD)"] = inventory_report["Cost Price Per Unit (USD)"].astype(float)
        inventory_report["Cost Price Total (USD)"] = inventory_report["Cost Price Total (USD)"].astype(float)

        # Store locally
        with shelve.open("shelved_sample_data") as db:
            db["inventory_report"] = inventory_report
            db["data_as_of"] = data_as_of

        streamlit.subheader("*:primary[All set!]*", anchor= False)
        streamlit.caption(f"*Data as-of: :blue[**{data_as_of}**]*")