# PC tracker - client
#### About
PC tracker - client is project that focuses on recording activity that happens on PC Windows OS.
#####Currently it tracks:
- local ip address of PC in use
- name of user that has logged in
- what application were in use
- title of those applications
- how much time did user spend on per application
- how much time did user spend in idle state during that time on app and idle periods (time and date + duration)
#####Data can be saved:
- on local PC where data is gathering
- inside local network on some shared network folder
- currently it doesn't support saving activity data on remote pc that is not part of your local network
#### Setup and install
1. If you don not have Python 3 installed, please do that first. I'm using 3.7 version at this moment.
2. Install virtualenv library if you didn't already. You can do that by writing following line in command line ```pip3.7 install virtualenv```. Be sure to change the version number on pip to the version number of python that you have installed.
3. Deploy virtual environment ```py -3.7 -m virtualenv Envs/myproject```. By default location should be ```C:\Users\NameOfUserThatIsLoggedIn\Envs```.
4. Activate virtual environment that should be on location where you deployed virtual environment. it should be something like ```C:\Users\NameOfUserThatIsLoggedIn\Envs\myproject\Scripts\activate.bat```.
5. Install pc_tracker using pip