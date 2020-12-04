## box_upload
A simple python script that uses OAuth 2.0 to upload a file to box.com

## Script Setup
1. Copy the config.json template to your home directory (~/.box_config) and ```chmod 600 ~/.box_config```
2. Log into your box.com account:
	- Go to Dev Console
	- Create a New App
	- Choose 'Custom App'
	- Authentication Method: Choose 'User Authentication (OAuth 2.0)'
	- App Name: Create a name for your app. This can be 'box_upload'
3. On the 'Configuration' of your newly created app on box.com you will find your 'Client ID' and 'Client Secret'. Put these values in the 'client_id' and 'client_secret' fields in the ~/.box_config file.
4. For the 'Redirect URI' field, change 'app.box.com' to 'localhost'

NOTE: If you change the location of your config file to be other than ```~/.box.config``` then you will need to change ```config_file``` variable in the python script.

## Usage
1. Run ```./box_upload -h``` to see options. 
NOTE: You will need to specify the remote directory that exists for the location of the file you are uploading. Otherwise it uploads the file to the root directory on box.com ('/All Files/).
