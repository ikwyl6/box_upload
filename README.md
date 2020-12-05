## box_upload
A simple python script that uses OAuth 2.0 to upload a file to your box.com account.

## Script Setup
1. Copy the config.json template to your home directory (```~/.box_config```) and ```chmod 600 ~/.box_config```
2. Run ```pip install -r requirements.txt``` which will install ```boxsdk``` for you which is required. 
3. Log into your box.com account:
	- Go to Dev Console
	- Create a New App
	- Choose 'Custom App'
	- Authentication Method: Choose 'User Authentication (OAuth 2.0)'
	- App Name: Create a name for your app. This can be 'box_upload'
4. On the 'Configuration' of your newly created app on box.com you will find your 'Client ID' and 'Client Secret'. Put these values in the 'client_id' and 'client_secret' fields in the ```~/.box_config``` file.
5. For the 'Redirect URI' field, change 'app.box.com' to 'localhost'

NOTE: If you change the location of your config file to be other than ```~/.box.config``` then you will need to change ```config_file``` variable in the python script.

## First Time Use
1. The first time you use the script it will output a link on the command line. Copy this link and paste it in your browser. This is how you will get your authentication and refresh tokens.
2. After pasting this link you will then be prompted to log into box.com using your box.com account credentials.
3. Choose 'Grant Access to Box' on the next page
4. It will then bring you to a link in your browser that will probably be 'not found' or 'This site can't be reached'. In the address bar of your browser of this 'not found' link, copy the value of the ```code``` variable (everything after the 'code=' portion of the url). 
5. Paste the value of this into the script.

NOTE: You will only have to do the above steps once. 

## Normal Usage
1. Run ```./box_upload -h``` to see options. 
NOTE: You will need to specify the remote directory that exists for the location of the file you are uploading. Otherwise it uploads the file to the root directory on box.com ('/All Files/').

## Examples of usage
```
./box_upload file
```

This uploads ```file``` to your ```/All Files/``` directory on box.com

```./box_upload -d "/All Files/Documents" /home/user/my_local_file``` 
	- uploads ```my_local_file``` to ```/All Files/Documents``` on box.com

```./box_upload -u file``` 
	- uploads (updates with new version) ```file``` to box.com. If no ```-u``` is given then script will exit without uploading ```file``` 
