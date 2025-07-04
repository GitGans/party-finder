import sys
from PyQt5.QtWidgets import QApplication
from ui import PartyFinderApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wnd = PartyFinderApp()
    wnd.show()
    sys.exit(app.exec_())