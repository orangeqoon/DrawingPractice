@echo off
if exist "%~dp0GestureApp.exe" (
    start "" "%~dp0GestureApp.exe"
) else (
    start "" "%~dp0GestureDrawingApp.exe"
)
