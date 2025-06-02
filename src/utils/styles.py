from PyQt5.QtCore import QFile, QTextStream

def load_stylesheet():
    file = QFile(":/qss/dark.qss")
    if not file.exists():
        print("Stylesheet file not found!")
        return ""
    
    if file.open(QFile.ReadOnly | QTextStream.Text):
        stream = QTextStream(file)
        stylesheet = stream.readAll()
        file.close()
        return stylesheet
    return ""