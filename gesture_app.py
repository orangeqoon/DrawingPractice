import sys
import json
import os
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QListWidgetItem, QSpinBox, QComboBox, QFileDialog, 
                             QScrollArea, QMessageBox, QInputDialog, QProgressBar,
                             QGridLayout, QStackedWidget, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QImageReader, QIcon

# --- 定数・設定 ---
PRESET_FILE = "session_presets.json"
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

# --- 言語リソース辞書 ---
TEXTS = {
    "app_title": {"en": "Gesture Drawing App", "ja": "ジェスチャードローイング"},
    
    # Config Screen
    "preset_label": {"en": "Preset:", "ja": "プリセット:"},
    "custom_setting": {"en": "Custom Settings", "ja": "カスタム設定"},
    "btn_save": {"en": "Save", "ja": "保存"},
    "btn_del": {"en": "Delete", "ja": "削除"},
    "folder_section": {"en": "<b>Image Folders</b>", "ja": "<b>画像フォルダ構成</b>"},
    "btn_add_folder": {"en": "Add Folder", "ja": "フォルダを追加"},
    "step_section": {"en": "<b>Session Steps</b>", "ja": "<b>セッション構成</b>"},
    "btn_add_step": {"en": "+ Add Step", "ja": "＋ 工程を追加"},
    "btn_start": {"en": "START SESSION", "ja": "セッション開始"},
    "lang_toggle": {"en": "日本語", "ja": "English"}, # ボタンに表示する「切り替え先」の言語
    
    # Session Step Row
    "lbl_count": {"en": "Count:", "ja": "枚数:"},
    "lbl_time": {"en": "Time:", "ja": "時間:"},
    "suffix_count": {"en": " imgs", "ja": " 枚"},
    "suffix_min": {"en": " m", "ja": " 分"},
    "suffix_sec": {"en": " s", "ja": " 秒"},
    "infinite": {"en": "Inf (∞)", "ja": "無限 (∞)"},
    
    # Viewer
    "btn_pause": {"en": "Pause (Space)", "ja": "一時停止 (Space)"},
    "btn_skip": {"en": "Skip (S)", "ja": "別画像へ (S)"},
    "btn_stop": {"en": "Quit (Esc)", "ja": "終了 (Esc)"},
    "loading": {"en": "Loading...", "ja": "読み込み中..."},
    "step_fmt": {"en": "Step {}/{} - [ {}s x {} ]", "ja": "工程 {}/{} - [ {}秒 x {} ]"},
    
    # Result
    "result_msg": {"en": "<b>Session Complete! {} drawings finished.</b>", "ja": "<b>お疲れ様でした！ {} 枚のドローイングが完了しました。</b>"},
    "result_hint": {"en": "Click thumbnail to review. Click image to return.", "ja": "クリックで拡大表示。画像クリックで一覧に戻ります。"},
    "btn_back_config": {"en": "Back to Config", "ja": "設定画面に戻る"},
    
    # Tooltips
    "tt_preset": {"en": "Save or load your folder/time settings.", "ja": "フォルダや時間の構成を保存・読み込みします。"},
    "tt_folder": {"en": "Check folders to include in this session.", "ja": "今回のセッションで使用するフォルダにチェックを入れてください。"},
    "tt_step_count": {"en": "Set 0 for infinite mode.", "ja": "0に設定すると手動で止めるまで続きます（無限モード）。"},
    "tt_step_time": {"en": "Time limit per image.", "ja": "画像1枚あたりの表示時間です。"},
    "tt_lang": {"en": "Switch Language", "ja": "言語を切り替えます"},
    
    # Messages
    "msg_error": {"en": "Error", "ja": "エラー"},
    "msg_no_folder": {"en": "No checked folders found.", "ja": "有効な画像フォルダが選択されていません。"},
    "msg_no_step": {"en": "No steps configured.", "ja": "セッション工程が設定されていません。"},
    "msg_no_img": {"en": "No images found in folders.", "ja": "選択されたフォルダに画像が見つかりません。"},
    "msg_img_gone": {"en": "No more images.", "ja": "画像がなくなりました。"},
    "input_preset": {"en": "Enter preset name:", "ja": "プリセット名を入力:"},
}

