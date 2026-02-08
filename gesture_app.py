import sys
import json
import os
import random
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QListWidgetItem, QSpinBox, QComboBox, QFileDialog, 
                             QScrollArea, QMessageBox, QInputDialog, QProgressBar,
                             QGridLayout, QStackedWidget, QSizePolicy, QTabWidget,
                             QAbstractItemView, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QImageReader, QIcon, QPainter, QColor, QFont

# --- データ保存用ファイル名 (固定) ---
PRESET_FILE = "session_sets.json"
STATS_FILE = "image_stats.json"
CONFIG_FILE = "app_config.json"

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# --- 言語リソース ---
TEXTS = {
    "app_title": {"en": "Gesture Drawing App", "ja": "ジェスチャードローイング"},
    "always_top": {"en": "📌 Always on Top", "ja": "📌 常に手前に表示"},
    "preset_label": {"en": "Session Set:", "ja": "セッションセット:"},
    "custom_setting": {"en": "Custom Settings", "ja": "カスタム設定"},
    "btn_save": {"en": "Save Set", "ja": "セットを保存"},
    "btn_del": {"en": "Delete Set", "ja": "セットを削除"},
    "input_preset": {"en": "Enter set name:", "ja": "セット名を入力:"},
    "folder_section": {"en": "<b>Image Folders</b>", "ja": "<b>画像フォルダ構成</b>"},
    "folder_hint_label": {"en": "📂 Drag & Drop folders here to add", "ja": "📂 ここにフォルダをドラッグ＆ドロップして追加"},
    "btn_add_folder": {"en": "Add Folder", "ja": "フォルダ追加"},
    "btn_remove_folder": {"en": "Remove Selected", "ja": "選択フォルダを削除"},
    "empty_folder_bg": {"en": "DROP FOLDERS HERE", "ja": "ここにフォルダを\n投げ込んでください"},
    "move_section": {"en": "<b>'Move & Skip' Destination</b>", "ja": "<b>'移動してスキップ' の保存先</b>"},
    "btn_select_move": {"en": "Select Folder...", "ja": "フォルダを選択..."},
    "no_move_folder": {"en": "(Not set - will ask on first use)", "ja": "(未設定 - 初回使用時に尋ねます)"},
    "step_section": {"en": "<b>Session Steps</b>", "ja": "<b>セッション構成</b>"},
    "btn_add_step": {"en": "+ Add Step", "ja": "＋ 工程を追加"},
    "btn_start": {"en": "START SESSION", "ja": "セッション開始"},
    "lang_toggle": {"en": "日本語にする", "ja": "English"},
    "lbl_count": {"en": "Count:", "ja": "枚数:"},
    "lbl_time": {"en": "Time:", "ja": "時間:"},
    "suffix_count": {"en": " imgs", "ja": " 枚"},
    "suffix_min": {"en": " m", "ja": " 分"},
    "suffix_sec": {"en": " s", "ja": " 秒"},
    "infinite": {"en": "Inf (∞)", "ja": "無限 (∞)"},
    
    # Viewer Text
    "btn_pause": {"en": "Pause (Space)", "ja": "一時停止 (Space)"},
    "btn_skip": {"en": "Skip (S)", "ja": "スキップ (S)"},
    "btn_move": {"en": "Move Image", "ja": "画像を別フォルダに移動"}, # Changed
    "btn_stop": {"en": "Quit (Esc)", "ja": "終了 (Esc)"},
    "loading": {"en": "Loading...", "ja": "読み込み中..."},
    
    # Status Display (New Format)
    # {0}=Time, {1}=Current, {2}=Total
    "step_fmt": {"en": "{}s Set - Image {} / {}", "ja": "{}秒セット - {} / {} 枚目"},
    "step_fmt_inf": {"en": "{}s Set - Image {} (∞)", "ja": "{}秒セット - {} 枚目 (∞)"},
    
    "next_fmt": {"en": "Next: [ {}s x {} ]", "ja": "次: [ {}秒 x {} ]"},
    "next_finish": {"en": "Next: Finish", "ja": "次: 終了"},
    
    "tab_completed": {"en": "Completed", "ja": "完了した画像"},
    "tab_skipped": {"en": "Skipped", "ja": "スキップした画像"},
    "result_msg": {"en": "<b>Session Complete!</b>", "ja": "<b>セッション終了！</b>"},
    "result_stats": {"en": "Finished: {} | Skipped: {}", "ja": "完了: {} 枚 | スキップ: {} 枚"},
    "result_hint": {"en": "Click thumbnail to review.", "ja": "サムネイルをクリックで拡大表示"},
    "btn_back_config": {"en": "Back to Config", "ja": "設定画面に戻る"},
    "tt_lang": {"en": "Switch to Japanese", "ja": "英語に切り替え"},
    "msg_error": {"en": "Error", "ja": "エラー"},
    "msg_info": {"en": "Info", "ja": "情報"},
    "msg_no_folder": {"en": "No checked folders found.", "ja": "有効な画像フォルダがありません。"},
    "msg_no_step": {"en": "No steps configured.", "ja": "工程が設定されていません。"},
    "msg_no_img": {"en": "No images found.", "ja": "画像が見つかりません。"},
    "msg_moved": {"en": "Image moved to:\n{}", "ja": "画像を移動しました:\n{}"},
    "msg_move_fail": {"en": "Failed to move image.", "ja": "画像の移動に失敗しました。"},
    "select_move_target": {"en": "Select destination folder", "ja": "移動先のフォルダを選択してください"},
}

