@echo off
py -m pip install -r requirements.txt
py make_dataset.py
py build_analysis_ml.py
py make_cover.py
py ml\predict.py
echo Done - open dashboard_preview\index.html
pause
