@echo off
echo Starting Frontend...
if not exist node_modules call npm install
npm run dev
pause
