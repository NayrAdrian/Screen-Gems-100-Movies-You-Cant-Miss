import csv
import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QStatusBar, QFileDialog
)
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()


class MovieApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window settings
        self.setWindowTitle("Screen Gems: Top 100 Movies You Can't Miss")
        self.setGeometry(100, 100, 1024, 768)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QVBoxLayout()

        # Title Bar
        title_label = QLabel("Screen Gems: 100 Movies You Can't Miss")
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
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(["Rank", "Title", "Year", "Rating", "Description", "Trailer"])
        self.table_widget.verticalHeader().setVisible(False)

        # Set column widths
        self.table_widget.setColumnWidth(0, 50)  # Rank column
        self.table_widget.setColumnWidth(1, 200)  # Title column
        self.table_widget.setColumnWidth(2, 60)  # Year column
        self.table_widget.setColumnWidth(3, 80)  # Rating column
        self.table_widget.setColumnWidth(4, 500)  # Description column
        self.table_widget.horizontalHeader().setStretchLastSection(True)  # Stretch the last column

        # Enable word wrap for the description column
        self.table_widget.setWordWrap(True)

        # Ensure rows resize to fit contents
        self.table_widget.resizeRowsToContents()

        main_layout.addWidget(self.table_widget)

        # Buttons Layout
        button_layout = QHBoxLayout()

        scrape_button = QPushButton("Scrape Movies")
        scrape_button.clicked.connect(self.scrape_movies)
        button_layout.addWidget(scrape_button)

        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(export_button)

        clear_button = QPushButton("Clear Data")
        clear_button.clicked.connect(self.clear_data)
        button_layout.addWidget(clear_button)

        main_layout.addLayout(button_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("height: 40px;")
        self.setStatusBar(self.status_bar)

        # Disclaimer in Status Bar
        self.status_bar.showMessage(
            "Disclaimer: The data provided in this application is sourced from Rotten Tomatoes. "
            "This app is intended solely for educational and study purposes only."
        )

        # Set Layout
        central_widget.setLayout(main_layout)

    def scrape_movies(self):
        try:
            movies = self.scrape_top_100_movies()
            self.table_widget.setRowCount(len(movies))
            for i, movie in enumerate(movies):
                # Add movie details to the table
                self.table_widget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.table_widget.setItem(i, 1, QTableWidgetItem(movie['Title']))
                self.table_widget.setItem(i, 2, QTableWidgetItem(movie['Year']))
                self.table_widget.setItem(i, 3, QTableWidgetItem(movie['Rating']))
                self.table_widget.setItem(i, 4, QTableWidgetItem(movie['Description']))

                # Add trailer button
                trailer_button = QPushButton("Watch Trailer")
                trailer_button.clicked.connect(lambda checked, url=movie['TrailerURL']: self.open_trailer(url))
                self.table_widget.setCellWidget(i, 5, trailer_button)

            self.table_widget.resizeRowsToContents()
            self.status_bar.showMessage("Movies scraped successfully! Disclaimer: All movie information is subject to "
                                    "change and may not reflect the most current ratings or details.", 30000)
        except Exception as e:
            self.status_bar.showMessage(f"An error occurred: {str(e)}", 5000)
            print(f"Error: {e}")  # Print the error for debugging

    def clear_data(self):
        self.table_widget.setRowCount(0)
        self.status_bar.showMessage("Data cleared.", 5000)

    def export_to_csv(self):
        # Open file dialog to select save location
        options = QFileDialog.Options()
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"movies_export_{timestamp}.csv"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", default_filename, "CSV Files (*.csv)",
                                                   options=options)

        if not file_path:
            return

        # Write table data to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # Write the header
            header = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
            writer.writerow(header)

            # Write the data
            for row in range(self.table_widget.rowCount()):
                row_data = [self.table_widget.item(row, col).text() if self.table_widget.item(row, col) else '' for col
                            in range(self.table_widget.columnCount())]
                writer.writerow(row_data)

        self.status_bar.showMessage("Data exported to CSV successfully.", 5000)

    def scrape_top_100_movies(self):
        base_url = "https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/"
        movies = self.scrape_rotten_tomatoes(base_url)
        second_page_url = f"{base_url}page/2/"
        movies += self.scrape_rotten_tomatoes(second_page_url)
        return movies[:100]

    def scrape_rotten_tomatoes(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.status_bar.showMessage(f"Failed to retrieve the page. Status code: {response.status_code}", 5000)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        movies = []
        movie_containers = soup.find_all('div', class_='article_movie_title')
        for container in movie_containers:
            title_element = container.find('a')
            title = title_element.text.strip() if title_element else 'No title available'
            year = container.find('span', class_='subtle start-year').text.strip() if container.find('span',
                                                                                                     class_='subtle start-year') else 'No year available'
            rating = container.find('span', class_='tMeterScore').text.strip() if container.find('span',
                                                                                                 class_='tMeterScore') else 'No rating available'
            description_container = container.find_next('div', class_='info critics-consensus')
            description = description_container.get_text(
                strip=True) if description_container else 'No description available'
            if description.startswith('Critics Consensus:'):
                description = description.replace('Critics Consensus:', '').strip()

            # Replace this with the actual fetching logic
            trailer_url = self.fetch_trailer_url(title, year)

            movies.append({
                'Title': title,
                'Year': year,
                'Rating': rating,
                'Description': description,
                'TrailerURL': trailer_url
            })
        return movies

    def fetch_trailer_url(self, title, year):
        api_key = os.getenv("YT_DATA_API")
        if not api_key:
            self.status_bar.showMessage("YouTube API key not found. Please check your environment variables.", 5000)
            return ""

        youtube = build("youtube", "v3", developerKey=api_key)

        search_query = f"{title} {year} official trailer"
        search_response = youtube.search().list(
            q=search_query,
            part="id,snippet",
            maxResults=1,
            type="video"
        ).execute()

        if search_response['items']:
            video_id = search_response['items'][0]['id']['videoId']
            trailer_url = f"https://www.youtube.com/watch?v={video_id}"
            return trailer_url
        else:
            return ""  # Return empty string if no trailer is found

    def open_trailer(self, url):
        if not url:
            self.status_bar.showMessage("Trailer not available.", 5000)
            return
        # Open in a new window using QWebEngineView
        trailer_window = QMainWindow(self)
        trailer_window.setWindowTitle("Movie Trailer")
        trailer_window.setGeometry(100, 100, 800, 600)

        web_view = QWebEngineView()
        web_view.setUrl(QUrl(url))
        trailer_window.setCentralWidget(web_view)
        trailer_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieApp()
    window.show()
    sys.exit(app.exec_())
