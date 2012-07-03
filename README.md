  	** Pushes the curent active file to a metaweblog compatible blog **

		# blog settings
		Relies on a settings file called "sublimemarkpress.sublime-settings" using the structure:
			{
			    "xmlrpcurl": <URL to xml rpc endpoint>,
			    "username": <username.,
			    "password": <password>
			}

		# key mapping
		Add an entry to Prefs -> Key Bindings - User to add a keyboard shortcut. I've used ctrl+alt+m:
		[
			{ "keys": ["ctrl+alt+m"], "command": "publish" }
		]

		# tags
		blog tags are optional at the top of the file in the structure:
		<!-- 
		#post_id:<id of existing post - optional>
		#tags:<comma delimited list of post tags - optional>
		#status:<draft or publish - optional>
		-->

		# title
		blog title is the first line following that section; if it starts with "#" then it's assumed
		to be a markdown post