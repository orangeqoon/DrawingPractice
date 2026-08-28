
# Custom Gesture Drawing App（日本語説明は下記）

A desktop application designed for efficient gesture drawing and figure study practice using your local image collections.
Fully offline, customizable, and optimized for artists who want to focus on drawing.

![Main Screen](images/main.png)

## 🎨 Features


* **Local Folder Support**: Use your own reference images stored on your PC. No cloud upload required.
* **Flexible Session Structure**: Create custom routines like "30sec x 10 images" followed by "2min x 5 images".
* **Smart Shuffle**: The app tracks view counts for each image. It prioritizes showing images you haven't seen yet or have seen the least, ensuring a fresh experience every session.
* **Preset Management**: Save and load your favorite folder combinations and time settings instantly.
* **Review Mode**: At the end of a session, review all the images you drew in a thumbnail grid. Click to zoom in.
* **Bilingual Interface**: Toggle between English and Japanese with a single click.

## 📸 Screenshots

| Configuration |
| :---: |
| ![<img width="800" height="800" alt="image" src="https://github.com/user-attachments/assets/cbba2937-fce0-4785-b8ed-2851cd29263b" />) |

| Results | 
| :---: |
| ![Result](<img width="2126" height="1987" alt="image" src="https://github.com/user-attachments/assets/b62f5727-f374-4282-b669-2faece8f3bb3" />
) | ![Review](images/review.png) |


## ⚡ Quick Start (Windows Standalone EXE)

**No Python installation required!**
* Double-click **`GestureApp.exe`** (or **`起動する.bat`**) to launch immediately.
* Everything is self-contained in a single executable.

### 🛠 Building from Source (Optional)
If you want to build the EXE yourself:
1. Double-click `build.bat`
2. Or run via terminal:
   ```bash
   pip install PyQt6 pyinstaller Pillow
   pyinstaller --noconfirm --onefile --windowed --name "GestureApp" --icon "icon.ico" --add-data "icon.png;." gesture_app.py
   ```

## 🚀 How to Use

### 1. Setup
1.  Click **Add Folder** to select directories containing your reference images. Check/uncheck boxes to include specific folders.
2.  Click **+ Add Step** to define the session flow.
    * **Count**: Number of images (Set to `0` for Infinite Mode).
    * **Time**: Duration per image (Minutes/Seconds).
3.  (Optional) Click **Save** to store your current configuration as a preset.
4.  Click **START SESSION**.

### 2. During Session
* **Space**: Pause / Resume timer.
* **S**: Skip current image (Does not count towards the session goal).
* **Esc**: Quit session early and go to the result screen.

### 3. Review
* After the session (or upon pressing Esc), a summary screen appears.
* Click any thumbnail to view the image in full size.
* Click the full-size image to return to the grid.


# Custom Gesture Drawing App (ジェスチャードローイング練習ツール)


自分好みの画像フォルダと時間設定で、効率的にジェスチャードローイング（クロッキー）の練習ができるデスクトップアプリです。
Windows/Mac/Linuxで動作し、完全にオフラインで動作します。

![Main Screen](images/main.png)


## 🎨 特徴 (Features)

* **ローカル画像対応**: 自分のPCにある画像フォルダを指定して練習できます。クラウドへのアップロードは不要です。
* **柔軟なセッション設定**: 「30秒×10枚 → 1分×5枚 → 無制限」のように、好きな工程を組み合わせてプリセット保存できます。
* **スマートシャッフル機能**: 画像の表示回数を記録し、**「まだ見ていない画像」や「見る頻度が少ない画像」を優先的に表示**します。セッションをまたいでも記録は保持されます。
* **レビューモード**: 練習終了後、描いた画像のサムネイル一覧が表示され、クリックで拡大して復習できます。
* **多言語対応**: 日本語と英語をワンクリックで切り替え可能です。

## 📸 スクリーンショット

| 設定画面 | ビューアー |
| :---: | :---: |
| ![<img width="2192" height="1998" alt="image" src="https://github.com/user-attachments/assets/6fcff8e5-6080-4c0c-a33f-d5d173020f51" />) | ![Viewer](images/viewer.png) |
| **フォルダ選択・時間設定・プリセット保存** | **残り時間バー・一時停止機能** |

| リザルト画面 | レビュー画面 |
| :---: | :---: |
| ![<img width="2126" height="1987" alt="image" src="https://github.com/user-attachments/assets/2aec61b1-eeb3-405f-bb12-9e2baa8c0c83" />
) | ![Review](images/review.png) |
| **練習した画像の一覧確認** | **クリックで拡大表示** |






## ⚡ 簡単起動（Windows EXE版・インストール不要）

**Pythonやライブラリのインストールは不要です！**
* **`GestureApp.exe`**（または **`起動する.bat`**）をダブルクリックするだけで、すぐにアプリが起動します。
* 必要なファイルが1つのEXEにまとめられているため、誰でも簡単に利用可能です。

### 🛠 ソースコードからのEXE作成手順（開発者向け）
自身でEXEファイルを再ビルドしたい場合は、以下のいずれかで作成できます：
1. **`build.bat`** をダブルクリックして実行
2. またはコマンドラインで以下を実行：
   ```bash
   pip install PyQt6 pyinstaller Pillow
   pyinstaller --noconfirm --onefile --windowed --name "GestureApp" --icon "icon.ico" --add-data "icon.png;." gesture_app.py
   ```

## 🚀 使い方 (Usage)

### 1. 起動と設定
1.  **Add Folder** ボタンで、練習用画像が入っているフォルダを追加します（複数可）。チェックボックスで有効/無効を切り替えられます。
2.  **Add Step** ボタンで、セッションの構成を追加します。
    * **Count**: 画像の枚数（0にすると無限モード）
    * **Time**: 1枚あたりの表示時間（分・秒）
3.  (任意) **Save** ボタンで現在の設定をプリセットとして保存できます。
4.  **START SESSION** で開始します。

### 2. ドローイング中
* **Space**: 一時停止 / 再開
* **S**: 画像をスキップ（カウントは進みません）
* **Esc**: セッションを終了してリザルト画面へ

### 3. 終了後
* 表示されたサムネイルをクリックすると、拡大画像で確認できます。
* 拡大画面をクリックすると、一覧に戻ります。
