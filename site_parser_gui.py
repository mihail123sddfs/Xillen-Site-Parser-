import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt
import csv

class SiteParser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Xillen Site Parser")
        self.setMinimumSize(700, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Вставьте URL для парсинга (пример: https://news.ycombinator.com/)")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://...")
        layout.addWidget(self.url_input)

        self.btn_parse = QPushButton("Парсить")
        self.btn_parse.clicked.connect(self.parse)
        layout.addWidget(self.btn_parse)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.result_list = QListWidget()
        layout.addWidget(self.result_list)

        self.btn_save = QPushButton("Сохранить в CSV")
        self.btn_save.clicked.connect(self.save_csv)
        self.btn_save.setEnabled(False)
        layout.addWidget(self.btn_save)

        self.setLayout(layout)

    def parse(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите URL!")
            return
        self.result_list.clear()
        self.progress.setVisible(True)
        self.progress.setValue(0)
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            items = []
            for i, a in enumerate(soup.find_all("a"), 1):
                text = a.get_text(strip=True)
                href = a.get("href")
                if text and href:
                    items.append({"title": text, "url": href})
                if i % 20 == 0:
                    self.progress.setValue(i)
                    QApplication.processEvents()
            self.progress.setVisible(False)
            for item in items:
                lw_item = QListWidgetItem(f"{item['title']} — {item['url']}")
                self.result_list.addItem(lw_item)
            self.items = items
            self.btn_save.setEnabled(bool(items))
            QMessageBox.information(self, "Готово", f"Найдено {len(items)} ссылок.")
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Ошибка", f"Не удалось спарсить: {e}")

    def save_csv(self):
        if not hasattr(self, "items") or not self.items:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV", "parsed.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["title", "url"])
                writer.writeheader()
                for row in self.items:
                    writer.writerow(row)
            QMessageBox.information(self, "Успех", f"Сохранено {len(self.items)} записей в {path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SiteParser()
    win.show()
    sys.exit(app.exec_())
