import sublime, sublime_plugin # sublime
import xmlrpclib # wordpress

class PublishCommand(sublime_plugin.TextCommand):
	r""" 
		** Pushes the curent active file to a metaweblog compatible blog **

		# blog settings
		Relies on a settings file called "sublimemarkpress.sublime-settings" using the structure:
			{
			    "xmlrpcurl": <URL to xml rpc endpoint>,
			    "username": <username>,
			    "password": <password>
			}

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

		# markdown
		If the file "markdown2.py" from the awesome repo https://github.com/trentm/python-markdown2/tree/master/lib exists, markdown is enabled

		# usage
		Currently, you need to copy this file into the sublimetext packages/user directory. Then on the file you wish to post press ctrl+' and type "view.run_command('publish')"
		
		# key mapping -> doesn't pass the view, so not sure how to do this correctly yet.
	"""
	def run(self, edit):
		# load settings
		mbURL, mbUsername, mbPassword = self.GetBlogSettings()
		header_lines = []

		# get page content
		all_lines_in_page = self.view.lines(sublime.Region(0, self.view.size()))

		# get the "header" (MB details)
		post_id, tags, status, title, has_header_content, is_markdown = self.GetHeaderContent(header_lines, all_lines_in_page)

		# get the "body" (content)
		post_content = self.GetPostBody(self.view, all_lines_in_page, is_markdown)

		body_content = self.BuildPostPayload(self.view, {"content": post_content, "title": title, "tags": tags, "status": status})

		# save to MB
		new_post_id = self.PostToBlog(self.view, mbURL, mbUsername, mbPassword, post_id, body_content)

		if not new_post_id == post_id:
			self.PrefixPostHeader(self.view, edit, new_post_id, header_lines, has_header_content)
	
	def GetBlogSettings(self):
		s = sublime.load_settings("sublimemarkpress.sublime-settings")
		return s.get("xmlrpcurl"), s.get("username"), s.get("password")

	def GetHeaderContent(self, header_lines, all_lines_in_page):
		page_info = {"has_header_content":False,"post_id":None, "tags":"", "status":"", "title":"","is_markdown":False}

		if self.view.substr(all_lines_in_page[0]).startswith("<!--"):
			page_info["has_header_content"] = True
			self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			# post_id
			if self.view.substr(all_lines_in_page[0]).startswith("#post_id"):
				page_info["post_id"] = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			#post tags
			if self.view.substr(all_lines_in_page[0]).startswith("#tags"):
				page_info["tags"] = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			#post status
			if self.view.substr(all_lines_in_page[0]).startswith("#status"):
				page_info["status"] = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			self.MoveCurrentLineToHeader(header_lines, all_lines_in_page) # removes the closing comment tag

			if self.view.substr(all_lines_in_page[0]).startswith("# "):
				page_info["title"] = self.view.substr(all_lines_in_page[0]).split("# ")[1]
				page_info["is_markdown"] = True
			else:
				title = self.view.substr(all_lines_in_page[0])

		self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

		return	page_info["post_id"], page_info["tags"], page_info["status"], page_info["title"], page_info["has_header_content"], page_info["is_markdown"]

	def MoveCurrentLineToHeader(self, header_lines, all_lines_in_page):
			header_lines.insert(len(header_lines),all_lines_in_page[0])
			all_lines_in_page.remove(all_lines_in_page[0])

	def BuildPostPayload(self, view, page_data):		
		return {"description": page_data["content"], "post_content": page_data["content"], "title": page_data["title"], "mt_keywords": page_data["tags"], "post_status": page_data["status"]}

	def GetPostBody(self, view, lines, is_markdown):
		can_markdown = False
		try: 
			import markdown2 # markdown
			can_markdown = True
		except ImportError:
			can_markdown = False

		body_content = view.substr(sublime.Region(lines[0].begin(),lines[len(lines)-1].end()))
		if is_markdown & can_markdown:
			body_content = str(markdown2.markdown(body_content))
		return body_content

	def PrefixPostHeader(self, view, edit, post_id, header_lines, has_header):
		post_header = "<!--" + '\n' + "#post_id:" + str(post_id) + '\n'

		if has_header:
			end_point = header_lines[1].begin()
			header_lines.remove(header_lines[0])
			view.replace(edit, sublime.Region(0, end_point), post_header)
		else:
			view.replace(edit, sublime.Region(0,0), post_header + "-->" + '\n')

	def PostToBlog(self, view, url, username, password, post_id, blog_content):
		proxy = xmlrpclib.ServerProxy(url)

		if post_id == None:
			post_id = proxy.metaWeblog.newPost(0, username, password, blog_content)
			print("created new:", post_id)
		else:
			proxy.metaWeblog.editPost(post_id, username, password, blog_content)
			print("updated existing:", post_id)

		return post_id
