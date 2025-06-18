from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QTextEdit, QPushButton, QProgressBar, QLabel, QMessageBox, QComboBox, QSpacerItem, QSizePolicy, QFrame, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QGuiApplication, QDesktopServices, QIcon
import qtawesome as qta
import os
from .api_manager import APIKeyManager
from .gemini_worker import PromptRefinementWorker
from .settings_dialog import SettingsDialog
import re
import json
from pathlib import Path

DEFAULT_AI_PLATFORMS = {
    "ChatGPT (OpenAI)": "https://chat.openai.com/",
    "Gemini (Google)": "https://gemini.google.com/app",
    "Claude (Anthropic)": "https://claude.ai/",
    "Copilot (Microsoft)": "https://copilot.microsoft.com/",
    "Perplexity": "https://www.perplexity.ai/",
    "Midjourney": "https://www.midjourney.com/app/",
    "DALL-E": "https://labs.openai.com/",
    "Suno AI": "https://app.suno.ai/",
    "Stable Diffusion": "https://stablediffusionweb.com/",
    "Pika Labs": "https://pika.art/",
    "Sora (OpenAI)": "https://openai.com/sora",
    "Google Bard": "https://bard.google.com/",
    "You.com": "https://you.com/",
    "Cohere": "https://chat.cohere.com/",
    "Mistral": "https://chat.mistral.ai/",
    "Llama 3 (Meta)": "https://llama.meta.com/",
    "Other / Custom": ""
}

def load_ai_platforms_from_config(base_dir):
    config_path = Path(base_dir) / "App" / "config" / "config.json"
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            ai_platforms = config.get("ai_platforms", None)
            if isinstance(ai_platforms, dict) and ai_platforms:
                return ai_platforms
    except Exception:
        pass
    return DEFAULT_AI_PLATFORMS

