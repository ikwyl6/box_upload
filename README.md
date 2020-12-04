## box_upload
A simple python script that uses OAuth 2.0 to upload a file to box.com

## Script Setup
1. Copy the config.json template to your home directory (~/.box_config) and ```chmod 600 ~/.box_config```
2. Log into your box.com account
- Go to Dev Console
- Create a New App
- Custom App
- Authentication Method: Choose 'User Authentication (OAuth 2.0)'
- App Name: Create a name 'box_upload'
3. Using the 'Client ID' and 'Client Secret' from your created app screen in box.com, put these two in the 'client_id' and 'client_secret' fields in the ~/.box_config file.

NOTE: If you change the location of your config file to be other than ```~/.box.config``` then you will need to change ```config_file``` variable in the python script.

## Usage

