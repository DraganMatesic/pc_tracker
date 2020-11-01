# PC tracker - client
#### About
PC tracker - client is project that focuses on recording activity that happens on PC Windows OS.<br>
##### Currently it tracks
- local ip address of PC in use
- name of user that has logged in
- what application were in use
- title of those applications
- how much time did user spend on per application
- how much time did user spend in idle state during that time on app and idle periods (time and date + duration)<br>
##### Data can be saved
- on local PC where data is gathering
- inside local network on some shared network folder
- currently it doesn't support saving activity data on remote pc that is not part of your local network
#### Installation
1. If you don not have Python 3 installed, please do that first. I'm using 3.7 version at this moment.
2. Install virtualenv library if you didn't already. You can do that by writing following line in command line ```pip3.7 install virtualenv```. Be sure to change the version number on pip to the version number of python that you have installed.
3. Deploy virtual environment ```py -3.7 -m virtualenv Envs/myproject```. By default location should be ```C:\Users\NameOfUserThatIsLoggedIn\Envs```.
4. Activate virtual environment that should be on location where you deployed virtual environment. it should be something like ```C:\Users\NameOfUserThatIsLoggedIn\Envs\myproject\Scripts\activate.bat```.
5. Install pc_tracker using ```pip install pc-tracker```
#### Setup - for Administrator 
1. Run CMD as administrator
2. Activate virtual environment same way it is explained in Installation section in step 4.
3. Enter command ```manage.py config```. As admin you will have to fill down 2 options:
    - path where the data of all pc users on local network will save data. 
    - path to main settings file where all pc users will pull latest settings admin had set
4. Save form data and you are ready for next step.
#### Setup - Client
1. Run CMD
2. Activate virtual environment same way it is explained in Installation section in step 4.
3. Enter command ```manage.py config```. After you run command and if option for specifying path to save data is visible then that user has admin privileges. 
    If you do not want to override existing path and settings you should press ```CTRL+C``` and then write command ```manage.py configcl```
4. Client with no admin privileges should be able to see only form with option to specify directory path where the global settings are located.
5. After specifying path save form data.
#### Run activity monitoring
1. Repeat steps 1 and 2 from Setup section
2. Enter command ```manage.py runclient```
3. And that's it! Data is now storing on specified location and it is ready for further processing

    