# --- 共通ヘルパー関数 ---
def get_image_files(folders):
    """画像収集ロジック"""
    image_paths = []
    for folder_data in folders:
        if not folder_data["checked"]:
            continue
        path = folder_data["path"]
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS:
                        image_paths.append(os.path.join(root, file))
    return image_paths

# --- UI部品クラス ---

class SessionStepRow(QWidget):
    """設定画面の1行（分・秒対応）"""
    def __init__(self, count=10, duration=30, parent=None):
        super().__init__(parent)
        self.current_lang = "en"
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 枚数
        self.lbl_count = QLabel()
        self.spin_count = QSpinBox()
        self.spin_count.setRange(0, 9999) 
        self.spin_count.setValue(count)
        
        # 時間 (分)
        self.lbl_time = QLabel()
        self.spin_min = QSpinBox()
        self.spin_min.setRange(0, 60)
        
        # 時間 (秒)
        self.spin_sec = QSpinBox()
        self.spin_sec.setRange(0, 59)
        
        # 初期値セット（秒を分:秒に変換）
        mins, secs = divmod(duration, 60)
        self.spin_min.setValue(mins)
        self.spin_sec.setValue(secs)

        # 削除ボタン
        btn_delete = QPushButton("×")
        btn_delete.setFixedSize(30, 30)
        btn_delete.clicked.connect(self.delete_row)

        layout.addWidget(self.lbl_count)
        layout.addWidget(self.spin_count)
        layout.addWidget(self.lbl_time)
        layout.addWidget(self.spin_min)
        layout.addWidget(self.spin_sec)
        layout.addWidget(btn_delete)
        
        self.update_language(self.current_lang)

    def delete_row(self):
        self.setParent(None)
        self.deleteLater()

    def get_data(self):
        # 分と秒を合計して秒で返す
        total_seconds = (self.spin_min.value() * 60) + self.spin_sec.value()
        # 0秒設定は事故防止のため最低1秒にする
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
        
        # Tooltips
        self.spin_count.setToolTip(TEXTS["tt_step_count"][lang])
        self.spin_min.setToolTip(TEXTS["tt_step_time"][lang])
        self.spin_sec.setToolTip(TEXTS["tt_step_time"][lang])

