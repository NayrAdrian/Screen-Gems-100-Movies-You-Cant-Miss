import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QStatusBar
)


class MovieApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window settings
        self.setWindowTitle("Screen Gems: 100 Movies You Can't Miss")
        self.setGeometry(100, 100, 1024, 768)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QVBoxLayout()

        # Title Bar
        title_label = QLabel("Top 100 Movies to Watch")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; text-align: center;")
        main_layout.addWidget(title_label)

        # Search Box
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by title...")
        search_layout.addWidget(self.search_box)
        main_layout.addLayout(search_layout)

        # Movie Table
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Rank", "Title", "Year", "Rating", "Description"])
        main_layout.addWidget(self.table_widget)

        # Buttons Layout
        button_layout = QHBoxLayout()

        scrape_button = QPushButton("Scrape Movies")
        button_layout.addWidget(scrape_button)

        export_button = QPushButton("Export to CSV")
        button_layout.addWidget(export_button)

        clear_button = QPushButton("Clear Data")
        button_layout.addWidget(clear_button)

        main_layout.addLayout(button_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Set Layout
        central_widget.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieApp()
    window.show()
    sys.exit(app.exec_())
