import sys
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QLabel, QLineEdit, QTabWidget,
                             QMessageBox, QGroupBox, QFormLayout, QListWidget,
                             QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

API_BASE_URL = 'http://localhost:8000/api'

class UploadThread(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, filepath, token):
        super().__init__()
        self.filepath = filepath
        self.token = token
    
    def run(self):
        try:
            with open(self.filepath, 'rb') as f:
                files = {'file': f}
                headers = {}
                if self.token:
                    headers['Authorization'] = f'Token {self.token}'
                
                response = requests.post(f'{API_BASE_URL}/upload/', 
                                       files=files, headers=headers)
                
                if response.status_code in [200, 201]:
                    self.finished.emit(response.json())
                else:
                    self.error.emit(f"Upload failed: {response.text}")
        except Exception as e:
            self.error.emit(str(e))

class ChartCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure(figsize=(6, 4))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.token = None
        self.current_upload_id = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Chemical Equipment Visualizer')
        self.setGeometry(100, 100, 1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.show_login_screen()
    
    def show_login_screen(self):
        self.clear_layout()
        
        login_widget = QWidget()
        login_layout = QVBoxLayout(login_widget)
        login_layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel('Chemical Equipment Visualizer')
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(title)
        
        form_group = QGroupBox('Login')
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow('Username:', self.username_input)
        form_layout.addRow('Password:', self.password_input)
        
        form_group.setLayout(form_layout)
        form_group.setMaximumWidth(400)
        login_layout.addWidget(form_group, alignment=Qt.AlignCenter)
        
        btn_layout = QHBoxLayout()
        login_btn = QPushButton('Login')
        login_btn.clicked.connect(self.handle_login)
        register_btn = QPushButton('Register')
        register_btn.clicked.connect(self.handle_register)
        
        btn_layout.addWidget(login_btn)
        btn_layout.addWidget(register_btn)
        login_layout.addLayout(btn_layout)
        
        self.layout.addWidget(login_widget)
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            response = requests.post(f'{API_BASE_URL}/auth/login/', 
                                   json={'username': username, 'password': password})
            if response.status_code == 200:
                data = response.json()
                self.token = data['token']
                self.show_main_screen()
            else:
                QMessageBox.warning(self, 'Error', 'Invalid credentials')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
    
    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        try:
            response = requests.post(f'{API_BASE_URL}/auth/register/', 
                                   json={'username': username, 'password': password})
            if response.status_code == 201:
                data = response.json()
                self.token = data['token']
                self.show_main_screen()
            else:
                QMessageBox.warning(self, 'Error', 'Registration failed')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
    
    def show_main_screen(self):
        self.clear_layout()
        
        header = QWidget()
        header_layout = QHBoxLayout(header)
        title = QLabel('Chemical Equipment Parameter Visualizer')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        logout_btn = QPushButton('Logout')
        logout_btn.clicked.connect(self.handle_logout)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        self.layout.addWidget(header)
        
        tabs = QTabWidget()
        
        upload_tab = self.create_upload_tab()
        data_tab = self.create_data_tab()
        charts_tab = self.create_charts_tab()
        
        tabs.addTab(upload_tab, 'Upload')
        tabs.addTab(data_tab, 'Data View')
        tabs.addTab(charts_tab, 'Charts')
        
        self.layout.addWidget(tabs)
        
        self.load_history()
    
    def create_upload_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        upload_group = QGroupBox('Upload CSV File')
        upload_layout = QVBoxLayout()
        
        self.file_label = QLabel('No file selected')
        upload_layout.addWidget(self.file_label)
        
        btn_layout = QHBoxLayout()
        select_btn = QPushButton('Select File')
        select_btn.clicked.connect(self.select_file)
        upload_btn = QPushButton('Upload')
        upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(upload_btn)
        upload_layout.addLayout(btn_layout)
        
        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)
        
        history_group = QGroupBox('Upload History')
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_item)
        history_layout.addWidget(self.history_list)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        summary_group = QGroupBox('Summary Statistics')
        self.summary_layout = QFormLayout()
        summary_group.setLayout(self.summary_layout)
        layout.addWidget(summary_group)
        
        pdf_btn = QPushButton('Generate PDF Report')
        pdf_btn.clicked.connect(self.generate_pdf)
        layout.addWidget(pdf_btn)
        
        layout.addStretch()
        return widget
    
    def create_data_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.data_table = QTableWidget()
        layout.addWidget(self.data_table)
        
        return widget
    
    def create_charts_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.pie_canvas = ChartCanvas(widget)
        self.bar_canvas = ChartCanvas(widget)
        
        layout.addWidget(QLabel('Equipment Type Distribution'))
        layout.addWidget(self.pie_canvas)
        layout.addWidget(QLabel('Average Parameters'))
        layout.addWidget(self.bar_canvas)
        
        return widget
    
    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Select CSV File', '', 'CSV Files (*.csv)')
        if filename:
            self.selected_file = filename
            self.file_label.setText(filename.split('/')[-1].split('\\')[-1])
    
    def upload_file(self):
        if not hasattr(self, 'selected_file'):
            QMessageBox.warning(self, 'Warning', 'Please select a file first')
            return
        
        self.upload_thread = UploadThread(self.selected_file, self.token)
        self.upload_thread.finished.connect(self.upload_finished)
        self.upload_thread.error.connect(self.upload_error)
        self.upload_thread.start()
    
    def upload_finished(self, data):
        self.current_upload_id = data['upload_id']
        QMessageBox.information(self, 'Success', 'File uploaded successfully')
        self.display_summary(data['summary'])
        self.load_equipment_data(data['upload_id'])
        self.load_history()
    
    def upload_error(self, error):
        QMessageBox.critical(self, 'Error', f'Upload failed: {error}')
    
    def load_history(self):
        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'Token {self.token}'
            
            response = requests.get(f'{API_BASE_URL}/history/', headers=headers)
            if response.status_code == 200:
                history_data = response.json()
                self.history_list.clear()
                for item in history_data:
                    self.history_list.addItem(
                        f"{item['filename']} - {item['uploaded_at']} (Count: {item['total_count']})"
                    )
                self.history_data = history_data
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def load_history_item(self, item):
        index = self.history_list.row(item)
        upload_id = self.history_data[index]['id']
        self.current_upload_id = upload_id
        
        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'Token {self.token}'
            
            response = requests.get(f'{API_BASE_URL}/summary/?upload_id={upload_id}', headers=headers)
            if response.status_code == 200:
                summary = response.json()
                self.display_summary(summary)
                self.load_equipment_data(upload_id)
            else:
                QMessageBox.critical(self, 'Error', f'Failed to load data: {response.text}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
    
    def display_summary(self, summary):
        self.clear_form_layout(self.summary_layout)
        
        if 'total_count' in summary:
            self.summary_layout.addRow('Total Count:', QLabel(str(summary['total_count'])))
            self.summary_layout.addRow('Avg Flowrate:', QLabel(str(summary['avg_flowrate'])))
            self.summary_layout.addRow('Avg Pressure:', QLabel(str(summary['avg_pressure'])))
            self.summary_layout.addRow('Avg Temperature:', QLabel(str(summary['avg_temperature'])))
            
            if 'type_distribution' in summary:
                self.plot_charts(summary)
    
    def load_equipment_data(self, upload_id):
        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'Token {self.token}'
            
            response = requests.get(f'{API_BASE_URL}/equipment/?upload_id={upload_id}', headers=headers)
            if response.status_code == 200:
                equipment_data = response.json()
                self.populate_table(equipment_data)
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error loading equipment data: {e}")
    
    def populate_table(self, data):
        if not data:
            return
        
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        
        for row, equipment in enumerate(data):
            self.data_table.setItem(row, 0, QTableWidgetItem(equipment['equipment_name']))
            self.data_table.setItem(row, 1, QTableWidgetItem(equipment['equipment_type']))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(equipment['flowrate'])))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(equipment['pressure'])))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(equipment['temperature'])))
        
        self.data_table.resizeColumnsToContents()
    
    def plot_charts(self, summary):
        type_dist = summary.get('type_distribution', {})
        
        self.pie_canvas.axes.clear()
        if type_dist:
            self.pie_canvas.axes.pie(type_dist.values(), labels=type_dist.keys(), autopct='%1.1f%%')
            self.pie_canvas.axes.set_title('Equipment Type Distribution')
        self.pie_canvas.draw()
        
        self.bar_canvas.axes.clear()
        metrics = ['Flowrate', 'Pressure', 'Temperature']
        values = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]
        self.bar_canvas.axes.bar(metrics, values, color=['#4bc0c0', '#ff9f40', '#9966ff'])
        self.bar_canvas.axes.set_title('Average Parameters')
        self.bar_canvas.axes.set_ylabel('Value')
        self.bar_canvas.draw()
    
    def generate_pdf(self):
        if not self.current_upload_id:
            QMessageBox.warning(self, 'Warning', 'No data loaded')
            return
        
        try:
            headers = {}
            if self.token:
                headers['Authorization'] = f'Token {self.token}'
            
            response = requests.post(f'{API_BASE_URL}/generate-report/', 
                                   json={'upload_id': self.current_upload_id},
                                   headers=headers)
            
            if response.status_code == 200:
                filename, _ = QFileDialog.getSaveFileName(self, 'Save PDF', 
                                                         f'equipment_report_{self.current_upload_id}.pdf',
                                                         'PDF Files (*.pdf)')
                if filename:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, 'Success', 'PDF saved successfully')
            else:
                QMessageBox.critical(self, 'Error', f'Failed to generate PDF: {response.text}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))
    
    def handle_logout(self):
        self.token = None
        self.current_upload_id = None
        self.show_login_screen()
    
    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def clear_form_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
