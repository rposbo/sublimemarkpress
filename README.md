#Pushes the currently active SublimeText file to a metaweblog compatible blog

## blog settings
	Relies on a settings file called "sublimemarkpress.sublime-settings" using the structure:
	{
	    "xmlrpcurl": <URL to xml rpc endpoint>,
	    "username": <username>,
	    "password": <password>
	}

## tags
	blog tags are optional at the top of the file in the structure:
	<!-- 
	#post_id:<id of existing post - optional>
	#tags:<comma delimited list of post tags - optional>
	#status:<draft or publish - optional>
	-->

## title
blog title is the first line following that section; if it starts with "#" then it's assumed
to be a markdown post

## markdown
If the file "markdown2.py" from the awesome repo https://github.com/trentm/python-markdown2/tree/master/lib exists, markdown is enabled

## usage
Currently, you need to copy this file into the sublimetext packages/user directory. Then on the file you wish to post press ctrl+' and type "view.run_command('publish')"

## key mapping
Doesn't pass the "view", so not sure how to do this correctly yet.