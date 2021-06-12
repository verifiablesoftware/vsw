#!/bin/bash
rm -rf dist
python setup.py sdist bdist_wheel
cd dist
pip3 uninstall -y $(ls | grep .whl)
pip3 install $(ls | grep .whl)
cd ..
twine upload dist/*
