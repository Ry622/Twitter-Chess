#
# Shahir Chowdhury
# 2017-01-21
# This program manages a twitter bot to handle the twitter side of TwitterChess
#
# TO DO:
#	Methods:	update - Get new tweets and store in moves or games
#				getMoves - return moves if not empty else false (move must 4 to 5 characters long)
#				getGames - return games if not empty else false
#				sendMessage - Sends a message (takes in a string s)
#
#	Features: 	Ignore irrelavant tweets referencing realtwitChess
#				Calling self starts an AI game
#				Timestamping games to know latest board between two people
#
# 	Bonus:		Error messages for invalid actions
#				Game Displaying
#				Refresh Option

import tweepy
from time import sleep
from random import *
from Player import *
from game import *

#Authorizing information to control account
consumer_key = 	"Hw1ZVEq1fnCNg6Ru1DT0vteFn"
consumer_secret = "8fAShyc2IRusJ1Qv0KbX75TiVzYpv85vjEohR7aHKj2X6ZL6cV"

access_token = "822614698692591617-bt7zcInR2qu8AyIO7ZeyKlWEQyQJC1O"
access_token_secret = "ghdZ9yTND1pDncpMa3Xd1B50iucoXGKPgd0FrZC2KPztU"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
auth.secure = True #Stay safe and secure
api = tweepy.API(auth) #authorize the tweepy API
#wait_on_rate_limit=True
thisBot = api.get_user(screen_name = "@RealTwitChess")

stat = ""

#
# Objective: Creates an object that manages input and output from twitter
# Input: A list to store moves in active games and a list to store games preparing to be made
# Output: Can post statuses or supply other objects with the games and moves list it stores
#
class Input:
	def __init__ (self,moves,games):
		self.moves = moves
		self.games = games
		
	#
	# Objective: Scans twitter feeds for mentions of the twitterchess bot and records relevant actions
	# Input: None
	# Output: Stores new games and planned moves 
	#
	def update(self):
		myStreamListener = MyStreamListener()
		myStream = tweepy.Stream(auth = api.auth, listener = myStreamListener)
		myStream.filter(track = ["@realtwitchess"])

		#print api.rate_limit_status()
		# for tweet in tweepy.Cursor(api.search, q = '@realtwitchess ', count = 200, result_type = "recent",lang = ' ').pages():
		# 	print api.rate_limit_status()
		# 	try:
		# 		print (tweet.text)
		# 		text = str(tweet.text)

		# 		textparts = str.split(text) #convert tweet into string array to disect

		# 		for x, string in enumerate(textparts): 
		# 			if (x < len(textparts)-1): #prevents error that arises with an incomplete call of the twitter bot to start a game
		# 				if string == "gamestart" and textparts[x+1][:1] == "@": #find games
		# 					otheruser = api.get_user(screen_name = textparts[2][1:]) #drop the @ sign (although it might not matter)
		# 					self.games.append((tweet.user.id,otheruser.id))
		# 			elif (len(textparts[x]) == 4): #find moves
		# 				newMove = Move(tweet.user.id,string)
		# 				self.moves.append(newMove)
		# 		if tweet.user.id == thisBot.id: #ignore self tweets
		# 			continue
		# 			sleep(900)
		# 	except tweepy.TweepError as e: 
		# 		print(e.reason)	
		# 		if e.response is not None and e.response.status in set([401, 404]):
		# 			continue
		# 	except StopIteration: #stop iteration when last tweet is reached
		# 		break

	def getMoves(self): #returns the list of moves in active games
		return self.moves

	def getGames(self): #returns the list of games waiting to be made
		return self.games

