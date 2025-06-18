from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
                               QPushButton, QMessageBox, QFrame, QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QAbstractItemView)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import qtawesome as qta
from google import genai
import time
import json
from pathlib import Path


class APITestWorker(QThread):
    finished = Signal(str, bool)
    
    def __init__(self, api_key, key_index):
        super().__init__()
        self.api_key = api_key
        self.key_index = key_index
    
    def run(self):
        try:
            client = genai.Client(api_key=self.api_key)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=["Test connection"]
            )
            
            if response and hasattr(response, 'text') and response.text:
                self.finished.emit(f"Key #{self.key_index}: ✓ Valid (Response: {response.text[:50]}...)", True)
            else:
                self.finished.emit(f"Key #{self.key_index}: ✗ Invalid response", False)
                
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "PERMISSION_DENIED" in error_msg:
                self.finished.emit(f"Key #{self.key_index}: ✗ Invalid API key", False)
            elif "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                self.finished.emit(f"Key #{self.key_index}: ⚠ Rate limited (key may be valid)", True)
            elif "403" in error_msg:
                self.finished.emit(f"Key #{self.key_index}: ✗ Access forbidden", False)
            else:
                self.finished.emit(f"Key #{self.key_index}: ✗ Error - {error_msg}", False)


class SettingsDialog(QDialog):
    def __init__(self, api_manager, parent=None, ai_platforms=None):
        super().__init__(parent)
        self.api_manager = api_manager
        self.test_workers = []
        self.ai_platforms = ai_platforms if ai_platforms else {}
        self.base_dir = getattr(api_manager, "base_dir", None)
        self.config_path = Path(self.base_dir) / "App" / "config" / "config.json" if self.base_dir else None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Settings - API Configuration")
        self.setGeometry(200, 200, 750, 650)
        self.setModal(True)
        
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        # --- Tab 1: API Keys ---
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        # ...existing API key UI code, but use api_layout instead of layout...
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        header_icon.setPixmap(qta.icon('fa6s.gear', color='#1976D2').pixmap(24, 24))
        header_layout.addWidget(header_icon)
        header_label = QLabel("API Configuration")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        api_layout.addLayout(header_layout)
        desc_label = QLabel("Manage your Gemini AI API keys. Each key should be on a separate line.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; font-size: 11pt; margin-bottom: 10px;")
        api_layout.addWidget(desc_label)
        keys_frame = QFrame()
        keys_frame.setFrameShape(QFrame.StyledPanel)
        keys_layout = QVBoxLayout(keys_frame)
        keys_label_layout = QHBoxLayout()
        keys_icon = QLabel()
        keys_icon.setPixmap(qta.icon('fa6s.key', color='#F9A825').pixmap(18, 18))
        keys_label_layout.addWidget(keys_icon)
        keys_label = QLabel("API Keys:")
        keys_label.setFont(QFont("Arial", 12, QFont.Bold))
        keys_label_layout.addWidget(keys_label)
        keys_label_layout.addStretch()
        keys_layout.addLayout(keys_label_layout)
        self.api_keys_edit = QTextEdit()
        self.api_keys_edit.setMinimumHeight(200)
        self.api_keys_edit.setPlaceholderText("Enter your Gemini API keys here, one per line...\n\nExample:\nAIzaSyC1234567890abcdef\nAIzaSyD987654321zyxwvu")
        self.api_keys_edit.setFont(QFont("Consolas", 10))
        self.api_keys_edit.setStyleSheet("""
            QTextEdit {
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                border: 2px solid #dee2e6;
                border-radius: 6px;
            }
            QTextEdit:focus {
                border-color: #1976D2;
            }
        """)
        keys_layout.addWidget(self.api_keys_edit)
        self.test_results = QTextEdit()
        self.test_results.setMaximumHeight(120)
        self.test_results.setReadOnly(True)
        self.test_results.setPlaceholderText("API test results will appear here...")
        self.test_results.setFont(QFont("Consolas", 9))
        self.test_results.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
        keys_layout.addWidget(self.test_results)
        info_layout = QHBoxLayout()
        info_icon = QLabel()
        info_icon.setPixmap(qta.icon('fa6s.circle-info', color='#17A2B8').pixmap(16, 16))
        info_layout.addWidget(info_icon)
        info_label = QLabel("Get your free API key from: https://ai.google.dev/")
        info_label.setStyleSheet("color: #17A2B8; font-size: 10pt;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        keys_layout.addLayout(info_layout)
        api_layout.addWidget(keys_frame)
        self.status_frame = QFrame()
        self.status_frame.setFrameShape(QFrame.StyledPanel)
        status_layout = QHBoxLayout(self.status_frame)
        status_icon = QLabel()
        status_icon.setPixmap(qta.icon('fa6s.chart-line', color='#28A745').pixmap(18, 18))
        status_layout.addWidget(status_icon)
        self.status_label = QLabel()
        self.update_status()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        api_layout.addWidget(self.status_frame)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.test_button = QPushButton("API Test")
        self.test_button.setIcon(qta.icon('fa6s.flask', color='white'))
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #ffffff;
            }
        """)
        self.test_button.clicked.connect(self.test_api_keys)
        button_layout.addWidget(self.test_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.setIcon(qta.icon('fa6s.xmark', color='white'))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        save_button = QPushButton("Save")
        save_button.setIcon(qta.icon('fa6s.floppy-disk', color='white'))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        api_layout.addLayout(button_layout)
        self.load_current_keys()
        tabs.addTab(api_tab, "API Keys")

        # --- Tab 2: AI Platforms ---
        platform_tab = QWidget()
        platform_layout = QVBoxLayout(platform_tab)
        platform_header = QHBoxLayout()
        platform_icon = QLabel()
        platform_icon.setPixmap(qta.icon('fa6s.robot', color='#8e24aa').pixmap(20, 20))
        platform_header.addWidget(platform_icon)
        platform_label = QLabel("AI Platforms (Dropdown List)")
        platform_label.setFont(QFont("Arial", 13, QFont.Bold))
        platform_header.addWidget(platform_label)
        platform_header.addStretch()
        platform_layout.addLayout(platform_header)
        platform_desc = QLabel("Edit daftar platform AI dan URL-nya. Nama akan muncul di dropdown, URL akan dibuka saat tombol ditekan.")
        platform_desc.setStyleSheet("color: #666; font-size: 10pt;")
        platform_layout.addWidget(platform_desc)
        self.platform_table = QTableWidget()
        self.platform_table.setColumnCount(2)
        self.platform_table.setHorizontalHeaderLabels(["Platform Name", "URL"])
        self.platform_table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        self.platform_table.horizontalHeader().setStretchLastSection(True)
        self.platform_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.platform_table.setMinimumHeight(250)
        self.load_platform_table()
        platform_layout.addWidget(self.platform_table)
        # Add row button
        add_row_btn = QPushButton("Tambah Baris")
        add_row_btn.setIcon(qta.icon('fa6s.plus', color='white'))
        add_row_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e24aa;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6d1b7b;
            }
        """)
        add_row_btn.clicked.connect(self.add_platform_row)
        platform_layout.addWidget(add_row_btn)
        tabs.addTab(platform_tab, "AI Platforms")
        layout.addWidget(tabs)

    def load_platform_table(self):
        platforms = self.ai_platforms if self.ai_platforms else {}
        self.platform_table.setRowCount(len(platforms))
        for i, (name, url) in enumerate(platforms.items()):
            self.platform_table.setItem(i, 0, QTableWidgetItem(name))
            self.platform_table.setItem(i, 1, QTableWidgetItem(url))

    def add_platform_row(self):
        row = self.platform_table.rowCount()
        self.platform_table.insertRow(row)
        self.platform_table.setItem(row, 0, QTableWidgetItem(""))
        self.platform_table.setItem(row, 1, QTableWidgetItem(""))

    def get_platforms_from_table(self):
        platforms = {}
        for row in range(self.platform_table.rowCount()):
            name_item = self.platform_table.item(row, 0)
            url_item = self.platform_table.item(row, 1)
            name = name_item.text().strip() if name_item else ""
            url = url_item.text().strip() if url_item else ""
            if name:
                platforms[name] = url
        return platforms

    def load_current_keys(self):
        try:
            if self.api_manager.api_keys_path.exists():
                with open(self.api_manager.api_keys_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    self.api_keys_edit.setPlainText(content)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not load existing API keys: {str(e)}")

    def update_status(self):
        try:
            total_keys = len(self.api_manager.api_keys)
            current_index = self.api_manager.current_index
            self.status_label.setText(f"Status: {total_keys} keys loaded, currently using key #{current_index + 1}")
        except:
            self.status_label.setText("Status: No keys loaded")

    def test_api_keys(self):
        text = self.api_keys_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter at least one API key to test.")
            return
        
        lines = [line.strip() for line in text.split('\n') if line.strip() and not line.strip().startswith('#')]
        if not lines:
            QMessageBox.warning(self, "Warning", "No valid API keys found. Please enter at least one key.")
            return
        
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        self.test_results.clear()
        self.test_results.append("🔄 Starting real API tests...\n")
        
        # Clean up previous workers
        for worker in self.test_workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        self.test_workers.clear()
        
        # Test each key
        for i, key in enumerate(lines[:5]):  # Limit to first 5 keys to avoid spam
            if key.startswith('AIzaSy') and len(key) == 39:
                worker = APITestWorker(key, i + 1)
                worker.finished.connect(self.on_test_result)
                self.test_workers.append(worker)
                worker.start()
                time.sleep(0.5)  # Small delay between requests
            else:
                self.test_results.append(f"Key #{i+1}: ✗ Invalid format (should start with 'AIzaSy' and be 39 chars)")
        
        if len(lines) > 5:
            self.test_results.append(f"\nℹ Only testing first 5 keys to avoid rate limits. Total keys: {len(lines)}")
    
    def on_test_result(self, message, is_valid):
        self.test_results.append(message)
        
        # Check if all workers are done
        all_done = all(not worker.isRunning() for worker in self.test_workers)
        if all_done:
            self.test_button.setEnabled(True)
            self.test_button.setText("Real API Test")
            self.test_results.append("\n✅ API testing completed!")
    
    def save_settings(self):
        text = self.api_keys_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter at least one API key.")
            return
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        valid_lines = [line for line in lines if not line.startswith('#')]
        if not valid_lines:
            QMessageBox.warning(self, "Warning", "No valid API keys found. Please enter at least one key.")
            return
        try:
            # Save API keys
            with open(self.api_manager.api_keys_path, 'w', encoding='utf-8') as f:
                f.write(text)
            # Save AI platforms
            platforms = self.get_platforms_from_table()
            if self.config_path:
                try:
                    if self.config_path.exists():
                        with open(self.config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                    else:
                        config = {}
                    config["ai_platforms"] = platforms
                    with open(self.config_path, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Failed to save AI platforms: {str(e)}")
            QMessageBox.information(self, "Success", f"Settings saved successfully!\n\nTotal keys: {len(valid_lines)}")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")

    def closeEvent(self, event):
        for worker in self.test_workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        super().closeEvent(event)
