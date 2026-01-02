#!/usr/bin/env python

# box_upload - A simple python script that uses
# OAuth 2.0 to upload a file to your box.com account.
# Author: ikwyl6@protonmail.com

from boxsdk import OAuth2, Client, BoxAPIException
from logging.handlers import SysLogHandler, logging
import os
import argparse
from sys import exit
import json
import re

# Change config_file to something that you want
config_file = os.getenv('HOME') + "/.box_config"
# Used for supressing response results on cmd line
logging.basicConfig(level=logging.CRITICAL)

# COMMAND LINE ARGUMENTS
clp = argparse.ArgumentParser(prog='box_upload',
        description='Upload file to box.com')
clp.add_argument('file', help='Local FILE to upload')
clp.add_argument('-d', '--dir', help='Remote DIR location for FILE. \
        Default: Root folder (/All Files/)')
clp.add_argument('-c', '--create', action='store_true', help='Create remote \
        DIR if not present. Default: do not create.')
clp.add_argument('-u', '--update', action='store_true',
        help='Update FILE if one already exists on box.com')
clp.add_argument('-f', '--force', action='store_true',
        help='Force \'update\' to overwrite FILE') 
clp.add_argument('-l', '--list', action='store_true',
        help='List folders in box.com account')
clargs = clp.parse_args()

# Save access_token and refresh_token to the config_file
def save_tokens(access_token, refresh_token):
    # print("save_tokens. at: " + access_token + ", rt: " + refresh_token)
    with open(config_file, 'r') as f:
        data = json.load(f)
    data['token']['access_token'] = access_token
    data['token']['refresh_token'] = refresh_token
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=4)
    os.chmod(config_file, 0o600)

# Get access_token and refresh_token from the config_file
def get_local_tokens():
    with open(config_file) as f:
        data = json.load(f)
    return data.get('token', {}).get('access_token', ""), \
            data.get('token', {}).get('refresh_token', "")

# Save the box.com client_id and client_secret to the config_file
def save_cred(client_id, client_secret):
    with open(config_file, 'r') as f:
        data = json.load(f)
    data['user']['client_id'] = client_id
    data['user']['client_secret'] = client_secret
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=4)
    os.chmod(config_file, '0600')

# get the credentials from the config_file
def get_cred():
    with open(config_file) as f:
        data = json.load(f)
    return data.get('user', {}).get('client_id', ""), \
            data.get('user', {}).get('client_secret', "")

# Get the oauth object using the client_id and client_secret
def get_oauth(cid, cs, *args):
    if (not args):
        # print("get_oauth. no access token or refresh token, only have cid,cs")
        oauth = OAuth2(
            client_id=cid,
            client_secret=cs,
            store_tokens=save_tokens,
            )
        auth_url, csrf_token = oauth.get_authorization_url('https://localhost')
        print("LINK:\n " + auth_url)
        auth_code = input("\nCopy/paste your auth code: ")
        access_token, refresh_token = oauth.authenticate(auth_code)
    else:
        access_token = args[0]
        refresh_token = args[1]
        # print("get_oauth. reusing access_token: " + access_token + ", rt: "
        #        + refresh_token)
        oauth = OAuth2(
            client_id=cid,
            client_secret=cs,
            access_token=access_token,
            refresh_token=refresh_token,
            store_tokens=save_tokens,
        )
    return oauth