#
# Objective: Scans twitter feeds for mentions of the twitterchess bot and records relevant actions
# Input: None
# Output: Stores new games and planned moves 
#
def sendMessage(s, ID1 = None, ID2 = None): #writes a status, mentioning 1, 2 or no other users
	if not ID1 and not ID2: #No person to be mentioned
		api.update_status(s)

	elif ID1 and not ID2: #Only one person is mentioned
		user = api.get_user(ID1)   
		try:
			api.update_status("@" + user.screen_name + "\n" + s)
		except tweepy.TweepError as e:
			print("Damn: " + str(e.message))
			pass

	elif ID1 and ID2: #Two people are mentioned
		user = api.get_user(ID1)  
		user2 = api.get_user(ID2)
		try:
			print("@" + user.screen_name + "@" + user2.screen_name + "\n" + s)
			api.update_status("@" + user.screen_name + "@" + user2.screen_name + " " + s)
		except tweepy.TweepError as e:
			print("Damn")
			print(e.message)
			pass
#
# Objective: Send a direct message to one of the bot's followers
# Input: A string(the message) and the recipient's ID. It is assumed that the player is following the bot 
# Output: The recipient is messaged hte desired message
#
def sendDM(s, ID):
	new_followers = api.followers(thisBot) #must check to see if recipient is follower first
	for i in new_followers:
		if i.id == ID: #check if the recipient id matches one of the bot's followers
			api.send_direct_message(ID, text = s)

#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
	def __init__ (self):
		self.games = []
		self.api = api

	def on_status(self, status):
		new_game = False
		text = str(status.text)
		textparts = str.split(text) #convert tweet into string array to disect
		user = status.user
		print user.id
		for x, string in enumerate(textparts): 
			if (x < len(textparts)-1): #prevents error that arises with an incomplete call of the twitter bot to start a game
				if string == "gamestart" and textparts[x+1][:1] == "@": #find games
					new_game = True
					otheruser = api.get_user(screen_name = textparts[2][1:]) #drop the @ sign (although it might not matter)
					print otheruser.id
				elif (len(textparts[1]) == 4 or len(textparts[1]) == 2): #find moves
				 		m = Move(status.user.id, textparts[1])

		if new_game:
			print("New game starting")
			p1 = Player(user.id, True)
			p2 = Player(otheruser.id, False)

			self.games.append(Game(p1, p2))

			print(self.games[len(self.games) - 1].getBoard().legal_moves)

			sendDM(str(self.games[len(self.games) - 1].getBoard()), p1.getName())
			sendDM(str(self.games[len(self.games) - 1].getBoard()), p2.getName())
			#sendMessage(str(self.games[len(self.games) - 1].getBoard()), p1.getName())
			#sendMessage(str(self.games[len(self.games) - 1].getBoard()), p2.getName())
			##sendMessage("@dschana2 Test", p1.getName(), p2.getName())

		else:
			print("Moving")
			for g in range(len(self.games)):
				print("Move: " + str(m.getMove()))
				b = self.games[g].updateBoard(m.getMove())
				if b == "Invalid move":
					sendMessage(b, self.games[g].getPlayer(1, True).getName(), self.games[g].getPlayer(2, True).getName())
				else:
					sendDM(b, self.games[g].getPlayer(1, True).getName())
					sendDM(b, self.games[g].getPlayer(2, True).getName())
			'''
			for g in range(len(self.games)):
				p = self.games[g].getPlayer(m.getID())
				if p != -1:  # Check if either player is one of the tweeters
					if p.isTurn():
						b = self.games[g].updateBoard(m.getMove())  # update found game with new move
						if b == "Invalid move":
							sendDM(b, p.getName())
						else:
							sendDM(b, self.games[g].getPlayer(1, True).getName())
							sendDM(b, self.games[g].getPlayer(2, True).getName())
					else:
						sendDM(b, p.getName())
			'''

		new_game = False

		print(status.text)

	def on_error(self, status_code):
		if status_code == 420:
			#returning False in on_error disconnects the stream
			return False
        # returning non-False reconnects the stream, with backoff.

class Move: #object contains the ID of the player and the move they are to make
	def __init__ (self,playerID,move):
		self.playerID = playerID
		self.move = move

	def getID(self):
		return self.playerID

	def getMove(self):
		return self.move

moveslist = []
gameslist = []
test = Input(moveslist, gameslist)
#sendDM("Wake upppp pleaseeee!",735128411874689024)
#test.update()
while True:
	test.update()
