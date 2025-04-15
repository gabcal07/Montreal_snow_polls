#!/bin/bash
python3 -m venv env

source "env/bin/activate"

pip install -r requirements.txt

cd src

python3 ero1.py

echo "Rendez vous dans le dossier du Quartier pour obtenir l\'animation. Ou lancez le front-end avec ./front"

deactivate

rm -rf env