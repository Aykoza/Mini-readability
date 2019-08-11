import os
home_dir = os.getcwd()
os.system('pip install virtualenv')
os.system('virtualenv -p python3 venv')
os.system('venv/bin/pip install -r requirements.txt')