class ConfigWidget(QWidget):
    """設定画面"""
    start_requested = pyqtSignal(dict)
    lang_changed = pyqtSignal(str) # 言語変更シグナル

    def __init__(self, parent=None):
        super().__init__(parent)
        self.presets = {}
        self.current_lang = "en" # Default English
        self.layout = QVBoxLayout(self)
        
        # --- Header (Language Toggle) ---
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.btn_lang = QPushButton("日本語")
        self.btn_lang.setFixedWidth(80)
        self.btn_lang.clicked.connect(self.toggle_language)
        header_layout.addWidget(self.btn_lang)
        self.layout.addLayout(header_layout)

        # --- Preset Area ---
        preset_layout = QHBoxLayout()
        self.lbl_preset = QLabel()
        self.combo_presets = QComboBox()
        self.combo_presets.addItem("Custom")
        self.combo_presets.currentTextChanged.connect(self.load_preset)
        self.combo_presets.setToolTip(TEXTS["tt_preset"]["en"])
        
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

        # --- Folder Area ---
        self.lbl_folder_sec = QLabel()
        self.folder_list = QListWidget()
        self.folder_list.setToolTip(TEXTS["tt_folder"]["en"])
        self.btn_add_folder = QPushButton()
        self.btn_add_folder.clicked.connect(self.add_folder_dialog)
        self.layout.addWidget(self.lbl_folder_sec)
        self.layout.addWidget(self.folder_list)
        self.layout.addWidget(self.btn_add_folder)
        self.layout.addWidget(QLabel("<hr>"))

        # --- Steps Area ---
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

        # --- Start Button ---
        self.btn_start = QPushButton()
        self.btn_start.setFixedHeight(50)
        self.btn_start.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white;")
        self.btn_start.clicked.connect(self.request_start)
        self.layout.addWidget(self.btn_start)

        self.load_presets_from_file()
        if self.steps_layout.count() == 1:
            self.add_step_row(10, 30)
            
        self.update_ui_text()

    def toggle_language(self):
        self.current_lang = "ja" if self.current_lang == "en" else "en"
        self.lang_changed.emit(self.current_lang) # Mainへ通知して全画面更新

    def update_ui_text(self):
        lang = self.current_lang
        # Labels & Buttons
        self.btn_lang.setText(TEXTS["lang_toggle"][lang])
        self.btn_lang.setToolTip(TEXTS["tt_lang"][lang])
        
        self.lbl_preset.setText(TEXTS["preset_label"][lang])
        self.combo_presets.setItemText(0, TEXTS["custom_setting"][lang])
        self.btn_save.setText(TEXTS["btn_save"][lang])
        self.btn_del.setText(TEXTS["btn_del"][lang])
        self.lbl_folder_sec.setText(TEXTS["folder_section"][lang])
        self.btn_add_folder.setText(TEXTS["btn_add_folder"][lang])
        self.lbl_step_sec.setText(TEXTS["step_section"][lang])
        self.btn_add_step.setText(TEXTS["btn_add_step"][lang])
        self.btn_start.setText(TEXTS["btn_start"][lang])
        
        # Tooltips
        self.combo_presets.setToolTip(TEXTS["tt_preset"][lang])
        self.folder_list.setToolTip(TEXTS["tt_folder"][lang])

        # 子ウィジェット（工程行）も更新
        for i in range(self.steps_layout.count()):
            widget = self.steps_layout.itemAt(i).widget()
            if isinstance(widget, SessionStepRow):
                widget.update_language(lang)

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
        self.start_requested.emit(data)

    def add_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder: self.add_folder_item(folder, checked=True)

    def add_folder_item(self, path, checked=True):
        items = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        if path in items: return
        item = QListWidgetItem(path)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.folder_list.addItem(item)

    def add_step_row(self, count=10, duration=30):
        row = SessionStepRow(count, duration)
        row.update_language(self.current_lang) # 追加時に言語適用
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

    def save_current_preset(self):
        lang = self.current_lang
        name, ok = QInputDialog.getText(self, TEXTS["btn_save"][lang], TEXTS["input_preset"][lang])
        if ok and name:
            self.presets[name] = self.get_current_state()
            self.save_presets_to_file()
            self.update_preset_combo(name)

    def load_preset(self, name):
        if self.combo_presets.currentIndex() == 0 or name not in self.presets: return
        data = self.presets[name]
        self.folder_list.clear()
        for f in data["folders"]: self.add_folder_item(f["path"], f["checked"])
        self.clear_steps()
        for s in data["steps"]: self.add_step_row(s["count"], s["duration"])

    def delete_preset(self):
        name = self.combo_presets.currentText()
        if name in self.presets:
            del self.presets[name]
            self.save_presets_to_file()
            self.update_preset_combo()

    def update_preset_combo(self, select_name=None):
        self.combo_presets.blockSignals(True)
        self.combo_presets.clear()
        self.combo_presets.addItem("Custom") # Text will be updated by update_ui_text
        self.combo_presets.addItems(list(self.presets.keys()))
        if select_name: self.combo_presets.setCurrentText(select_name)
        else: self.combo_presets.setCurrentIndex(0)
        self.update_ui_text() # Re-apply language
        self.combo_presets.blockSignals(False)

    def save_presets_to_file(self):
        with open(PRESET_FILE, 'w', encoding='utf-8') as f: json.dump(self.presets, f, ensure_ascii=False, indent=2)

    def load_presets_from_file(self):
        if os.path.exists(PRESET_FILE):
            with open(PRESET_FILE, 'r', encoding='utf-8') as f: self.presets = json.load(f)
            self.update_preset_combo()