class PromanisMainWindow(QMainWindow):
    def __init__(self, base_dir):
        super().__init__()
        self.base_dir = base_dir
        # Set wand.ico as window icon for all GUI (including taskbar)
        icon_path = os.path.join(self.base_dir, "App", "wand.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(qta.icon('fa5s.magic'))
        self.api_manager = APIKeyManager(base_dir)
        self.worker = None
        self.ai_platforms = load_ai_platforms_from_config(self.base_dir)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Promanis - AI Prompt Refiner")
        self.setGeometry(100, 100, 1200, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        header_icon = QLabel()
        # Use wand.ico as header icon if available, else fallback to qtawesome
        icon_path = os.path.join(self.base_dir, "App", "wand.ico")
        if os.path.exists(icon_path):
            header_icon.setPixmap(QIcon(icon_path).pixmap(28, 28))
        else:
            header_icon.setPixmap(qta.icon('fa6s.wand-sparkles', color='#1976D2').pixmap(28, 28))
        header_layout.addWidget(header_icon)
        self.header_label = QLabel("Promanis - AI Prompt Refiner")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        self.header_label.setFont(header_font)
        self.header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        self.desc_label = QLabel("Promanis helps you rewrite, enhance, and structure your AI prompts for better results. "
                            "Paste your raw prompt, add context if needed, and let Promanis generate a refined, ready-to-use prompt for any AI model (text, image, audio, video, etc).")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.desc_label.setStyleSheet("color: #555; font-size: 11pt; margin-bottom: 8px;")
        main_layout.addWidget(self.desc_label)

        # --- Top: Ribbon-style Grouped Options ---
        ribbon_frame = QFrame()
        ribbon_frame.setFrameShape(QFrame.StyledPanel)
        ribbon_layout = QHBoxLayout(ribbon_frame)
        ribbon_layout.setSpacing(16)
        ribbon_layout.setContentsMargins(8, 8, 8, 8)
        ribbon_layout.setAlignment(Qt.AlignTop)

        group_style = (
            "QGroupBox {"
            " border: none;"
            " margin-top: 0px;"
            " padding: 14px 0 14px 0;"
            " background-color: rgba(153,153,153,0.07);"
            " border-radius: 12px;"
            "}"
        )

        # Store group widgets for language switching
        self.lang_group = QGroupBox("Language")
        self.lang_group.setStyleSheet(group_style)
        lang_layout = QHBoxLayout(self.lang_group)
        lang_layout.setAlignment(Qt.AlignTop)
        lang_icon = QLabel()
        lang_icon.setPixmap(qta.icon('fa6s.language', color='#1976D2').pixmap(18, 18))
        lang_layout.addWidget(lang_icon)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Bahasa Indonesia"])
        self.language_combo.setCurrentText("English")
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.language_combo)
        ribbon_layout.addWidget(self.lang_group, alignment=Qt.AlignTop)

        self.scope_type_group = QGroupBox("Scope & Type")
        self.scope_type_group.setStyleSheet(group_style)
        scope_type_layout = QGridLayout(self.scope_type_group)
        scope_type_layout.setAlignment(Qt.AlignTop)
        scope_icon = QLabel()
        scope_icon.setPixmap(qta.icon('fa6s.layer-group', color='#388E3C').pixmap(18, 18))
        scope_type_layout.addWidget(scope_icon, 0, 0, alignment=Qt.AlignTop)
        self.scope_combo = QComboBox()
        self.scope_combo.addItems([
            "General", "Programming", "Novel", "Science", "Math", "Education", "History", "Philosophy",
            "Business", "Marketing", "Legal", "Medical", "Technical Writing", "Art", "Music", "Poetry",
            "Social Media", "Blog", "News", "Productivity", "Personal", "Finance", "Travel", "Cooking",
            "Gaming", "Interview", "Resume", "Email", "Presentation", "Research", "Psychology", "Self-help",
            "Spirituality", "Parenting", "Fitness", "Health", "Fashion", "Beauty", "DIY", "Photography",
            "Film", "Theater", "Comics", "Scriptwriting", "Journalism", "Advertising", "UX/UI", "Data Science",
            "AI/ML", "Engineering", "Environment", "Politics", "Sports", "Other"
        ])
        self.scope_combo.setCurrentText("General")
        scope_type_layout.addWidget(self.scope_combo, 0, 1, alignment=Qt.AlignTop)
        type_icon = QLabel()
        type_icon.setPixmap(qta.icon('fa6s.shapes', color='#F9A825').pixmap(18, 18))
        scope_type_layout.addWidget(type_icon, 1, 0, alignment=Qt.AlignTop)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Text Generation",
            "Image Generation",
            "Audio Generation",
            "Video Generation",
            "Video+Audio Generation",
            "Novel",
            "Explanation",
            "Other"
        ])
        self.type_combo.setCurrentText("Text Generation")
        scope_type_layout.addWidget(self.type_combo, 1, 1, alignment=Qt.AlignTop)
        ribbon_layout.addWidget(self.scope_type_group, alignment=Qt.AlignTop)

        # Group 3: Detail
        self.detail_group = QGroupBox("Detail")
        self.detail_group.setStyleSheet(group_style)
        detail_layout = QHBoxLayout(self.detail_group)
        detail_layout.setAlignment(Qt.AlignTop)
        detail_icon = QLabel()
        detail_icon.setPixmap(qta.icon('fa6s.list', color='#D32F2F').pixmap(18, 18))
        detail_layout.addWidget(detail_icon)
        self.detail_combo = QComboBox()
        self.detail_combo.addItems(["Simple", "Detailed", "Complex", "Template"])
        self.detail_combo.setCurrentText("Detailed")
        detail_layout.addWidget(self.detail_combo)
        ribbon_layout.addWidget(self.detail_group, alignment=Qt.AlignTop)

        # Group 4: Platform
        self.platform_group = QGroupBox("Platform")
        self.platform_group.setStyleSheet(group_style)
        platform_layout = QHBoxLayout(self.platform_group)
        platform_layout.setAlignment(Qt.AlignTop)
        platform_icon = QLabel()
        platform_icon.setPixmap(qta.icon('fa6s.robot', color='#8e24aa').pixmap(18, 18))
        platform_layout.addWidget(platform_icon)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(list(self.ai_platforms.keys()))
        self.platform_combo.setCurrentText("ChatGPT (OpenAI)")
        platform_layout.addWidget(self.platform_combo)
        self.open_platform_button = QPushButton("Buka Platform")
        self.open_platform_button.setIcon(qta.icon('fa6s.arrow-up-right-from-square', color='white'))
        self.open_platform_button.setStyleSheet("""
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
        self.open_platform_button.clicked.connect(self.open_selected_platform)
        platform_layout.addWidget(self.open_platform_button)
        ribbon_layout.addWidget(self.platform_group, alignment=Qt.AlignTop)

        ribbon_layout.addStretch()
        main_layout.addWidget(ribbon_frame)

        # --- Actions Layout (compact, right-aligned) ---
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        self.config_button = QPushButton()
        self.config_button.setText("Settings")
        self.config_button.setIcon(qta.icon('fa6s.gear', color='white'))
        self.config_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        self.config_button.clicked.connect(self.open_settings)
        actions_layout.addWidget(self.config_button)
        
        self.run_button = QPushButton()
        self.run_button.setText("Refine Prompt")
        self.run_button.setIcon(qta.icon('fa6s.wand-sparkles', color='white'))
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.run_button.clicked.connect(self.refine_prompt)
        actions_layout.addWidget(self.run_button)
        
        self.clear_button = QPushButton()
        self.clear_button.setText("Clear All")
        self.clear_button.setIcon(qta.icon('fa6s.eraser', color='white'))
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.clear_button.clicked.connect(self.clear_all)
        actions_layout.addWidget(self.clear_button)

        self.copy_button = QPushButton()
        self.copy_button.setText("Copy Refined Prompt")
        self.copy_button.setIcon(qta.icon('fa6s.copy', color='white'))
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.copy_button.clicked.connect(self.copy_refined_prompt)
        actions_layout.addWidget(self.copy_button)

        self.wa_button = QPushButton()
        self.wa_button.setText("WA Group")
        self.wa_button.setIcon(qta.icon('fa6b.whatsapp', color='white'))
        self.wa_button.setStyleSheet("""
            QPushButton {
                background-color: #25D366;
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #128C7E;
            }
        """)
        self.wa_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://chat.whatsapp.com/CMQvDxpCfP647kBBA6dRn3")))
        actions_layout.addWidget(self.wa_button)

        main_layout.addLayout(actions_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        content_layout = QHBoxLayout()
        
        left_layout = QVBoxLayout()

        input_label_layout = QHBoxLayout()
        input_icon = QLabel()
        input_icon.setPixmap(qta.icon('fa6s.pen-to-square', color='#1976D2').pixmap(20, 20))
        input_label_layout.addWidget(input_icon)
        self.input_label = QLabel("Raw Prompt (Before):")
        self.input_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.input_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        input_label_layout.addWidget(self.input_label)
        input_label_layout.addStretch()
        left_layout.addLayout(input_label_layout)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter your raw prompt here...")
        self.input_text.setMinimumHeight(200)
        input_font = QFont("Arial", 14)
        self.input_text.setFont(input_font)
        self.input_text.setStyleSheet("""
            QTextEdit {
                padding: 16px;
                font-size: 12pt;
            }
        """)
        left_layout.addWidget(self.input_text)

        context_label_layout = QHBoxLayout()
        context_icon = QLabel()
        context_icon.setPixmap(qta.icon('fa6s.circle-info', color='#388E3C').pixmap(20, 20))
        context_label_layout.addWidget(context_icon)
        self.context_label = QLabel("Context (Optional):")
        self.context_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.context_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        context_label_layout.addWidget(self.context_label)
        context_label_layout.addStretch()
        left_layout.addLayout(context_label_layout)

        self.context_text = QTextEdit()
        self.context_text.setPlaceholderText("Add any context or background information here (optional)...")
        self.context_text.setMinimumHeight(80)
        context_font = QFont("Arial", 14)
        self.context_text.setFont(context_font)
        self.context_text.setStyleSheet("""
            QTextEdit {
                padding: 16px;
                font-size: 12pt;
            }
        """)
        left_layout.addWidget(self.context_text)
        
        content_layout.addLayout(left_layout)
        
        right_output_layout = QVBoxLayout()

        output_label_layout = QHBoxLayout()
        output_icon = QLabel()
        output_icon.setPixmap(qta.icon('fa6s.wand-sparkles', color='#F9A825').pixmap(20, 20))
        output_label_layout.addWidget(output_icon)
        self.output_label = QLabel("Refined Prompt (After):")
        self.output_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.output_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        output_label_layout.addWidget(self.output_label)
        output_label_layout.addStretch()
        right_output_layout.addLayout(output_label_layout)

        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Refined prompt will appear here...")
        self.output_text.setMinimumHeight(400)
        self.output_text.setReadOnly(True)
        output_font = QFont("Arial", 14)
        self.output_text.setFont(output_font)
        self.output_text.setStyleSheet("""
            QTextEdit {
                padding: 16px;
                font-size: 12pt;
            }
        """)
        right_output_layout.addWidget(self.output_text)
        content_layout.addLayout(right_output_layout)
        
        main_layout.addLayout(content_layout)

        self.status_label = QLabel("Ready to refine prompts")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Set initial language
        self.on_language_changed("English")
    
    def open_selected_platform(self):
        platform_name = self.platform_combo.currentText()
        url = self.ai_platforms.get(platform_name, "")
        prompt_text = self.output_text.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Warning", "No refined prompt to copy and open.")
            return
        QGuiApplication.clipboard().setText(prompt_text)
        if url:
            QDesktopServices.openUrl(QUrl(url))
            self.status_label.setText(f"Prompt copied & opening {platform_name}...")
        else:
            self.status_label.setText("Prompt copied to clipboard. (No URL for this platform)")

    def open_settings(self):
        dialog = SettingsDialog(self.api_manager, self, ai_platforms=self.ai_platforms)
        if dialog.exec():
            try:
                self.api_manager.load_api_keys()
                # Reload AI platforms in case user changed them
                self.ai_platforms = load_ai_platforms_from_config(self.base_dir)
                self.platform_combo.clear()
                self.platform_combo.addItems(list(self.ai_platforms.keys()))
                self.platform_combo.setCurrentText("ChatGPT (OpenAI)")
                current_language = self.language_combo.currentText()
                if current_language == "Bahasa Indonesia":
                    self.status_label.setText("Pengaturan berhasil disimpan!")
                else:
                    self.status_label.setText("Settings saved successfully!")
            except Exception as e:
                current_language = self.language_combo.currentText()
                if current_language == "Bahasa Indonesia":
                    QMessageBox.critical(self, "Error", f"Gagal memuat ulang API keys: {str(e)}")
                else:
                    QMessageBox.critical(self, "Error", f"Failed to reload API keys: {str(e)}")
    
    def on_language_changed(self, language):
        # Update group titles directly for both languages
        if language == "Bahasa Indonesia":
            self.setWindowTitle("Promanis - Penyempurna Prompt AI")
            self.header_label.setText("Promanis - Penyempurna Prompt AI")
            self.desc_label.setText("Promanis membantu Anda menulis ulang, meningkatkan, dan menyusun prompt AI Anda untuk hasil yang lebih baik. "
                                   "Tempel prompt mentah Anda, tambahkan konteks jika diperlukan, dan biarkan Promanis menghasilkan prompt yang disempurnakan dan siap pakai untuk model AI apa pun (teks, gambar, audio, video, dll).")
            self.lang_group.setTitle("Bahasa")
            self.scope_type_group.setTitle("Cakupan & Jenis")
            self.detail_group.setTitle("Detail")
            self.platform_group.setTitle("Platform")
            scope_items_id = [
                "Umum", "Pemrograman", "Novel", "Sains", "Matematika", "Pendidikan", "Sejarah", "Filsafat",
                "Bisnis", "Pemasaran", "Hukum", "Medis", "Penulisan Teknis", "Seni", "Musik", "Puisi",
                "Media Sosial", "Blog", "Berita", "Produktivitas", "Personal", "Keuangan", "Perjalanan", "Memasak",
                "Game", "Wawancara", "CV", "Email", "Presentasi", "Riset", "Psikologi", "Bantuan Diri",
                "Spiritual", "Parenting", "Kebugaran", "Kesehatan", "Fashion", "Kecantikan", "DIY", "Fotografi",
                "Film", "Teater", "Komik", "Penulisan Naskah", "Jurnalisme", "Iklan", "UX/UI", "Data Science",
                "AI/ML", "Teknik", "Lingkungan", "Politik", "Olahraga", "Lainnya"
            ]
            current_scope_index = self.scope_combo.currentIndex()
            self.scope_combo.clear()
            self.scope_combo.addItems(scope_items_id)
            self.scope_combo.setCurrentIndex(current_scope_index)
            type_items_id = [
                "Generasi Teks",
                "Generasi Gambar", 
                "Generasi Audio",
                "Generasi Video",
                "Generasi Video+Audio",
                "Novel",
                "Penjelasan",
                "Lainnya"
            ]
            current_type_index = self.type_combo.currentIndex()
            self.type_combo.clear()
            self.type_combo.addItems(type_items_id)
            self.type_combo.setCurrentIndex(current_type_index)
            detail_items_id = ["Sederhana", "Detail", "Kompleks", "Template"]
            current_detail_index = self.detail_combo.currentIndex()
            self.detail_combo.clear()
            self.detail_combo.addItems(detail_items_id)
            self.detail_combo.setCurrentIndex(current_detail_index)
            self.input_label.setText("Prompt Mentah (Sebelum):")
            self.output_label.setText("Prompt Matang (Sesudah):")
            self.input_text.setPlaceholderText("Masukkan prompt mentah Anda di sini...")
            self.output_text.setPlaceholderText("Prompt yang sudah disempurnakan akan muncul di sini...")
            self.context_label.setText("Konteks (Opsional):")
            self.context_text.setPlaceholderText("Tambahkan konteks atau informasi latar belakang di sini (opsional)...")
            self.run_button.setText("Sempurnakan Prompt")
            self.clear_button.setText("Bersihkan Semua")
            self.copy_button.setText("Salin Prompt Matang")
            self.config_button.setText("Pengaturan")
            self.wa_button.setText("Grup WA")
            self.open_platform_button.setText("Buka Platform")
            self.status_label.setText("Siap untuk menyempurnakan prompt")
        else:
            self.setWindowTitle("Promanis - AI Prompt Refiner")
            self.header_label.setText("Promanis - AI Prompt Refiner")
            self.desc_label.setText("Promanis helps you rewrite, enhance, and structure your AI prompts for better results. "
                                   "Paste your raw prompt, add context if needed, and let Promanis generate a refined, ready-to-use prompt for any AI model (text, image, audio, video, etc).")
            self.lang_group.setTitle("Language")
            self.scope_type_group.setTitle("Scope & Type")
            self.detail_group.setTitle("Detail")
            self.platform_group.setTitle("Platform")
            scope_items_en = [
                "General", "Programming", "Novel", "Science", "Math", "Education", "History", "Philosophy",
                "Business", "Marketing", "Legal", "Medical", "Technical Writing", "Art", "Music", "Poetry",
                "Social Media", "Blog", "News", "Productivity", "Personal", "Finance", "Travel", "Cooking",
                "Gaming", "Interview", "Resume", "Email", "Presentation", "Research", "Psychology", "Self-help",
                "Spirituality", "Parenting", "Fitness", "Health", "Fashion", "Beauty", "DIY", "Photography",
                "Film", "Theater", "Comics", "Scriptwriting", "Journalism", "Advertising", "UX/UI", "Data Science",
                "AI/ML", "Engineering", "Environment", "Politics", "Sports", "Other"
            ]
            current_scope_index = self.scope_combo.currentIndex()
            self.scope_combo.clear()
            self.scope_combo.addItems(scope_items_en)
            self.scope_combo.setCurrentIndex(current_scope_index)
            type_items_en = [
                "Text Generation",
                "Image Generation",
                "Audio Generation", 
                "Video Generation",
                "Video+Audio Generation",
                "Novel",
                "Explanation",
                "Other"
            ]
            current_type_index = self.type_combo.currentIndex()
            self.type_combo.clear()
            self.type_combo.addItems(type_items_en)
            self.type_combo.setCurrentIndex(current_type_index)
            detail_items_en = ["Simple", "Detailed", "Complex", "Template"]
            current_detail_index = self.detail_combo.currentIndex()
            self.detail_combo.clear()
            self.detail_combo.addItems(detail_items_en)
            self.detail_combo.setCurrentIndex(current_detail_index)
            self.input_label.setText("Raw Prompt (Before):")
            self.output_label.setText("Refined Prompt (After):")
            self.input_text.setPlaceholderText("Enter your raw prompt here...")
            self.output_text.setPlaceholderText("Refined prompt will appear here...")
            self.context_label.setText("Context (Optional):")
            self.context_text.setPlaceholderText("Add any context or background information here (optional)...")
            self.run_button.setText("Refine Prompt")
            self.clear_button.setText("Clear All")
            self.copy_button.setText("Copy Refined Prompt")
            self.config_button.setText("Settings")
            self.wa_button.setText("WA Group")
            self.open_platform_button.setText("Open Platform")
            self.status_label.setText("Ready to refine prompts")
    
    def refine_prompt(self):
        prompt_text = self.input_text.toPlainText().strip()
        context_text = self.context_text.toPlainText().strip()
        current_language = self.language_combo.currentText()
        current_scope = self.scope_combo.currentText()
        current_detail = self.detail_combo.currentText()
        current_type = self.type_combo.currentText()
        
        if not prompt_text:
            if current_language == "Bahasa Indonesia":
                QMessageBox.warning(self, "Peringatan", "Silakan masukkan prompt terlebih dahulu!")
            else:
                QMessageBox.warning(self, "Warning", "Please enter a prompt first!")
            return
            
        try:
            self.run_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            if current_language == "Bahasa Indonesia":
                self.status_label.setText("Sedang memproses prompt dengan Gemini AI...")
            else:
                self.status_label.setText("Processing prompt with Gemini AI...")
            
            self.worker = PromptRefinementWorker(
                self.api_manager, prompt_text, current_language, context_text, current_scope, current_detail, current_type
            )
            self.worker.finished.connect(self.on_refinement_finished)
            self.worker.error.connect(self.on_refinement_error)
            self.worker.start()
            
        except Exception as e:
            current_language = self.language_combo.currentText()
            if current_language == "Bahasa Indonesia":
                QMessageBox.critical(self, "Error", f"Kesalahan: {str(e)}")
            else:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            self.reset_ui()
    
    def on_refinement_finished(self, result):
        if result and isinstance(result, str):
            result = result.replace("\\n", "\n")
            result = re.sub(r"(?<!\*)\* (?!\*)", "• ", result)
            result = re.sub(r"\*\*(.*?)\*\*", lambda m: m.group(1).upper(), result)
        self.output_text.setPlainText(result)
        current_language = self.language_combo.currentText()
        if current_language == "Bahasa Indonesia":
            self.status_label.setText("Penyempurnaan prompt berhasil!")
        else:
            self.status_label.setText("Prompt refinement completed successfully!")
        self.reset_ui()
    
    def on_refinement_error(self, error_message):
        current_language = self.language_combo.currentText()
        if current_language == "Bahasa Indonesia":
            QMessageBox.critical(self, "Error", f"Gagal menyempurnakan prompt: {error_message}")
            self.status_label.setText("Gagal menyempurnakan prompt")
        else:
            QMessageBox.critical(self, "Error", f"Failed to refine prompt: {error_message}")
            self.status_label.setText("Failed to refine prompt")
        self.reset_ui()
    
    def reset_ui(self):
        self.run_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if self.worker:
            self.worker.quit()
            self.worker.wait()
            self.worker = None
    
    def clear_all(self):
        self.input_text.clear()
        self.output_text.clear()
        self.context_text.clear()
        current_language = self.language_combo.currentText()
        if current_language == "Bahasa Indonesia":
            self.status_label.setText("Siap untuk menyempurnakan prompt")
        else:
            self.status_label.setText("Ready to refine prompts")

    def copy_refined_prompt(self):
        text = self.output_text.toPlainText()
        if text.strip():
            QGuiApplication.clipboard().setText(text)
            current_language = self.language_combo.currentText()
            if current_language == "Bahasa Indonesia":
                self.status_label.setText("Prompt matang berhasil disalin ke clipboard!")
            else:
                self.status_label.setText("Refined prompt copied to clipboard!")
        else:
            current_language = self.language_combo.currentText()
            if current_language == "Bahasa Indonesia":
                QMessageBox.information(self, "Info", "Tidak ada prompt matang untuk disalin.")
            else:
                QMessageBox.information(self, "Info", "No refined prompt to copy.")
        self.progress_bar.setVisible(False)
        if self.worker:
            self.worker.quit()
            self.worker.wait()
            self.worker = None
    
    def clear_all(self):
        self.input_text.clear()
        self.output_text.clear()
        self.context_text.clear()
        current_language = self.language_combo.currentText()
        if current_language == "Bahasa Indonesia":
            self.status_label.setText("Siap untuk menyempurnakan prompt")
        else:
            self.status_label.setText("Ready to refine prompts")

    def copy_refined_prompt(self):
        text = self.output_text.toPlainText()
        if text.strip():
            QGuiApplication.clipboard().setText(text)
            current_language = self.language_combo.currentText()
            if current_language == "Bahasa Indonesia":
                self.status_label.setText("Prompt matang berhasil disalin ke clipboard!")
            else:
                self.status_label.setText("Refined prompt copied to clipboard!")
        else:
            current_language = self.language_combo.currentText()
            if current_language == "Bahasa Indonesia":
                QMessageBox.information(self, "Info", "Tidak ada prompt matang untuk disalin.")
            else:
                QMessageBox.information(self, "Info", "No refined prompt to copy.")
