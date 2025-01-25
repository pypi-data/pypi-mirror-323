import sys
import os
import json
import Orange
from Orange.data import Table, Domain, ContinuousVariable, StringVariable
from AnyQt.QtWidgets import QApplication
from Orange.widgets import widget
from Orange.widgets.widget import OWWidget, MultiInput
from Orange.widgets.utils.signals import Input, Output
from Orange.data import Table
from Orange.base import Learner, Model
from orangewidget import gui
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from orangecontrib.AAIT.utils import SimpleDialogQt
from orangecontrib.AAIT.utils import MetManagement
from Orange.widgets.settings import Setting
import random
import math
import re


class OWWidgetRandomData(widget.OWWidget):
    name = "Random data from inference space"
    description = "Random data permettant de générer des données en fonctin d'un min un max et un step (optionnel)"
    icon = "icons/de.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/de.png"

    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/ow_widget_random_data.ui")
    want_control_area = False
    priority = 1003

    class Inputs:
        data = Input("Data", Orange.data.Table)
        data_rules = Input("Rules from CN2", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)

    nombre_generation :str =Setting("10")

    @Inputs.data
    def set_data(self, data):
        if data is not None:
            self.in_data = data
            self.load_random_data()

    @Inputs.data_rules
    def set_data_rules(self, dataset):
        if dataset is not None:
            self.data_rules = dataset
            self.load_random_data()


    def __init__(self):
        super().__init__()
        uic.loadUi(self.gui, self)
        self.labelChemin = self.findChild(QtWidgets.QLabel, 'label_chemin_fichier')
        self.boutton = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.boutton.clicked.connect(self.load_random_data)
        self.spinbox = self.findChild(QtWidgets.QSpinBox, 'lineEdit_nomFichier')
        self.spinbox.setValue(int(self.nombre_generation))
        self.spinbox.valueChanged.connect(self.spinbox_value_changed)
        self.data_rules = None
        self.in_data = None
        self.seed = True

    def spinbox_value_changed(self, value):
        self.nombre_generation = str(value)

    def random_float_with_step(self, min, max, step):
        steps = int((max - min) / step)
        return round(min + (random.randint(0, steps) * step), 2)

    def generate_random_data_for_rules(self, tab_min, tab_max, tab_nb_iteration):
        data = []
        if self.seed:
            random.seed(0)
        for _ in range(tab_nb_iteration):
            d = []
            for i in range(len(tab_min)):
                value = random.uniform(tab_min[i], tab_max[i])
                d.append(value)
            data.append(d)
        return data

    def generate_random_data(self, nb_iterations, tab):
        data = []
        if self.seed:
            random.seed(0)
        for _ in range(nb_iterations):
            d = []
            for i in range(len(tab)):
                value_min = min([tab[i]["min"].value, tab[i]["max"].value])
                value_max = max([tab[i]["min"].value, tab[i]["max"].value])
                if "step" in tab.domain and math.isnan(tab[i]["step"].value) == False:
                    value = self.random_float_with_step(value_min, value_max, tab[i]["step"].value)
                else:
                    value = random.uniform(value_min, value_max)
                d.append(value)
            data.append(d)
        return data

    def del_space_debut_fin(self,text_to_edit):
        if text_to_edit[0] == " ":
            text_to_edit = text_to_edit[1:]
        if text_to_edit[-1] == " ":
            text_to_edit = text_to_edit[:-1]
        return text_to_edit


    def generate_random_data_from_rules(self, nb_iterations, tab, rules_rename):
        data = []
        rules=[]

        if len(rules_rename)==0:
            return []

        for i in range(len(rules_rename)):
            rules.append(rules_rename[i]["regle"].value)

        tab_nb_iteration=[]
        for i in range(len(rules)):
            tab_nb_iteration.append(int(nb_iterations/len(rules)))
        nb_iteration_to_add=nb_iterations-sum(tab_nb_iteration)
        tab_nb_iteration[-1]=tab_nb_iteration[-1]+nb_iteration_to_add

        for idx,element in enumerate(rules):
            tab_element_name=[]
            tab_element_min=[]
            tab_element_max=[]
            for i in range(len(tab)):
                element_name=tab[i]["name"].value
                element_min = tab[i]["min"].value
                element_max = tab[i]["max"].value
                if(element_min>element_max):
                    element_max=tab[i]["min"].value
                    element_min= tab[i]["max"].value
                tab_element_name.append(element_name)
                tab_element_min.append(element_min)
                tab_element_max.append(element_max)

            if element!="TRUE":
                regl_list=element.split(" and ")
                for unit_rule in regl_list:
                    current_var,current_symb,current_value=re.split(r'(<=|>=)', unit_rule)
                    current_var=self.del_space_debut_fin(current_var)
                    current_symb=self.del_space_debut_fin(current_symb)
                    current_value=self.del_space_debut_fin(current_value)
                    index_tab = tab_element_name.index(current_var) if current_var in tab_element_name else -1

                    if index_tab==-1:
                        print("error "+current_var+ " not in possible variable")
                        raise Exception("error "+current_var+ " not in possible variable")
                    if current_symb=='>=':
                        tab_element_min[index_tab]=max(tab_element_min[index_tab],float(current_value))
                    else:
                        tab_element_max[index_tab] = min(tab_element_max[index_tab], float(current_value))

            d = self.generate_random_data_for_rules(tab_element_min, tab_element_max, tab_nb_iteration[idx])
            data = data + d
        return data

    def load_random_data(self):
        self.error("")
        if self.in_data is None:
            return
        if "name" not in self.in_data.domain or "min" not in self.in_data.domain or "max" not in self.in_data.domain:
                if "Feature" not in self.in_data.domain or "Min." not in self.in_data.domain or "Max." not in self.in_data.domain:
                    self.error("You file need at least 3 headers : 'name', 'min', 'max' or 'Feature', 'Min.', 'Max.'")
                    return
        if self.nombre_generation == "0":
            self.error("Error in the numner of generation")
            return
        if "Feature" in self.in_data.domain or "Min." in self.in_data.domain or "Max." in self.in_data.domain:
            new_attributes = [
                ContinuousVariable("min") if attr.name == "Min." else
                ContinuousVariable("max") if attr.name == "Max." else
                attr
                for attr in self.in_data.domain.attributes
            ]
            new_metas = [
                StringVariable("name") if meta.name == "Feature" else meta
                for meta in self.in_data.domain.metas
            ]
            new_domain = Domain(new_attributes, metas=new_metas)
            self.in_data = Table(new_domain, self.in_data.X, metas=self.in_data.metas)
        if self.data_rules != None:
            data = self.generate_random_data_from_rules(int(self.nombre_generation), self.in_data, self.data_rules)
        else:
            data = self.generate_random_data(int(self.nombre_generation), self.in_data)
        if data != None and data != []:
            headers = []
            for i in range(len(self.in_data)):
                headers.append(self.in_data[i]["name"].value)
            domain = Domain([ContinuousVariable(h) for h in headers])
            tab = Table.from_list(domain, data)
            self.Outputs.data.send(tab)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    obj = OWWidgetRandomData()
    obj.show()
    app.exec_()



