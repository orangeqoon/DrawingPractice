@echo off
chcp 65001 > nul
echo GestureApp の EXE をビルドしています...
pip install PyQt6 pyinstaller Pillow
pyinstaller --noconfirm --onefile --windowed --name "GestureApp" --icon "icon.ico" --add-data "icon.png;." gesture_app.py
copy /Y "dist\GestureApp.exe" "GestureApp.exe"
copy /Y "dist\GestureApp.exe" "GestureDrawingApp.exe"
echo.
echo ビルドが完了しました！ GestureApp.exe を実行してください。
pause
