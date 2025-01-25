import sys

from AnyQt.QtWidgets import (QApplication, QDialog, QFileDialog, QLabel,
                             QMessageBox, QVBoxLayout)


def BoxInfo(text):
    """
    Open A simple info box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.setWindowTitle("Information")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()


def BoxWarning(text):
    """
    Open A simple warning box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(text)
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()


def BoxError(text):
    """
    Open A simple error box
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowTitle("Error")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()


def BoxSelectFolder(argself, default_path=None):
    """
    return "" if nothing was selected else the path
    """
    if default_path == None or default_path == "":
        folder = QFileDialog.getExistingDirectory()
    else:
        folder = QFileDialog.getExistingDirectory(argself, caption="Select a folder", directory=default_path)
    return folder.replace("\\", "/")

def BoxSelectExistingFile(argself,default_dir="",extention="All Files (*);;Text Files (*.txt)"):
    """
    return "" if nothing was selected else the path
    """
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    fileName, _ = QFileDialog.getOpenFileName(argself, "Select a file", default_dir, extention,options=options)
    if fileName:
        fileName=fileName.replace("\\", "/")
        return fileName
    else:
        return ""


def BoxYesNo(question):
    """
    return True if Yes is clicked, False in other cases
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(question)
    msg.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
    ret = msg.exec()
    if ret == msg.Yes:
        return True
    return False


class ProgressDialog(QDialog):
    """
    to use :
    dialog_progress = ProgressDialog(title="hello",content="blablalblagblal")
    dialog_progress.show()
    # do something
    dialog_progress.stop()
    """
    def __init__(self, title="Title",content="blablabla",parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)
        self.label = QLabel(content, self)
        layout.addWidget(self.label)

    def show(self):
        super().show()
        QApplication.processEvents()

    def closeEvent(self, event):
        # ignore click on x
        event.ignore()

    def stop(self):
        self.accept()