# --- 統計管理クラス ---
class ImageStatsManager:
    def __init__(self):
        self.stats = {}
        self.load_stats()

    def load_stats(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except:
                self.stats = {}

    def save_stats(self):
        try:
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_count(self, path):
        return self.stats.get(path, 0)

    def increment_count(self, path):
        self.stats[path] = self.stats.get(path, 0) + 1
        self.save_stats()

    def select_next_image(self, image_pool, current_image_path=None):
        if not image_pool: return None
        pool_counts = {path: self.get_count(path) for path in image_pool}
        min_count = min(pool_counts.values())
        candidates = [path for path, count in pool_counts.items() if count == min_count]
        
        if len(candidates) > 1 and current_image_path in candidates:
            candidates = [p for p in candidates if p != current_image_path]
        
        return random.choice(candidates)

stats_manager = ImageStatsManager()

# --- 設定管理クラス ---
class AppConfigManager:
    def __init__(self):
        self.config = {
            "window_size": [1000, 800],
            "language": "en",
            "last_preset_data": None,
            "last_set_name": "Custom",
            "always_on_top": False,
            "move_target_folder": "" 
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config.update(data)
            except:
                pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass

config_manager = AppConfigManager()

# --- 共通ヘルパー関数 ---
def get_image_files(folders):
    image_paths = []
    for folder_data in folders:
        if not folder_data["checked"]: continue
        path = folder_data["path"]
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS:
                        image_paths.append(os.path.join(root, file))
    return image_paths

# --- UI部品: ドラッグ＆ドロップ対応リスト ---
class FolderListWidget(QListWidget):
    folders_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.placeholder_text = ""
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def set_placeholder(self, text):
        self.placeholder_text = text
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0 and self.placeholder_text:
            painter = QPainter(self.viewport())
            painter.save()
            col = self.palette().color(self.foregroundRole())
            col.setAlpha(80)
            painter.setPen(col)
            font = painter.font()
            font.setPointSize(20)
            font.setBold(True)
            painter.setFont(font)
            
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.placeholder_text)
            painter.restore()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                paths.append(path)
        if paths:
            self.folders_dropped.emit(paths)

# --- UI部品: セッション行 ---
class SessionStepRow(QWidget):
    def __init__(self, count=10, duration=30, parent=None):
        super().__init__(parent)
        self.current_lang = "en"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_count = QLabel()
        self.spin_count = QSpinBox()
        self.spin_count.setRange(0, 9999) 
        self.spin_count.setValue(count)
        
        self.lbl_time = QLabel()
        self.spin_min = QSpinBox()
        self.spin_min.setRange(0, 60)
        self.spin_sec = QSpinBox()
        self.spin_sec.setRange(0, 59)
        
        mins, secs = divmod(duration, 60)
        self.spin_min.setValue(mins)
        self.spin_sec.setValue(secs)

        btn_delete = QPushButton("×")
        btn_delete.setFixedSize(30, 30)
        btn_delete.clicked.connect(self.delete_row)

        layout.addWidget(self.lbl_count)
        layout.addWidget(self.spin_count)
        layout.addWidget(self.lbl_time)
        layout.addWidget(self.spin_min)
        layout.addWidget(self.spin_sec)
        layout.addWidget(btn_delete)
        
        self.update_language(config_manager.config["language"])

    def delete_row(self):
        self.setParent(None)
        self.deleteLater()

    def get_data(self):
        total_seconds = (self.spin_min.value() * 60) + self.spin_sec.value()
        if total_seconds < 1: total_seconds = 1
        return {"count": self.spin_count.value(), "duration": total_seconds}

    def update_language(self, lang):
        self.current_lang = lang
        self.lbl_count.setText(TEXTS["lbl_count"][lang])
        self.lbl_time.setText(TEXTS["lbl_time"][lang])
        self.spin_count.setSuffix(TEXTS["suffix_count"][lang])
        self.spin_min.setSuffix(TEXTS["suffix_min"][lang])
        self.spin_sec.setSuffix(TEXTS["suffix_sec"][lang])
        self.spin_count.setSpecialValueText(TEXTS["infinite"][lang])

class ConfigWidget(QWidget):
    start_requested = pyqtSignal(dict)
    lang_changed = pyqtSignal(str)
    on_top_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.presets = {}
        self.current_lang = config_manager.config["language"]
        self.layout = QVBoxLayout(self)
        
        # --- Header ---
        header_layout = QHBoxLayout()
        
        self.btn_ontop = QPushButton("📌 Always on Top")
        self.btn_ontop.setCheckable(True)
        self.btn_ontop.setChecked(config_manager.config.get("always_on_top", False))
        self.btn_ontop.clicked.connect(self.toggle_always_on_top)
        self.btn_ontop.setStyleSheet("QPushButton:checked { background-color: #FFA500; color: white; }")
        
        header_layout.addWidget(self.btn_ontop)
        header_layout.addStretch()
        
        self.btn_lang = QPushButton()
        self.btn_lang.setFixedWidth(120)
        self.btn_lang.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.btn_lang)
        self.layout.addLayout(header_layout)

        # --- Session Set ---
        preset_layout = QHBoxLayout()
        self.lbl_preset = QLabel()
        self.combo_presets = QComboBox()
        self.combo_presets.addItem("Custom", "custom_marker")
        self.combo_presets.currentTextChanged.connect(self.load_preset)
        self.btn_save = QPushButton()
        self.btn_save.clicked.connect(self.save_current_preset)
        self.btn_del = QPushButton()
        self.btn_del.clicked.connect(self.delete_preset)
        
        preset_layout.addWidget(self.lbl_preset)
        preset_layout.addWidget(self.combo_presets, 1)
        preset_layout.addWidget(self.btn_save)
        preset_layout.addWidget(self.btn_del)
        self.layout.addLayout(preset_layout)
        self.layout.addWidget(QLabel("<hr>"))

        # --- Folders ---
        self.lbl_folder_hint = QLabel()
        self.lbl_folder_hint.setStyleSheet("font-size: 14px; font-weight: bold; color: #555; margin-top: 10px;")
        
        self.lbl_folder_sec = QLabel()
        
        self.folder_list = FolderListWidget()
        self.folder_list.folders_dropped.connect(self.handle_dropped_folders)
        
        folder_btn_layout = QHBoxLayout()
        self.btn_add_folder = QPushButton()
        self.btn_add_folder.clicked.connect(self.add_folder_dialog)
        self.btn_remove_folder = QPushButton()
        self.btn_remove_folder.clicked.connect(self.remove_selected_folder)
        
        folder_btn_layout.addWidget(self.btn_add_folder)
        folder_btn_layout.addWidget(self.btn_remove_folder)
        
        self.layout.addWidget(self.lbl_folder_sec)
        self.layout.addWidget(self.lbl_folder_hint)
        self.layout.addWidget(self.folder_list)
        self.layout.addLayout(folder_btn_layout)
        self.layout.addWidget(QLabel("<hr>"))

        # --- Move Target Settings ---
        move_layout = QHBoxLayout()
        self.lbl_move_sec = QLabel()
        self.lbl_move_path = QLabel()
        self.lbl_move_path.setStyleSheet("color: #666; font-style: italic;")
        self.btn_select_move = QPushButton()
        self.btn_select_move.clicked.connect(self.select_move_folder)
        
        move_layout.addWidget(self.lbl_move_sec)
        move_layout.addWidget(self.btn_select_move)
        
        self.layout.addLayout(move_layout)
        self.layout.addWidget(self.lbl_move_path)
        self.layout.addWidget(QLabel("<hr>"))

        # --- Steps ---
        self.lbl_step_sec = QLabel()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.steps_container = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_container)
        self.steps_layout.addStretch()
        scroll.setWidget(self.steps_container)
        self.layout.addWidget(self.lbl_step_sec)
        self.layout.addWidget(scroll)

        self.btn_add_step = QPushButton()
        self.btn_add_step.clicked.connect(lambda: self.add_step_row())
        self.layout.addWidget(self.btn_add_step)

        # --- Start ---
        self.btn_start = QPushButton()
        self.btn_start.setFixedHeight(50)
        self.btn_start.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;")
        self.btn_start.clicked.connect(self.request_start)
        self.layout.addWidget(self.btn_start)

        # Initialization
        self.load_presets_from_file()
        last_set_name = config_manager.config.get("last_set_name", "Custom")
        index = self.combo_presets.findText(last_set_name)
        if index >= 0:
            self.combo_presets.setCurrentIndex(index)
        else:
            self.combo_presets.setCurrentIndex(0)
            last_data = config_manager.config.get("last_preset_data")
            if last_data:
                self.restore_state(last_data)
        
        if self.steps_layout.count() == 1:
            self.add_step_row(10, 30)
            self.add_step_row(10, 60)
            self.add_step_row(5, 180)

        self.update_ui_text()
        self.update_move_path_label()

    def toggle_always_on_top(self):
        state = self.btn_ontop.isChecked()
        config_manager.config["always_on_top"] = state
        self.on_top_toggled.emit(state)

    def toggle_language(self):
        self.current_lang = "ja" if self.current_lang == "en" else "en"
        config_manager.config["language"] = self.current_lang
        self.lang_changed.emit(self.current_lang)
        self.update_ui_text()

    def update_ui_text(self):
        lang = self.current_lang
        self.btn_lang.setText(TEXTS["lang_toggle"][lang])
        self.btn_ontop.setText(TEXTS["always_top"][lang])
        self.lbl_preset.setText(TEXTS["preset_label"][lang])
        
        idx = self.combo_presets.findData("custom_marker")
        if idx != -1:
            self.combo_presets.setItemText(idx, TEXTS["custom_setting"][lang])

        self.btn_save.setText(TEXTS["btn_save"][lang])
        self.btn_del.setText(TEXTS["btn_del"][lang])
        
        self.lbl_folder_sec.setText(TEXTS["folder_section"][lang])
        self.lbl_folder_hint.setText(TEXTS["folder_hint_label"][lang])
        self.folder_list.set_placeholder(TEXTS["empty_folder_bg"][lang])
        
        self.btn_add_folder.setText(TEXTS["btn_add_folder"][lang])
        self.btn_remove_folder.setText(TEXTS["btn_remove_folder"][lang])
        
        self.lbl_move_sec.setText(TEXTS["move_section"][lang])
        self.btn_select_move.setText(TEXTS["btn_select_move"][lang])
        self.update_move_path_label()

        self.lbl_step_sec.setText(TEXTS["step_section"][lang])
        self.btn_add_step.setText(TEXTS["btn_add_step"][lang])
        self.btn_start.setText(TEXTS["btn_start"][lang])

        for i in range(self.steps_layout.count()):
            widget = self.steps_layout.itemAt(i).widget()
            if isinstance(widget, SessionStepRow):
                widget.update_language(lang)

    def update_move_path_label(self):
        path = config_manager.config.get("move_target_folder", "")
        if path:
            self.lbl_move_path.setText(path)
        else:
            self.lbl_move_path.setText(TEXTS["no_move_folder"][self.current_lang])

    def select_move_folder(self):
        folder = QFileDialog.getExistingDirectory(self, TEXTS["btn_select_move"][self.current_lang])
        if folder:
            config_manager.config["move_target_folder"] = folder
            config_manager.save_config()
            self.update_move_path_label()

    def request_start(self):
        data = self.get_current_state()
        checked_folders = [f for f in data['folders'] if f['checked']]
        lang = self.current_lang
        if not checked_folders:
            QMessageBox.warning(self, TEXTS["msg_error"][lang], TEXTS["msg_no_folder"][lang])
            return
        if not data['steps']:
            QMessageBox.warning(self, TEXTS["msg_error"][lang], TEXTS["msg_no_step"][lang])
            return
        
        # 開始時に設定を保存
        config_manager.config["last_preset_data"] = data
        config_manager.config["last_set_name"] = self.combo_presets.currentText()
        config_manager.save_config()
        self.start_requested.emit(data)

    def add_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder: self.add_folder_item(folder, checked=True)
    
    def handle_dropped_folders(self, paths):
        for path in paths:
            self.add_folder_item(path, checked=True)

    def add_folder_item(self, path, checked=True):
        items = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        if path in items: return
        item = QListWidgetItem(path)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.folder_list.addItem(item)

    def remove_selected_folder(self):
        row = self.folder_list.currentRow()
        if row >= 0:
            self.folder_list.takeItem(row)

    def add_step_row(self, count=10, duration=30):
        row = SessionStepRow(count, duration)
        row.update_language(self.current_lang)
        self.steps_layout.insertWidget(self.steps_layout.count()-1, row)

    def clear_steps(self):
        while self.steps_layout.count() > 1:
            child = self.steps_layout.itemAt(0).widget()
            if child: child.setParent(None); child.deleteLater()

    def get_current_state(self):
        folders = []
        for i in range(self.folder_list.count()):
            item = self.folder_list.item(i)
            folders.append({"path": item.text(), "checked": item.checkState() == Qt.CheckState.Checked})
        steps = []
        for i in range(self.steps_layout.count() - 1):
            widget = self.steps_layout.itemAt(i).widget()
            if isinstance(widget, SessionStepRow): steps.append(widget.get_data())
        return {"folders": folders, "steps": steps}

    def restore_state(self, data):
        self.folder_list.clear()
        for f in data.get("folders", []):
            self.add_folder_item(f["path"], f["checked"])
        self.clear_steps()
        for s in data.get("steps", []):
            self.add_step_row(s["count"], s["duration"])

    def save_current_preset(self):
        lang = self.current_lang
        name, ok = QInputDialog.getText(self, TEXTS["btn_save"][lang], TEXTS["input_preset"][lang])
        if ok and name:
            self.presets[name] = self.get_current_state()
            self.save_presets_to_file()
            self.update_preset_combo(name)

    def load_preset(self, name):
        # 変更された瞬間に現在の選択を記憶
        config_manager.config["last_set_name"] = name
        config_manager.save_config()

        if self.combo_presets.currentIndex() == 0: 
            return
        if name not in self.presets: return
        data = self.presets[name]
        self.restore_state(data)

    def delete_preset(self):
        name = self.combo_presets.currentText()
        if name in self.presets:
            del self.presets[name]
            self.save_presets_to_file()
            self.update_preset_combo()

    def update_preset_combo(self, select_name=None):
        self.combo_presets.blockSignals(True)
        self.combo_presets.clear()
        self.combo_presets.addItem("Custom", "custom_marker")
        self.combo_presets.addItems(list(self.presets.keys()))
        if select_name: self.combo_presets.setCurrentText(select_name)
        else: self.combo_presets.setCurrentIndex(0)
        self.update_ui_text() 
        self.combo_presets.blockSignals(False)

    def save_presets_to_file(self):
        with open(PRESET_FILE, 'w', encoding='utf-8') as f: json.dump(self.presets, f, ensure_ascii=False, indent=2)

    def load_presets_from_file(self):
        if os.path.exists(PRESET_FILE):
            with open(PRESET_FILE, 'r', encoding='utf-8') as f: self.presets = json.load(f)
            self.update_preset_combo()

