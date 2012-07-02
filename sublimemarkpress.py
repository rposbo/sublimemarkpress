import sublime, sublime_plugin # sublime
import xmlrpclib # wordpress

class PublishCommand(sublime_plugin.TextCommand):
	""" 
		** Pushes the curent active file to a metaweblog compatible blog **

		# blog settings
		Relies on a settings file called "sublimemarkpress.sublime-settings" using the structure:
			{
			    "xmlrpcurl": <URL to xml rpc endpoint>,
			    "username": <username.,
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
	"""
	def run(self, edit):

		can_markdown = False
		try: 
			import markdown2 # markdown
			can_markdown = True
		except ImportError:
			can_markdown = False

		# load settings
		s = sublime.load_settings("sublimemarkpress.sublime-settings")
		mbURL = s.get("xmlrpcurl")
		mbUsername = s.get("username")
		mbPassword = s.get("password")

		blog_id = 0 # not currently used on wordpress

		# get page content
		all_lines_in_page = self.view.lines(sublime.Region(0, self.view.size()))
		header_lines = []

		post_id = None
		tags = ""
		title = ""
		status = "draft"

		has_header_content = False
		# get the "header" (MB details)
		if self.view.substr(all_lines_in_page[0]).startswith("<!--"):
			has_header_content = True
			self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			# post_id
			if self.view.substr(all_lines_in_page[0]).startswith("#post_id"):
				post_id = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			#post tags
			if self.view.substr(all_lines_in_page[0]).startswith("#tags"):
				tags = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			#post status
			if self.view.substr(all_lines_in_page[0]).startswith("#status"):
				status = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

		#title
		is_markdown = False
		if self.view.substr(all_lines_in_page[0]).startswith("# "):
			title = self.view.substr(all_lines_in_page[0]).split("# ")[1]
			is_markdown = True
		else:
			title = self.view.substr(all_lines_in_page[0])

		self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

		# get the "body" (content)
		post_content = self.CombineContent(self.view, all_lines_in_page)

		# markdown content
		if is_markdown and can_markdown:
			post_content = str(markdown2.markdown(post_content))

		content = self.BuildPostContent(self.view, {"content": post_content, "title": title, "tags": tags, "status": status})

		# save to MB
		proxy = xmlrpclib.ServerProxy(mbURL)

		if post_id == None:
			post_id = proxy.metaWeblog.newPost(blog_id, mbUsername, mbPassword, content)
			self.PrefixPostHeader(self.view, edit, post_id, header_lines, has_header_content)
			print("created new:", post_id)
		else:
			proxy.metaWeblog.editPost(post_id, mbUsername, mbPassword, content)
			print("updated existing:", post_id)

	def MoveCurrentLineToHeader(self, header_lines, all_lines_in_page):
			header_lines.insert(len(header_lines),all_lines_in_page[0])
			all_lines_in_page.remove(all_lines_in_page[0])

	def BuildPostContent(self, view, page_data):		
		return {"description": page_data["content"], "post_content": page_data["content"], "title": page_data["title"], "mt_keywords": page_data["tags"], "post_status": page_data["status"]}

	def CombineContent(self, view, lines):
		return view.substr(sublime.Region(lines[0].begin(),lines[len(lines)-1].end()))

	def PrefixPostHeader(self, view, edit, post_id, header_lines, has_header):
		post_header = "<!--" + '\n' + "#post_id:" + str(post_id) + '\n'

		if has_header:
			end_point = header_lines[1].begin()
			header_lines.remove(header_lines[0])
			view.replace(edit, sublime.Region(0, end_point), post_header)
		else:
			view.replace(edit, sublime.Region(0,0), post_header + "-->" + '\n')