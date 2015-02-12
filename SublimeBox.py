__author__ = 'Brian'
print("Loading SublimeBox")

import sublime, sublime_plugin
import fnmatch
import os, sys
from os.path import join

pluginRootDirectory = os.path.dirname(__file__)

setupToolsModulePath = join(pluginRootDirectory, "setuptools-12.0.5-py2.py3-none-any.whl")
sys.path.append(setupToolsModulePath)

urlLib3ModulePath = join(pluginRootDirectory, "urllib3-1.10-py3.4.egg")
sys.path.append(urlLib3ModulePath)

dropboxModulePath = join(pluginRootDirectory, "dropbox-2.2.0-py3.4.egg")
sys.path.append(dropboxModulePath)
import dropbox

dropboxApiKey = ''
dropboxApiSecret = ''

class get_dropbox_authorization_codeCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		flow = dropbox.client.DropboxOAuth2FlowNoRedirect(dropboxApiKey, dropboxApiSecret)
		authorize_url = flow.start()
		print()
		print("Welcome to SublimeBox setup! Follow these steps to get started:")
		print("1. Go to " + authorize_url)
		print("2. Click 'Allow' (you might have to log in first)")
		print("3. Copy the authorization code.")
		print('4. Run the following from the sublime comsole: view.run_command("get_dropbox_access_token", {"authorizationCode": "<your authorization code>"})')


class get_dropbox_access_tokenCommand(sublime_plugin.TextCommand):
	
	def run(self, edit, authorizationCode):			
		flow = dropbox.client.DropboxOAuth2FlowNoRedirect(dropboxApiKey, dropboxApiSecret)
		access_token, user_id = flow.finish(authorizationCode) 
		client = dropbox.client.DropboxClient(access_token)
		print("Successfully linked account: " + client.account_info()["display_name"])
		print('1. Add the following to your settings to enable SublimeSync: "dropboxAccessToken": "' + access_token + '"')


class upload_settings_to_dropbox(sublime_plugin.TextCommand):
	
	def run(self, edit):
		access_token = self.view.settings().get('dropboxAccessToken')
		if access_token is None:
			print("Error: Dropbox access token not found. Please run GetDropboxAuthorizationCode")
			return
		
		client = dropbox.client.DropboxClient(access_token)
		settings_root_path = join(sublime.packages_path(), "User")
		for currentDirectory, dirnames, filenames in os.walk(settings_root_path):
			for filename in fnmatch.filter(filenames, '*.sublime-settings'):
				relativeDirPath = os.path.relpath(currentDirectory, settings_root_path)
				relativeFilePath = os.path.join(relativeDirPath, filename)
				fullFilePath = os.path.join(currentDirectory, filename)

				dropboxRelativeFilePath = "/" + relativeFilePath.replace("\\", "/").lstrip('./')
				print("uploading " + fullFilePath)
				print("uploading to: " + dropboxRelativeFilePath)
				file = open(fullFilePath, "rb")
				response = client.put_file(dropboxRelativeFilePath, file)
				file.close()
				print("uploaded: " + str(response))
