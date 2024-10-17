@echo off
cd D:\dss-poi_backe
call .venv\Scripts\activate
fastapi dev
timeout /t 2 /nobreak >nul