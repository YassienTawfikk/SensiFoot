import sys
from PyQt5.QtWidgets import QApplication
from sensifoot.ui.main_window import SensiFootApp
from sensifoot.ui.styles import COMMERCIAL_THEME_QSS

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(COMMERCIAL_THEME_QSS)
    
    window = SensiFootApp()
    window.showFullScreen()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
