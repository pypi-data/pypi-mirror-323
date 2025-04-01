# Installation process inside script

The scripts above run the following commands in order:

Firs installs the python module 'psyneulinkviewer' from PyPi

```
sudo pip install psyneulinkviewer
```

This commands installs required libraries and packages. Also creates a conda enviroment where the needed packages are installed.

After successfully installing the python package above, it reset the user's bash profile to apply the settings changes

- Linux

```
source ~/.profile  
```

- Mac

```
source ~/.bash_profile  
```

Then, a desktop file is created on the Desktop which allows users to open the application this way

# Psyneulinkviewer Requirements

Psyneulinkviewer requires:

- Python 3.11 and pip
- Pip packages : psyneulink, graphviz, wget, packaging and requests
- Conda 4.9.1 or above
- Node 4.19.0 or above
- Rosetta ( on Mac)

All of these are downloaded and installed as part of psyneulinkviewer installation process.

# Testing Models

If all went well with installation, you should see the application running as in screenshot below :
![image](https://github.com/user-attachments/assets/ec84044c-287a-4e39-bdf7-aa27cdc486f9)

To test models, download [these models](https://github.com/MetaCell/PsyNeuLinkView/tree/feature/PSYNEU-140/test_models) and import one at a time to test. Each time a Model is open, the previous one will disappear. I recommend you start with the models inside 'working_tests', as those are the ones we know for sure should we working.

To import go to File -> Open Models

# PsyNeuLinkView Package Building

To build pip package

```
cd package
python3 -m pip install build
python3 -m build --sdist
```

To test local build

```
pip install dist/psyneulinkviewer-VERSIOn.tar.gz
```

To upload to distribution server. You will need token shared privately to be able to upload.

```
python3 -m twine upload dist/*
```

To upload to test Pypi server

```
python3 -m twine upload --repository testpypi dist/*
```
