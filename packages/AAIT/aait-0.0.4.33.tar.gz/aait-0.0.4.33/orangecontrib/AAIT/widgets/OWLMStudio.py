import os
import sys
import ntpath
import Orange.data
from AnyQt.QtWidgets import QApplication, QLabel
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Domain, StringVariable, Table


if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils.import_uic import uic
    from Orange.widgets.orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from Orange.widgets.orangecontrib.AAIT.llm import lmstudio
else:
    from orangecontrib.AAIT.utils.import_uic import uic
    from orangecontrib.AAIT.utils.initialize_from_ini import apply_modification_from_python_file
    from orangecontrib.AAIT.utils.llm import lmstudio

@apply_modification_from_python_file(filepath_original_widget=__file__)
class OWLMStudio(widget.OWWidget):
    name = "LM Studio"
    description = "Query LM studio to get a response"
    icon = "icons/llm4all.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/llm4all.svg"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owqueryllm.ui")
    want_control_area = False
    priority = 1110
    class Inputs:
        data = Input("Data", Orange.data.Table)
        model = Input("Model", str, auto_summary=False)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    @Inputs.model
    def set_model(self, model):
        """
        Setter for the model.

        Parameters
        ----------
        model : str
            The model.

        Returns
        -------
        None
        """
        if not self.runable:
            return
        self.error("")
        # Set the model
        self.model = ntpath.basename(model)
        if not self.model.endswith(".gguf"):
            self.error("Model needs to be in a gguf format.")
            return
        if self.model is None:
            return
        if self.data is None:
            self.error("widget need an input data with a prompt column")
            return
        if "prompt" not in self.data.domain:
            self.error("input table need a prompt column")
            return

        # Run the widget
        self.run()

    @Inputs.data
    def set_data(self, in_data):
        """
        Setter for the input data.

        Parameters
        ----------
        in_data : Orange.data.Table
            The input table.

        Returns
        -------
        None

        """
        if not self.runable:
            return
        self.error("")
        # Set the input data
        self.data = in_data
        if self.data is None:
            return
        if "prompt" not in self.data.domain:
            self.error("input table need a prompt column")
            return
        if self.model==None:
            return
        # Run the widget
        self.run()

    def __init__(self):
        """
        Initialize the widget.

        This function initializes the widget and sets up its basic properties.
        It also loads the user interface file and finds the label for the description.
        """

        super().__init__()
        self.runable=True
        # Initialize path management
        # This is used to store the current Orange Widgets (OWS) path
        self.current_ows = ""

        # Set the fixed width and height of the widget
        self.setFixedWidth(470)
        self.setFixedHeight(300)

        # Load the user interface file
        uic.loadUi(self.gui, self)

        # Find the label for the description
        self.label_description = self.findChild(QLabel, 'Description')

        # Initialize data management
        # This is used to store the input data
        self.data = None
        self.model = None#"solar-10.7b-instruct-v1.0.Q6_K.gguf"
        self.result = None

    def run(self):
        """
        Run the widget.

        This function runs the widget by initializing the thread and starting it.
        It also handles the case where the thread is already running and interrupts it.

        Returns:
            None
        """
        # Clear the error message
        self.error("")

        # If data is not provided, exit the function
        if self.data is None:
            return

        liste = lmstudio.get_model_lmstudio()
        if liste is None:
            self.error("No model load in lm studio")
            return

        find = False
        for data in liste["data"]:
            if data["id"] == self.model:
                find = True
                break

        if find == False:
            self.error("Model not found in lm studio")
            return

        stream = False
        if "stream" in self.data.domain:
            stream = True
        rows = []
        for i, row in enumerate(self.data):
            features = list(self.data[i])
            metas = list(self.data.metas[i])
            liste = lmstudio.get_model_lmstudio()
            result = lmstudio.appel_lmstudio(str(row["prompt"]), self.model)
            metas.append(result)
            rows.append(features + metas)
        answer_dom = [StringVariable("Answer")]
        domain = Domain(attributes=self.data.domain.attributes, metas=(list(self.data.domain.metas)) + answer_dom,
                        class_vars=self.data.domain.class_vars)
        self.Outputs.data.send(Table.from_list(domain, rows=rows))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWLMStudio()
    my_widget.show()
    app.exec_()
