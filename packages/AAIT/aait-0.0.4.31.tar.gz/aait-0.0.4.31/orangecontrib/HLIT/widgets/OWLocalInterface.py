import os
from pathlib import Path
from pprint import pprint

from AnyQt.QtWidgets import QMessageBox
from Orange.data import Table

from Orange.widgets import widget
if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.HLIT.widgets.download.BaseLocalInterfaceWidget import BaseLocalInterfaceWidget
    from Orange.widgets.orangecontrib.AAIT.utils import MetManagement

else:
    from orangecontrib.HLIT.widgets.download.BaseLocalInterfaceWidget import BaseLocalInterfaceWidget
    from orangecontrib.AAIT.utils import MetManagement



class OWLocalInterface(widget.OWWidget): # type: ignore
    name = "TOTO TATA"
    description = "Get a simple data file (csv, xlsx, pkl...) from a local interface"
    # icon = "icons/local_interf_pull.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/local_interf_pull.svg"
    priority =0
    category = "Advanced Artificial Intelligence Tools"


    def __init__(self):
        # Specific for this widget: defines how files are opened
        self.opening_method = "file"
        super().__init__()
        #self.info_label.setText("Initialized Local Interface Widget.")
        from Orange.widgets.orangecontrib.AAIT.utils.shared_functions import setup_shared_variables
        self.current_ows=""
        setup_shared_variables(self)
        print("################################")
        print(self.current_ows)
        print("################################")
        

    def process_files(self, files_to_process: list[Path]):

        if len(files_to_process) > 1:
            print("More than one file to process. Only processing first. You may want to use MultiFile Download Widget")
            QMessageBox.critical(self, "DownloadWidget Error", "More than one file to process. Only processing first. You may want to use MultiFile Download Widget instead.")
        elif len(files_to_process) == 0:
            print("No files to process for Download Widget. Make sure you correctly set the input_id.")
            return
        file_path = files_to_process[0]

        try:
            # Load data using the defined opening method
            data_table = Table.from_file(str(file_path))
            self.info_label.setText(f"Loaded file: {str(file_path)}")
            self.Outputs.data.send(data_table)
        except Exception as e:
            print(f"Error loading file {str(file_path)}: {e}")
            self.info_label.setText(f"Error loading file: {str(file_path)}")
        return  # Only process first matching entry
