import sys, os, re, time, argparse, getpass, praw, requests, reddit, config, wordcloud, pyimgur, json

current = {

	'credentials': {
	
		'username': '',
		'password': '',
		
	},
	
	'limit': '',
	'id': '',
	
}

replied_current {
	
	'replied:': [],
	
}

config_name = 'config.json'

def bootup():
	
	version = "1.0"
	
	parse = argparse.ArgumentParser(description = 'LinkFixerBot')
	parse.add_argument('-l', '--login', action = 'store_true', help = 'Login to a different account than config account')
	args = parse.parse_args()
	
	print('\nMWC // version ' + version)
	print('------------------')
	
	if not os.path.isfile(config_name) or os.path.isfile('replied.json'):
		
		config.write(current, config_name)
		print('> Created config.json & replied.json. Please edit the values in the config before continuing.')
		sys.exit()
		
	conf = config.load(config_name)
	
	if conf['limit'] == '':
		
		print('> The limit in the config is not set! Please set it to a proper number.')
		sys.exit()
		
	elif conf['limit'] > '50':
		
		print('> The limit in the config is over 100! Please make it a lower number.')
		sys.exit()
		
	if conf['id'] == '':
		
		print('> The id in the config is not set! Please set it to an Imgur client id.')
		sys.exit()
		
	if args.login:
		
		user = raw_input('> Reddit username: ')
		passwd = getpass.getpass("> %s's password: " % user)
		
		print
		
	else:
		
		user = conf['credentials']['username']
		passwd = conf['credentials']['password']
		
	agent = (
		'/u/' + user + ' running makeswordclouds, version ' + version + ', created by /u/WinneonSword.'
	)
	
	r = praw.Reddit(user_agent = agent)
	utils = Utils(conf, r)
	
	reddit.login(user, passwd, r)
	loop(user, r, utils)
	
def loop(user, reddit, utils):
	
	print('\n> Booting up makeswordclouds. You will be notified when makeswordclouds detects a broken link.')
	print('> To stop the bot, press Ctrl + C.')
	
	try:
		
		while True:
			
			print('\n> Checking comments for valid entries...')
			submissions = reddit.get_subreddit('all').get_hot(limit = 100)
			
			for submission in submissions:
				
				if submission.id not in utils.replied and submission.num_comments >= utils.config['limit']:
					
					print('\n> Found valid submission in the subreddit /r/' + submission.subreddit.display_name + '!')
					
					text = utils.get_submission_comments(submission.id)
					cloud = utils.make_cloud(text)
					upload = utils.upload_image(cloud)
					
					print('> Successfully made word cloud and uploaded to imgur!')
					os.remove(cloud)
					
					try:
						
						submission.add_comment(
							'Here is a word cloud of all of the comments in this thread: ' + upload + '\n\n'
							'*****\n'
							'[^source ^code](https:/github.com/WinneonSword/makeswordclouds) ^| [^contact ^developer](http://reddit.com/user/WinneonSword)'
						)
						
						print('> Comment posted! Link: ' + upload)
						utils.replied.add(submission.id)
						
						out = open(utils.replied_file, 'w')
						list = list(utils.replied)
						
						out.write(json.dumps(list))
						out.close()
						
					except:
						
						print('> Failed to post comment.')
						
			print('\n> Sleeping.')
			time.sleep(15)
			
	except KeyboardInterrupt:
		
		print('> Stopped makeswordclouds. Thank you for running this bot!')
		
	except:
		
		print('\n> An error has occured. Restarting the bot.')
		loop(reddit, config, utils)
		
class Utils:
	
	def __init__(self, config, reddit):
		
		self.out = 'cloud.png'
		self.config = config
		self.reddit = reddit
		
		self.replied_file = 'replied.json'
		resp = []
		
		if os.path.exists(self.replied_file):
			
			opened= open(self.replied_file).read()
			resp = json.loads(opened)
			
		self.replied = set(resp)
		
	def get_submission_comments(self, id):
		
		submission = reddit.get_submission(submission_id = id, comment_limit = None)
		comments = praw.helpers.flatten_tree(submisison.comments)
		text = ''
		
		for comment in comments:
			
			if isInstance(comment, praw.objects.Comment):
				
				text += comment + '\n'
				
		return text
		
	def make_cloud(self, text):
		
		words = wordcloud.process_text(text)
		elements = wordcloud.fit_words(words)
		wordcloud.draw(elements, self.out)
		
		return self.out
		
	def upload(self, file):
		
		imgur = pyimgur.Imgur(self.config['id'])
		upload = imgur.upload_image(file)
		
		return upload.link
		
bootup()