class ViewerWidget(QWidget):
    finished = pyqtSignal(list, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_lang = "en"
        self.layout = QVBoxLayout(self)
        
        # 背景色をダークグレーに設定
        self.setStyleSheet("background-color: #333; color: white;")
        
        info_layout = QHBoxLayout()
        self.lbl_step_info = QLabel("Step 1")
        self.lbl_step_info.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        # 次のステップ表示用ラベル
        self.lbl_next_step = QLabel("")
        self.lbl_next_step.setStyleSheet("color: #AAA; font-size: 14px; margin-left: 10px;")
        
        self.lbl_timer = QLabel("00:00")
        self.lbl_timer.setStyleSheet("font-size: 24px; font-weight: bold; color: white;") # 白文字
        
        info_layout.addWidget(self.lbl_step_info)
        info_layout.addWidget(self.lbl_next_step)
        info_layout.addStretch()
        info_layout.addWidget(self.lbl_timer)
        self.layout.addLayout(info_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: 2px solid grey; border-radius: 5px; } QProgressBar::chunk { background-color: #4CAF50; }")
        self.layout.addWidget(self.progress_bar)

        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setStyleSheet("background-color: #222;") # 画像エリアはさらに暗く
        self.lbl_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.lbl_image, 1)

        control_layout = QHBoxLayout()
        self.btn_pause = QPushButton()
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_pause.setStyleSheet("color: black; background-color: #EEE;") # ボタンは見やすく
        
        self.btn_move = QPushButton()
        self.btn_move.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.btn_move.clicked.connect(self.move_and_skip)
        
        self.btn_skip = QPushButton()
        self.btn_skip.clicked.connect(self.skip_image)
        self.btn_skip.setStyleSheet("color: black; background-color: #EEE;")
        
        self.btn_stop = QPushButton()
        self.btn_stop.clicked.connect(self.stop_session)
        self.btn_stop.setStyleSheet("color: black; background-color: #EEE;")
        
        control_layout.addWidget(self.btn_pause)
        control_layout.addWidget(self.btn_move)
        control_layout.addWidget(self.btn_skip)
        control_layout.addWidget(self.btn_stop)
        self.layout.addLayout(control_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        
        self.folders = []
        self.steps = []
        self.image_pool = []
        self.history = []
        self.skipped_history = []
        self.current_step_index = 0
        self.images_done_in_step = 0
        self.time_left = 0
        self.total_step_time = 0
        self.is_paused = False
        self.current_image_path = ""
        
        self.update_ui_text()

    def update_ui_text(self):
        lang = self.current_lang
        self.btn_pause.setText(TEXTS["btn_pause"][lang])
        self.btn_move.setText(TEXTS["btn_move"][lang])
        self.btn_skip.setText(TEXTS["btn_skip"][lang])
        self.btn_stop.setText(TEXTS["btn_stop"][lang])
        if not self.history and not self.image_pool:
             self.lbl_image.setText(TEXTS["loading"][lang])

    def start_session(self, folders, steps, lang):
        self.current_lang = lang
        self.update_ui_text()
        
        self.folders = folders
        self.steps = steps
        self.image_pool = get_image_files(folders)
        self.history = []
        self.skipped_history = []
        self.current_step_index = 0
        self.images_done_in_step = 0
        self.is_paused = False
        
        if not self.image_pool:
            QMessageBox.critical(self, TEXTS["msg_error"][lang], TEXTS["msg_no_img"][lang])
            self.finished.emit([], [])
            return

        self.setFocus()
        self.start_step()

    def update_status_label(self):
        step = self.steps[self.current_step_index]
        count_str = str(step['count'])
        current_img_num = self.images_done_in_step + 1
        
        if step['count'] == 0:
            # 無限モード
            fmt = TEXTS["step_fmt_inf"][self.current_lang]
            self.lbl_step_info.setText(fmt.format(step['duration'], current_img_num))
        else:
            # 通常モード
            fmt = TEXTS["step_fmt"][self.current_lang]
            self.lbl_step_info.setText(fmt.format(step['duration'], current_img_num, count_str))

    def start_step(self):
        if self.current_step_index >= len(self.steps):
            self.finish_session()
            return

        step = self.steps[self.current_step_index]
        self.images_done_in_step = 0
        
        # 現在のステップ表示更新
        self.update_status_label()
        
        # 次のステップ表示
        next_idx = self.current_step_index + 1
        if next_idx < len(self.steps):
            next_step = self.steps[next_idx]
            next_fmt = TEXTS["next_fmt"][self.current_lang]
            next_count_str = str(next_step['count']) if next_step['count'] > 0 else "∞"
            self.lbl_next_step.setText(next_fmt.format(next_step['duration'], next_count_str))
        else:
            self.lbl_next_step.setText(TEXTS["next_finish"][self.current_lang])

        self.load_next_image()

    def load_next_image(self):
        if not self.image_pool:
            self.finish_session()
            return

        next_path = stats_manager.select_next_image(self.image_pool, self.current_image_path)
        self.current_image_path = next_path
        
        pixmap = QPixmap(self.current_image_path)
        if pixmap.isNull():
            if self.current_image_path in self.image_pool:
                self.image_pool.remove(self.current_image_path)
            self.load_next_image()
            return

        self.current_pixmap = pixmap
        self.update_image_scale()
        
        step = self.steps[self.current_step_index]
        self.total_step_time = step['duration'] * 10
        self.time_left = self.total_step_time
        
        self.progress_bar.setStyleSheet("QProgressBar { border: 2px solid grey; border-radius: 5px; } QProgressBar::chunk { background-color: #4CAF50; }") 
        self.progress_bar.setMaximum(self.time_left)
        self.progress_bar.setValue(self.time_left)
        self.update_timer_display()
        self.timer.start(100)

    def update_image_scale(self):
        if hasattr(self, 'current_pixmap') and not self.current_pixmap.isNull():
            w = self.lbl_image.width()
            h = self.lbl_image.height()
            if w > 0 and h > 0:
                scaled = self.current_pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.lbl_image.setPixmap(scaled)

    def resizeEvent(self, event):
        self.update_image_scale()
        super().resizeEvent(event)

    def tick(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.progress_bar.setValue(self.time_left)
            self.update_timer_display()
            
            if self.time_left / self.total_step_time <= 0.1:
                 self.progress_bar.setStyleSheet("QProgressBar { border: 2px solid grey; border-radius: 5px; } QProgressBar::chunk { background-color: #ff4444; }")
            
            if self.time_left in [30, 20, 10]:
                QApplication.beep()
                
        else:
            self.image_finished()

    def update_timer_display(self):
        total_sec = (self.time_left // 10) + 1
        mins, secs = divmod(total_sec, 60)
        self.lbl_timer.setText(f"{mins:02d}:{secs:02d} ({total_sec}s)")

    def image_finished(self):
        self.timer.stop()
        self.history.append(self.current_image_path)
        stats_manager.increment_count(self.current_image_path)
        
        self.images_done_in_step += 1
        step = self.steps[self.current_step_index]
        
        # 完了チェック
        if step['count'] > 0 and self.images_done_in_step >= step['count']:
            self.current_step_index += 1
            self.start_step()
        else:
            # まだこのステップが続くなら、枚数表示を更新して次へ
            self.update_status_label()
            self.load_next_image()

    def skip_image(self):
        self.timer.stop()
        self.skipped_history.append(self.current_image_path)
        self.load_next_image()

    def move_and_skip(self):
        self.timer.stop()
        target_dir = config_manager.config.get("move_target_folder")
        
        if not target_dir or not os.path.isdir(target_dir):
            target_dir = QFileDialog.getExistingDirectory(self, TEXTS["select_move_target"][self.current_lang])
            if target_dir:
                config_manager.config["move_target_folder"] = target_dir
                config_manager.save_config()
            else:
                self.timer.start()
                return

        src = self.current_image_path
        filename = os.path.basename(src)
        dst = os.path.join(target_dir, filename)
        
        try:
            if os.path.exists(dst):
                base, ext = os.path.splitext(filename)
                count = 1
                while os.path.exists(dst):
                    dst = os.path.join(target_dir, f"{base}_{count}{ext}")
                    count += 1
            
            shutil.move(src, dst)
            
            if src in self.image_pool:
                self.image_pool.remove(src)
            
            self.skipped_history.append(dst)
            self.load_next_image()
            
        except Exception as e:
            QMessageBox.critical(self, TEXTS["msg_error"][self.current_lang], str(e))
            self.timer.start()

    def toggle_pause(self):
        if self.is_paused:
            self.timer.start()
            self.is_paused = False
            self.lbl_timer.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        else:
            self.timer.stop()
            self.is_paused = True
            self.lbl_timer.setStyleSheet("font-size: 24px; font-weight: bold; color: red;")

    def stop_session(self):
        self.timer.stop()
        self.finished.emit(self.history, self.skipped_history)

    def finish_session(self):
        self.timer.stop()
        self.finished.emit(self.history, self.skipped_history)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.toggle_pause()
        elif event.key() == Qt.Key.Key_S:
            self.skip_image()
        elif event.key() == Qt.Key.Key_Escape:
            self.stop_session()

class ReviewWidget(QWidget):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setStyleSheet("background-color: #000;")
        self.layout.addWidget(self.lbl_image)

    def show_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.current_pixmap = pixmap
            self.update_scale()

    def update_scale(self):
        if hasattr(self, 'current_pixmap'):
            scaled = self.current_pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_image.setPixmap(scaled)

    def resizeEvent(self, event):
        self.update_scale()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        self.clicked.emit()

class ResultWidget(QWidget):
    back_requested = pyqtSignal()
    review_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_lang = "en"
        self.layout = QVBoxLayout(self)
        
        self.lbl_msg = QLabel()
        self.lbl_hint = QLabel()
        self.layout.addWidget(self.lbl_msg)
        self.layout.addWidget(self.lbl_hint)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.btn_back = QPushButton()
        self.btn_back.clicked.connect(self.back_requested.emit)
        self.layout.addWidget(self.btn_back)

    def create_thumbnail_grid(self, paths):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        row, col = 0, 0
        max_cols = 4
        
        for path in paths:
            if not os.path.exists(path): continue
            
            btn = QPushButton()
            btn.setFixedSize(200, 200)
            btn.setStyleSheet("border: none; background-color: #eee;")
            
            reader = QImageReader(path)
            if reader.size().width() > 200:
                reader.setScaledSize(QSize(200, 200))
            img = reader.read()
            
            if not img.isNull():
                icon = QIcon(QPixmap.fromImage(img))
                btn.setIcon(icon)
                btn.setIconSize(QSize(190, 190))
                btn.clicked.connect(lambda checked, p=path: self.review_requested.emit(p))
                
                grid.addWidget(btn, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        scroll.setWidget(container)
        return scroll

    def set_results(self, history, skipped, lang):
        self.current_lang = lang
        self.update_ui_text()
        
        self.lbl_msg.setText(TEXTS["result_stats"][lang].format(len(history), len(skipped)))
        
        self.tabs.clear()
        self.tabs.addTab(self.create_thumbnail_grid(history), TEXTS["tab_completed"][lang])
        self.tabs.addTab(self.create_thumbnail_grid(skipped), TEXTS["tab_skipped"][lang])

    def update_ui_text(self):
        lang = self.current_lang
        self.lbl_hint.setText(TEXTS["result_hint"][lang])
        self.btn_back.setText(TEXTS["btn_back_config"][lang])

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "icon.png")
        else:
            icon_path = "icon.png"

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.resize(*config_manager.config["window_size"])
        self.setWindowTitle(TEXTS["app_title"][config_manager.config["language"]])
        
        if config_manager.config.get("always_on_top", False):
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.config_screen = ConfigWidget()
        self.viewer_screen = ViewerWidget()
        self.result_screen = ResultWidget()
        self.review_screen = ReviewWidget()

        self.stack.addWidget(self.config_screen) 
        self.stack.addWidget(self.viewer_screen) 
        self.stack.addWidget(self.result_screen) 
        self.stack.addWidget(self.review_screen) 

        self.config_screen.start_requested.connect(self.go_to_viewer)
        self.config_screen.lang_changed.connect(self.change_language)
        self.config_screen.on_top_toggled.connect(self.toggle_always_on_top)
        
        self.viewer_screen.finished.connect(self.go_to_result)
        self.result_screen.back_requested.connect(self.go_to_config)
        self.result_screen.review_requested.connect(self.go_to_review)
        self.review_screen.clicked.connect(self.back_to_result)

    def toggle_always_on_top(self, checked):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def change_language(self, lang):
        self.setWindowTitle(TEXTS["app_title"][lang])
        self.config_screen.update_ui_text()
        self.viewer_screen.current_lang = lang
        self.result_screen.current_lang = lang

    def go_to_viewer(self, data):
        self.viewer_screen.start_session(data['folders'], data['steps'], self.config_screen.current_lang)
        self.stack.setCurrentIndex(1)

    def go_to_result(self, history, skipped):
        self.result_screen.set_results(history, skipped, self.config_screen.current_lang)
        self.stack.setCurrentIndex(2)

    def go_to_review(self, path):
        self.review_screen.show_image(path)
        self.stack.setCurrentIndex(3)

    def back_to_result(self):
        self.stack.setCurrentIndex(2)

    def go_to_config(self):
        self.stack.setCurrentIndex(0)

    def closeEvent(self, event):
        config_manager.config["window_size"] = [self.width(), self.height()]
        config_manager.save_config()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
