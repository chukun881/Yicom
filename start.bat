@echo off
title Payslip System Server
echo Starting the Payslip System...
echo Please leave this black window open while working!
echo.

:: Open the default web browser to the local server
start "" http://127.0.0.1:5000

:: Start the Python Flask server
python app.py

pause