class ViewerWidget(QWidget):
    """描画実行画面"""
    finished = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_lang = "en"
        self.layout = QVBoxLayout(self)
        
        info_layout = QHBoxLayout()
        self.lbl_step_info = QLabel("Step 1")
        self.lbl_timer = QLabel("00:00")
        self.lbl_timer.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        info_layout.addWidget(self.lbl_step_info)
        info_layout.addStretch()
        info_layout.addWidget(self.lbl_timer)
        self.layout.addLayout(info_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.layout.addWidget(self.progress_bar)

        self.lbl_image = QLabel()
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setStyleSheet("background-color: #222;")
        self.lbl_image.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.lbl_image, 1)

        control_layout = QHBoxLayout()
        self.btn_pause = QPushButton()
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_skip = QPushButton()
        self.btn_skip.clicked.connect(self.skip_image)
        self.btn_stop = QPushButton()
        self.btn_stop.clicked.connect(self.stop_session)
        control_layout.addWidget(self.btn_pause)
        control_layout.addWidget(self.btn_skip)
        control_layout.addWidget(self.btn_stop)
        self.layout.addLayout(control_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        
        self.folders = []
        self.steps = []
        self.image_pool = []
        self.history = []
        self.current_step_index = 0
        self.images_done_in_step = 0
        self.time_left = 0
        self.is_paused = False
        self.current_image_path = ""
        
        self.update_ui_text()

    def update_ui_text(self):
        lang = self.current_lang
        self.btn_pause.setText(TEXTS["btn_pause"][lang])
        self.btn_skip.setText(TEXTS["btn_skip"][lang])
        self.btn_stop.setText(TEXTS["btn_stop"][lang])
        self.lbl_image.setText(TEXTS["loading"][lang])

    def start_session(self, folders, steps, lang):
        """セッション開始"""
        self.current_lang = lang
        self.update_ui_text()
        
        self.folders = folders
        self.steps = steps
        self.image_pool = get_image_files(folders)
        self.history = []
        self.current_step_index = 0
        self.images_done_in_step = 0
        self.is_paused = False
        
        if not self.image_pool:
            QMessageBox.critical(self, TEXTS["msg_error"][lang], TEXTS["msg_no_img"][lang])
            self.finished.emit([])
            return

        random.shuffle(self.image_pool)
        self.setFocus()
        self.start_step()

    def start_step(self):
        if self.current_step_index >= len(self.steps):
            self.finish_session()
            return

        step = self.steps[self.current_step_index]
        self.images_done_in_step = 0
        count_str = str(step['count']) if step['count'] > 0 else "∞"
        
        fmt = TEXTS["step_fmt"][self.current_lang]
        self.lbl_step_info.setText(fmt.format(self.current_step_index + 1, len(self.steps), step['duration'], count_str))
        
        self.load_next_image()

    def load_next_image(self):
        if not self.image_pool:
            self.finish_session()
            return

        next_path = random.choice(self.image_pool)
        if len(self.image_pool) > 1 and next_path == self.current_image_path:
            next_path = random.choice(self.image_pool)
        self.current_image_path = next_path
        
        pixmap = QPixmap(self.current_image_path)
        if pixmap.isNull():
            self.load_next_image()
            return

        self.current_pixmap = pixmap
        self.update_image_scale()
        
        step = self.steps[self.current_step_index]
        self.time_left = step['duration'] * 10
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
        else:
            self.image_finished()

    def update_timer_display(self):
        seconds = (self.time_left // 10) + 1
        self.lbl_timer.setText(f"{seconds} s")

    def image_finished(self):
        self.timer.stop()
        self.history.append(self.current_image_path)
        self.images_done_in_step += 1
        step = self.steps[self.current_step_index]
        if step['count'] > 0 and self.images_done_in_step >= step['count']:
            self.current_step_index += 1
            self.start_step()
        else:
            self.load_next_image()

    def skip_image(self):
        self.timer.stop()
        self.load_next_image()

    def toggle_pause(self):
        if self.is_paused:
            self.timer.start()
            self.is_paused = False
            self.lbl_timer.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        else:
            self.timer.stop()
            self.is_paused = True
            self.lbl_timer.setStyleSheet("font-size: 24px; font-weight: bold; color: red;")

    def stop_session(self):
        self.timer.stop()
        self.finished.emit(self.history)

    def finish_session(self):
        self.timer.stop()
        self.finished.emit(self.history)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.toggle_pause()
        elif event.key() == Qt.Key.Key_S:
            self.skip_image()
        elif event.key() == Qt.Key.Key_Escape:
            self.stop_session()

class ReviewWidget(QWidget):
    """【新機能】画像を全画面で確認する画面"""
    clicked = pyqtSignal() # クリックされたらリザルトに戻る

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
        """画面クリックで戻る"""
        self.clicked.emit()

class ResultWidget(QWidget):
    """リザルト画面（サムネイル一覧）"""
    back_requested = pyqtSignal()
    review_requested = pyqtSignal(str) # 画像クリック時にフル表示をリクエスト

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_lang = "en"
        self.layout = QVBoxLayout(self)
        
        self.lbl_msg = QLabel()
        self.lbl_hint = QLabel()
        self.layout.addWidget(self.lbl_msg)
        self.layout.addWidget(self.lbl_hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self.container)
        self.layout.addWidget(scroll)

        self.btn_back = QPushButton()
        self.btn_back.clicked.connect(self.back_requested.emit)
        self.layout.addWidget(self.btn_back)

    def set_history(self, history, lang):
        self.current_lang = lang
        self.update_ui_text()
        self.lbl_msg.setText(TEXTS["result_msg"][lang].format(len(history)))
        
        # サムネイル生成
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        row, col = 0, 0
        max_cols = 4
        
        for path in history:
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
                # クリックしたらReview画面へ遷移するシグナルを出す
                btn.clicked.connect(lambda checked, p=path: self.review_requested.emit(p))
                
                self.grid.addWidget(btn, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def update_ui_text(self):
        lang = self.current_lang
        self.lbl_hint.setText(TEXTS["result_hint"][lang])
        self.btn_back.setText(TEXTS["btn_back_config"][lang])

# --- メインウィンドウ ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(TEXTS["app_title"]["en"])
        self.resize(1000, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 4つの画面：Config(0) -> Viewer(1) -> Result(2) <-> Review(3)
        self.config_screen = ConfigWidget()
        self.viewer_screen = ViewerWidget()
        self.result_screen = ResultWidget()
        self.review_screen = ReviewWidget()

        self.stack.addWidget(self.config_screen) # 0
        self.stack.addWidget(self.viewer_screen) # 1
        self.stack.addWidget(self.result_screen) # 2
        self.stack.addWidget(self.review_screen) # 3

        # シグナル接続
        self.config_screen.start_requested.connect(self.go_to_viewer)
        self.config_screen.lang_changed.connect(self.change_language) # 言語変更
        self.viewer_screen.finished.connect(self.go_to_result)
        self.result_screen.back_requested.connect(self.go_to_config)
        
        # リザルト -> レビュー -> リザルト のループ
        self.result_screen.review_requested.connect(self.go_to_review)
        self.review_screen.clicked.connect(self.back_to_result)

    def change_language(self, lang):
        self.setWindowTitle(TEXTS["app_title"][lang])
        # Config画面は自身のメソッド内で既に更新済み
        # 他の画面は表示時に更新されるか、ここで更新
        self.viewer_screen.current_lang = lang
        self.result_screen.current_lang = lang

    def go_to_viewer(self, data):
        self.viewer_screen.start_session(data['folders'], data['steps'], self.config_screen.current_lang)
        self.stack.setCurrentIndex(1)

    def go_to_result(self, history):
        self.result_screen.set_history(history, self.config_screen.current_lang)
        self.stack.setCurrentIndex(2)

    def go_to_review(self, path):
        """リザルトでクリックされた画像をフル画面表示"""
        self.review_screen.show_image(path)
        self.stack.setCurrentIndex(3)

    def back_to_result(self):
        """フル画面クリックでリザルトへ戻る"""
        self.stack.setCurrentIndex(2)

    def go_to_config(self):
        self.stack.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())