# Uploads upload_f to folder with folder_id
def upload_file(upload_f, folder_id):
    # print ('upload_file')
    try:
        new_file = client.folder(folder_id).upload(upload_f)
        print('File "{0}" uploaded to Box with file ID {1}'.format(
                new_file.name, new_file.id))
    except PermissionError as e:
        print("Permission denied ({0})".format(upload_f))
    except BoxAPIException as e:
        if (e.status == 401):
            print("Access token expired. " + e.message)
        if (e.status == 409):
            # print(e.message)
            # if '--update' passed then update the file
            if (clargs.update):
                file_id = e.context_info['conflicts']['id']
                # check if file size different, if not then pass
                remote_fs = client.file(file_id).get().size
                local_fs = os.path.getsize(upload_f)
                if (local_fs != remote_fs) or \
                    ((local_fs == remote_fs) and (clargs.force)):
                    updated_file = client.file(file_id).update_contents(upload_f)
                    print('File "{0}" has been updated'.format(updated_file.name))
                else:
                    print("local and remote files ({0}) are same size. " \
                            "Skipping".format(upload_f))
            else:
                print(str(e.status) + " Error: " + e.message +
                        "({0})".format(upload_f))
                print("Use '-u' or '--update' flag to update file")
                exit(1)

# Uses folder_query to search for the destination folder using client.search()
# and then compares folder_query to the results to get the folder_id
def get_folder_id(folder_query):
    try:
        # Remove any trailing slashes if passed by user
        folder_query = re.sub(r'\/$', r'', folder_query, 1)
        results = client.search().query(query=folder_query,
                result_type='folder')
        found = False
        for item in results:
            # print("item: {0}, id: {1}".format(item.name, item.id))
            path = "/"
            for folder in item.path_collection['entries']:
                path += folder.name + "/"
            path += item.name
            # print("path: {0}, folder_query: {1}".format(path, folder_query))
            if (path.lower() == folder_query.lower()):
                return item.id
        if (not found):
            return None
        # return item.id,(path + item.name + "/")
    except UnboundLocalError:
        return None

# Create remote folder 'folder'. Used with --create
def create_folder_id(folder):
    folder = re.sub(r'.*\/', r'', folder)
    #print("new folder {0}".format(folder))
    subfolder = client.folder('0').create_subfolder(folder)
    return subfolder.id

# List directories in box.com account
def list_dirs(folder_id=0, path='/All Files/'):
    items = client.folder(folder_id).get_items(limit=50, \
            fields=['id,type,name'])
    for item in items:
        if (item.type == "folder"):
            print("{0}".format(path + item.name))
            list_dirs(item.id, path + item.name + '/')

## START ##
if (os.path.exists(config_file)):
    try:
        client_id,client_secret = get_cred()
    except json.JSONDecodeError as e:
        print("config file error: " + e.msg + ", line: " + str(e.lineno))
        exit(1)
    if (not client_id or not client_secret):
        print("No client_id or no client_secret found in {0}"
                .format(config_file))
        exit(1)
    else:
        # print("cid,cs exist..")
        access_token,refresh_token = get_local_tokens()
        if (not access_token or not refresh_token):
            # print("no at,rt - getting new ones")
            try:
                oauth = get_oauth(client_id, client_secret)
            except BoxAPIException as e:
                print(e.status + " error. " + e.message)
                exit(1)
        else:
            # print("at,rt exist - reusing..")
            try:
                oauth = get_oauth(client_id,client_secret,
                        access_token,refresh_token)
            except BoxAPIException as e:
                if (e.status == 401):
                    # Need an updated access token
                    print(e.status + " error. Retrieving new access token")
                    # TODO Is this done automatically by boxsdk?
                    # commenting out below line to see..
                    # oauth = get_oauth(c_id,c_secret)
else:
    print("{0} does not exist. Exiting.".format(config_file))
    exit(1)

client = Client(oauth)
if (clargs.list):
    list_dirs()
    exit(0)
if (clargs.file):
    upload_f = clargs.file
if (clargs.dir):
    upload_dir = clargs.dir
    folder_id = get_folder_id(upload_dir)
    if (folder_id == None):
        if (clargs.create):
            print("Folder {0} not found, creating..".format(upload_dir))
            folder_id = create_folder_id(upload_dir)
        else:
            print("Destination folder '{0}' not found".format(upload_dir))
            exit(1)
else:
    folder_id = 0

upload_file(upload_f, folder_id)
