# bot.py
import os
from random import *

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = 'NzA0MDUxMjM5NzA4NTI0NjE0.XvVpWA.gF6iqotoH_yj7-XE7yNjHA4avcc'

bot = commands.Bot(command_prefix='!')

# Enable this (set to 'True') to turn off safeguards and most order/role checks so as to allow for easier debugging
bot.debug_enable = False

bot.game_in_session = False
bot.joinable = False

# Prepares bot, and connects it to the server / creates useful objects once it is ready, as well as defining the (all-important) emojis
@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

	bot.guild = bot.get_guild(464675162243989504) #'DISCORD_GUILD' # Why doesn't these work when they're the referenced values from .env? !!!!!!!!!!
	bot.channel = bot.get_channel(704065785407995965) #'DISCORD_CHANNEL'

	bot.sh_role = bot.guild.get_role(704071282148376617) #'SECRET_HITLER_ROLE'
	bot.president_role = bot.guild.get_role(704067481408372866) #'PRESIDENT_ROLE'
	bot.chancellor_role = bot.guild.get_role(704067735595778128) #'CHANCELLOR_ROLE'

	# Define emoji names all up here (to make changing them easier)
	bot.join_emoji = "☑️"
	bot.leave_emoji = "🇽"
	bot.players_emoji = "🎮"
	bot.start_emoji = "🎲"
	bot.ja_emoji = discord.utils.get(bot.guild.emojis, name='ja')
	bot.nein_emoji = discord.utils.get(bot.guild.emojis, name='nein')
	
# Handles any errors that come up during runtime - turn off to help with debugging (this blocks errors from showing up in the console)
#@bot.event
async def on_command_error(ctx, error):
	if hasattr(ctx.command, 'on_error'):
		return
		
	ignored = (commands.CommandNotFound, commands.UserInputError)
	
	error = getattr(error, 'original', error)
	
	if isinstance(error, ignored):
		return
	
	if isinstance(error, commands.CommandNotFound):
		return
	elif isinstance(error, commands.MissingPermissions):
		missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
		if len(missing) > 2:
			fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
		else:
			fmt = ' and '.join(missing)
		_message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
		await bot.channel.send(_message)
		return
	elif isinstance(error, commands.CheckFailure):
		await bot.channel.send("You do not have permission to use this command.")
		return
	elif isinstance(error, commands.UserInputError):
		await bot.channel.send("Invalid input.")
		return
	elif isinstance(error, commands.DisabledCommand):
		await bot.channel.send('This command has been disabled.')
		return
	else:
		await bot.channel.send("The command encountered an unexpected error.")
		return

def debug_list(ctx):
	bot.players = []
	for member in ctx.message.guild.members:
		if bot.sh_role in member.roles: 
			bot.players.append(member)

# Commands for gameplay ----------------------------------------------------------------------------------------------------

# Manages all of the reaction-based gameplay (joining/leaving, voting, etc)
@bot.event
async def on_reaction_add(reaction, user): # ADD CHECK FOR "CONFLICTING" EMOJI WHEN A NEW ONE IS ADDED (LIKE JA VS NEIN), AND REMOVE THE OLD, CONFLICTING ONE - check if it's on a bot-written message, 'cuz Liam will find a way to break it otherwise
	if not user.id == bot.user.id:
		if "Check which players are in the lobby" in reaction.message.content:
			if reaction.emoji == bot.join_emoji or reaction.emoji == bot.leave_emoji:
				if not bot.game_in_session:
					if bot.joinable:
						if reaction.emoji == bot.join_emoji:
							if bot.sh_role in user.roles:
								await bot.channel.send("You\'re already part of the game!")
							else:
								await user.add_roles(bot.sh_role)
								await bot.channel.send(":white_check_mark: {} is now in the game!".format(user.mention))
								bot.players.append(user)
					
						elif reaction.emoji == bot.leave_emoji:
							if bot.sh_role in user.roles:
								await user.remove_roles(bot.sh_role)
								await user.remove_roles(bot.chancellor_role)
								await user.remove_roles(bot.president_role)
								await bot.channel.send(":white_check_mark: {} has now left the game!".format(user.mention))
								bot.players.remove(user)
							else:
								await bot.channel.send("You aren\'t part of the game yet!")		
					else:
						await bot.channel.send("A game has yet to begin / is already in progress!")
				else:
					await bot.channel.send("A game is currently underway!")
		
			elif reaction.emoji == bot.players_emoji:
				# Make this give a player count... eventually
				await bot.channel.send("This hasn\'t been implemented yet!")
				return
			
			elif reaction.emoji == bot.start_emoji:
				await start_game()
		
		elif "The game will continue once all players have voted." in reaction.message.content:
			if reaction.emoji == bot.ja_emoji or reaction.emoji == bot.nein_emoji:
				if bot.game_in_session or bot.debug_enable:
					they_have_voted = False
					if bot.voting_open:
						if bot.sh_role in user.roles:
							if user in bot.has_voted:
								they_have_voted = True
							else:
								they_have_voted = False
			
							if they_have_voted == False or bot.debug_enable:
								if reaction.emoji == bot.ja_emoji:
									bot.voted_yes += 1
									bot.votes.append('ja')
									bot.has_voted.append(user)
									await bot.channel.send("Yes recorded, {}!".format(user.mention))
								elif reaction.emoji == bot.nein_emoji:
									bot.voted_no += 1
									bot.votes.append('nein')
									bot.has_voted.append(user)
									await bot.channel.send("No recorded, {}!".format(user.mention))
								else:
									return
			
								if bot.voted_yes + bot.voted_no >= len(bot.players):
									bot.voting_open = False
							
									# I'm restating these in this weird, totally inefficient way because I can't figure out why the vote counters aren't resetting otherwise
									voted_yes = bot.voted_yes
									voted_no = bot.voted_no 
									bot.voted_yes = 0
									bot.voted_no = 0
									bot.has_voted = []
				
									await bot.channel.send("Everyone has cast their vote! Voting is now closed.")
									await bot.channel.send("There were {} \'ja\' votes, and {} \'nein\' votes.".format(voted_yes, voted_no))

									if voted_yes > voted_no:
										await bot.chancellor_nominee.add_roles(bot.chancellor_role)
										bot.current_chancellor = bot.chancellor_nominee
						
										if bot.current_chancellor == bot.hitler:
											if bot.fascist_policies_played >= 3:
												await bot.channel.send("Hitler has been elected Chancellor after 3 fascist policies had been passed! The fascists have won!!!")
												await end_game(None)
												return
								
										await bot.channel.send("The motion passed! {} is now the Chancellor!".format(bot.current_chancellor.mention))
										await bot.channel.send("When you are ready, {}, please use the \"!draw\" command to take the top three policies from the deck.".format(bot.current_president.mention))
										await bot.channel.send("They will be sent to you in a private message. Look out for the one from \"Games Bot\"!")
					
									else:
										bot.election_tracker += 1
										await bot.channel.send("The motion failed! No Chancellor has been elected, and the election tracker has increased by 1 to {} (of 3)!".format(bot.election_tracker))
										if bot.election_tracker >= 3:
											# Pass top policy
											await bot.channel.send("The election tracker has reached 3 failed elections! The top policy card on the deck has been drawn:")
											await bot.channel.send("A new {} policy has been played!".format(bot.policies[0]))
											bot.top_three.append(bot.policies[0])
											play(bot.guild, bot.policies[0]) # VERIFY THAT THIS WORKS WITH "CHANNEL" IN PLACE OF "CTX" - Evaluate function under these conditions. I don't know if it will work.
											bot.election_tracker = 0
										
										bot.has_election_increased = True
										await new_government()
										
							else:
								await bot.channel.send("You have already voted, {}!".format(message.author.mention))
						else:
							await bot.channel.send("You can\'t vote, {}, because you aren't in the game!".format(message.author.mention))
					else:
						return
@bot.event
async def on_message(message):
	if message.author == bot.user:
		if "Lobby open! Join the lobby" in message.content:
			reactions = [bot.join_emoji, bot.leave_emoji, bot.players_emoji, bot.start_emoji]
			for emoji in reactions:
				await message.add_reaction(emoji)
			
#		elif "Everyone has cast their vote! Voting is now closed." in message.content:
#			for vote in bot.votes: # This is broken... ? Maybe just in debug mode. But it definitely is in debug mode !!!!!!!!!!
#				if vote == 'ja':
#					await message.add_reaction(bot.ja_emoji)
#				elif vote == 'nein':
#					await message.add_reaction(bot.nein_emoji)
#			bot.votes = []
			
		elif "The game will continue once all players have voted." in message.content:
			reactions = [bot.ja_emoji, bot.nein_emoji]
			for emoji in reactions:
				await message.add_reaction(emoji)
			
	await bot.process_commands(message)

# 'Force quits' the game, just in case it gets stuck (ADD CONFIRMATION PROMPT) - not a pretty game end!!! (MAKE IT WORK WELL)
@bot.command(pass_context = True, name = 'end_game', help = 'Ends the game')
async def end_game(ctx):
	if bot.game_in_session:
		bot.game_in_session = False
		for member in bot.players:
			member.remove_roles(bot.sh_role, bot.president_role, bot.chancellor_role)
			await bot.channel.send("{} has left the game".format(member.mention))
		await bot.channel.send("Game ended.")
			
		await bot.channel.send("{} was Hitler".format(bot.current_chancellor.mention))
		for player in bot.fascists:
			await bot.channel.send("{} was a Fascist".format(player.mention))
		for player in bot.liberals:
			await bot.channel.send("{} was a Liberal".format(player.mention))
	else:
		await bot.channel.send("Can't end game: one isn\'t running!")

# Allows the President to select a new Chancellor
@bot.command(pass_context = True, name = 'nominate', help = 'Allows the President to appoint a Chancellor (@nickname)')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def nominate(ctx, nominee):
	debug_list(ctx)
	if ctx.guild:
		if bot.game_in_session or bot.debug_enable:
			if not bot.pres_power:
				# Checks if there is already a Chancellor
				for member in bot.players:
					if bot.chancellor_role in member.roles:
						bot.chancellor_nominee = None # MAKE THIS WORK - should be "member", but it always throws the same error
			
				if True: #bot.chancellor_nominee == None or bot.debug_enable: # FIX THIS LATER !!!!!!!!!!
					for member in bot.players:
						if member.mention == nominee:
							if ctx.message.author != member or bot.debug_enable:
								if member != bot.previous_chancellor:
									if member != bot.previous_president:
										bot.chancellor_nominee = member
										bot.voting_open = True
										await bot.channel.send(":white_check_mark: {} has been nominated by {} as Chancellor! \n Voting has opened. Please react with either {} or {} to place your vote. \n The game will continue once all players have voted.".format(member.mention, ctx.message.author.mention, bot.ja_emoji, bot.nein_emoji))
									else:
										await bot.channel.send("You can\'t nominate them: they were President last round!")
								else:
									await bot.channel.send("You can\'t nominate them: they were Chancellor last round!")
							else:
								await bot.channel.send("You can't nominate yourself!")
						elif nominee == None:
							await bot.channel.send("Can\'t do that: player isn\'t in this game!")
				else:
					await bot.channel.send("Can\'t do that: a player has already been nominated as Chancellor")
			else:
				await bot.channel.send("The president hasn\'t used their power yet!")
		else:
			await bot.channel.send("Can\'t do that: game not in session!")
	else:
		await bot.channel.send("You can\'t use that here!")
		
		
# Allows the President to enact their presidential powers, given that certain criteria are met		
@bot.command(pass_context = True, name = 'draw', help = 'Allows the President to draw 3 new policies')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def draw(ctx):
	if ctx.guild:
		if bot.game_in_session or bot.debug_enable:
			# Check if there is an elected Chancellor in the game
			if bot.current_chancellor != None:
				chancellor_check = True
			else:
				chancellor_check = False
					
			if chancellor_check or bot.debug_enable:
				member = ctx.message.author
				
				if len(bot.policies) < 3:
					shuffle_deck()
				
				await member.create_dm()
				await member.dm_channel.send('You drew: ')
				
				for i in range(0,3):
					await member.dm_channel.send(bot.policies[i])
					bot.top_three.append(bot.policies[i])
					bot.policies.pop(i)
					
				await member.dm_channel.send('Choose one of these 3 cards to discard, and the two remaining cards will be passed on to the Chancellor.')
				await member.dm_channel.send('Type \'!discard\', followed by a space and either \"liberal\" or \"fascist\" to make your decision of which to discard.')
				
			else:
				await bot.channel.send("There isn't a Chancellor yet!")
			
		else:
			await bot.channel.send("Can\'t do that: game not in session!")
	else:
		await bot.channel.send("You can\'t use that here!")

# Allows the President to forward two of the policies to the Chancellor
@bot.command(pass_context = True, name = 'discard', help = 'Allows the President to pass 2 policies to the Chancellor')
async def discard(ctx, discard):
	if not ctx.guild:
		member = ctx.message.author
		chancellor = bot.current_chancellor
		if discard in bot.top_three:
			bot.top_three.remove(discard)
			bot.discarded.append(discard)
			await chancellor.dm_channel.send('The President has passed you these policy cards:')
			await member.dm_channel.send('You have sent the Chancellor these policy cards:')
			for card in range(0,2):
				await chancellor.dm_channel.send(bot.top_three[card])
				await member.dm_channel.send(bot.top_three[card])
			await chancellor.dm_channel.send('When you are ready, use the \'!play\' command here, followed by a space and the card you would like to play, to place your selection on the board.') # FIX TO WORK IN THE DM CHANNEL!!!!!
			
		else:
			await member.dm_channel.send('You didn\'t draw one of those! Try again.')
	else:
		await ctx.send("You can\'t use that here!")
			
# Allows the Chancellor to play a policy card
@bot.command(pass_context = True, name = 'play', help = 'Allows the Chancellor to play 1 policy, "liberal" or "fascist"') # Add check to only allow this once
async def play(ctx, policy_type):
	if not ctx.guild:
		member = ctx.message.author
		chancellor = bot.current_chancellor
		if member == chancellor:
			if bot.game_in_session or bot.debug_enable:
				if policy_type in bot.top_three:
					bot.top_three.remove(policy_type)
					bot.discarded.append(bot.top_three)
					bot.top_three = []
					fascist_before = bot.fascist_policies_played
					await ctx.send("You have successfully played a {} card! Please return to the main channel".format(policy_type))
					await bot.channel.send("{} played a {} card!".format(ctx.message.author.mention, policy_type))
					if policy_type == "liberal":
						bot.liberal_policies_played += 1
					elif policy_type == "fascist":
						bot.fascist_policies_played += 1
					else:
						return
						
					lib_address, fasc_address = display_board()
					await bot.channel.send(file = discord.File(lib_address))
					await bot.channel.send(file = discord.File(fasc_address))
					await bot.channel.send("Policies in Deck: " + str(len(bot.policies)))
					await bot.channel.send("Discarded Policies: " + str(len(bot.discarded)))
				
					if bot.liberal_policies_played >= 5:
						await bot.channel.send("The liberals have successfully passed their fifth policy! They win!")
						await end_game(None)
						return
				
					if bot.fascist_policies_played >= 6:
						await bot.channel.send("The fascists have successfully passed their sixth policy! They win!")
						await end_game(None)
						return
				
					if bot.fascist_policies_played > fascist_before:
						if bot.fascist_policies_played == 1:
							if len(bot.players) > 8:
								bot.pres_power = True
								bot.take_pres_action = bot.current_president
								await bot.channel.send("President of this round, {}, you must INSPECT A PLAYER\'S LOYALTY before the game may continue.".format(bot.take_pres_action.mention))
								await bot.channel.send("Use the \"!power\" command to do this.")

						elif bot.fascist_policies_played == 2:
							if len(bot.players) > 6:
								bot.pres_power = True
								bot.take_pres_action = bot.current_president
								await bot.channel.send("President of this round, {}, you must INSPECT A PLAYER\'S LOYALTY before the game may continue.".format(bot.take_pres_action.mention))
								await bot.channel.send("Use the \"!power\" command to do this.")

						elif bot.fascist_policies_played == 3:
							if len(bot.players) > 6:
								bot.pres_power = True
								bot.take_pres_action = bot.current_president
								await bot.channel.send("President of this round, {}, you must CHOOSE THE NEXT PRESIDENT before the game may continue.".format(bot.take_pres_action.mention))
								await bot.channel.send("Use the \"!power\" command to do this.")
							else:
								bot.pres_power = True
								bot.take_pres_action = bot.current_president
								await bot.channel.send("President of this round, {}, you must VIEW THE TOP THREE CARDS of the deck before the game may continue.".format(bot.take_pres_action.mention))
								await bot.channel.send("Use the \"!power\" command to do this.")
						
						elif bot.fascist_policies_played == 4 or bot.fascist_policies_played == 5:
							bot.pres_power = True
							bot.take_pres_action = bot.current_president
							await bot.channel.send("President of this round, {}, you must KILL A PLAYER before the game may continue.".format(bot.take_pres_action.mention))
							await bot.channel.send("Use the \"!power\" command to do this.")

					if not bot.pres_power:
						await new_government()
				
				else:
					await ctx.send("You didn\'t get passed one of those! Try again.")
			else:
				await ctx.send("Can\'t do that: game not in session!")
		else:
			await ctx.send("You aren't the Chancellor!")
	else:
		await ctx.send("Use this in the private channel!")

# Displays the current game boards
def display_board():
	liberal_board = ['/home/pi/Secret-Hitler-Bot/Images/Liberal0.png', '/home/pi/Secret-Hitler-Bot/Images/Liberal1.png', '/home/pi/Secret-Hitler-Bot/Images/Liberal2.png', '/home/pi/Secret-Hitler-Bot/Images/Liberal3.png', '/home/pi/Secret-Hitler-Bot/Images/Liberal4.png', '/home/pi/Secret-Hitler-Bot/Images/Liberal5.png']
	fascist_board_56 = ['/home/pi/Secret-Hitler-Bot/Images/Fascist(5,6)0.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist(5,6)1.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist(5,6)2.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist3.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist4.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist5.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist6.png']
	fascist_board_78 = ['/home/pi/Secret-Hitler-Bot/Images/Fascist(7,8)0.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist(7,8,9,10)1.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist(7,8,9,10)2.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist3.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist4.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist5.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist6.png']
	fascist_board_910 = ['/home/pi/Secret-Hitler-Bot/Images/Fascist(9,10)0.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist(7,8,9,10)1.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist(7,8,9,10)2.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist3.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist4.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist5.png', '/home/pi/Secret-Hitler-Bot/Images/Fascist6.png']
	if len(bot.players) < 7:
		liberal_address = liberal_board[bot.liberal_policies_played]
		
		fascist_address = fascist_board_56[bot.fascist_policies_played]
		
	elif len(bot.players) < 9:
		liberal_address = liberal_board[bot.liberal_policies_played]
		
		fascist_address = fascist_board_78[bot.fascist_policies_played]
		
	else:
		liberal_address = liberal_board[bot.liberal_policies_played]
		
		fascist_address = fascist_board_910[bot.fascist_policies_played]

	return liberal_address, fascist_address

# Removes old government and selects a new President (next in the list of players) - NEEDS TO BE OWN FUNCTION, SO THAT THIS "PRESIDENTIAL RESET" CAN BE CALLED ON THE THREE DIFFERENT OCCASIONS IT'S NEEDED!!!!!
async def new_government():
	current_index = bot.players.index(bot.current_president)
	if current_index == (len(bot.players) - 1):
		new_index = 0
	else:
		new_index = current_index + 1
				
	if not bot.has_election_increased: 
		await bot.channel.send("{} and {} have left office.".format(bot.current_president.mention, bot.current_chancellor.mention))
				
	bot.previous_president = bot.current_president
	bot.previous_chancellor = bot.current_chancellor
	await bot.current_president.remove_roles(bot.president_role)
	await bot.current_chancellor.remove_roles(bot.chancellor_role)
	bot.current_president = None
	bot.current_chancellor = None
				
	bot.current_president = bot.players[new_index]
	await bot.current_president.add_roles(bot.president_role)
						
	# These are here just in case, since the single instance of them up in the 'on_message' event doesn't seem to always reset them
	bot.voted_yes = 0
	bot.voted_no = 0
	
	# Check for election tracker status and vary messages accordingly
	
	await bot.channel.send("{} is the new President!".format(bot.current_president.mention))
	await bot.channel.send("When you are ready, {}, please nominate a Chancellor with the \"!nominate @nickname\" command!".format(bot.current_president.mention))
					
	bot.current_chancellor = None
					
	print(bot.players)
	
# Presidential powers --------------------------------------------------

@bot.command(pass_context = True, name = 'power', help = 'Allows the president to enact presidential powers')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def power(ctx, target = None):
	member = ctx.message.author
	for player in bot.players:
		if player.mention == target:
			target = player
	
	if ctx.guild:
		if bot.pres_power == True or bot.debug_enable:
			if bot.fascist_policies_played == 1:
				if len(bot.players) > 8:
					# Investigate identity
					if target in bot.fascists or target == bot.hitler:
						member.dm_channel.send("{} is a fascist".format(target))
					else:
						member.dm_channel.send("{} is a liberal".format(target))
					bot.pres_power = False
					
			elif bot.fascist_policies_played == 2:
				if len(bot.players) > 6:
					# Investigate identity
					if target in bot.fascists or target == bot.hitler:
						member.dm_channel.send("{} is a fascist".format(target))
					else:
						member.dm_channel.send("{} is a liberal".format(target))
					bot.pres_power = False
					
			elif bot.fascist_policies_played == 3:
				if len(bot.players) < 7:
					# Send the president the top three cards
					await member.dm_channel.send("The top three cards are:")
					for i in range(0,3):
						await member.dm_channel.send(bot.policies[i])
					
					bot.top_three = []
					bot.pres_power = False
				
				elif len(bot.players) > 6:
					# Select next president
					pres_override = True
					await bot.channel.send("New president selected")
					bot.pres_power = False
			
			elif bot.fascist_policies_played == 4 or bot.fascist_policies_played == 5:
				# Kill a player
				target.remove_roles(bot.sh_role, bot.presidental_role, bot.chancellor_role)
				bot.players.remove(target)
				await bot.channel.send("{} has been killed!".format(target.mention))
				if target == bot.hitler:
					await bot.channel.send("Hitler has been killed!!! The liberals win!")
					await end_game(None)
					return
				bot.pres_power = False
	
			# Removes old government and selects a new President (next in the list of players)
			current_index = bot.players.index(bot.current_president)
			if current_index == (len(bot.players) - 1):
				new_index = 0
			else:
				new_index = current_index + 1

			await bot.channel.send("{} and {} have left office.".format(bot.current_president.mention, bot.current_chancellor.mention))

			await bot.current_president.remove_roles(bot.president_role)
			await bot.current_chancellor.remove_roles(bot.chancellor_role)
			bot.current_president = None
			bot.current_chancellor = None
			
			# Applies presidential selection if the power was granted
			if pres_override:
				bot.current_president = target
			else:
				bot.current_president = bot.players[new_index]
			
			await bot.current_president.add_roles(president_role)
			await bot.channel.send("{} is the new President!".format(bot.current_president.mention))
			await bot.channel.send("When you are ready, {}, please nominate a Chancellor with the \"!nominate @nickname\" command!".format(bot.current_president.mention))
			
	print(bot.players)
	
# Runs the game ----------------------------------------------------------------------------------------------------

def shuffle_deck():
	bot.liberal_policies = 6 - bot.liberal_policies_played
	bot.fascist_policies = 11 - bot.fascist_policies_played
	bot.discarded = []
	for card in range(0, (bot.liberal_policies + bot.fascist_policies)):
		random_bin = randint(0,2)
		if random_bin == 0:
			if bot.liberal_policies > 0:
				bot.liberal_policies -= 1
				bot.policies.append("liberal")
			else:
				if bot.fascist_policies > 0:
					bot.fascist_policies -= 1
					bot.policies.append("fascist")
		elif random_bin >= 1:
			if bot.fascist_policies > 0:
				bot.fascist_policies -= 1
				bot.policies.append("fascist")
			else:
				if bot.liberal_policies > 0:
					bot.liberal_policies -= 1
					bot.policies.append("liberal")
	
	print("Policy Deck: ")
	print(bot.policies)

@bot.command(pass_context = True, name = 'lobby', help = 'Allows players to join game / starts game sequence')
async def lobby(ctx):
	if ctx.guild:
		if not bot.game_in_session:
			bot.players = []
			bot.game_in_session = False
			bot.joinable = True
			bot.liberal_policies = 6
			bot.liberal_policies_played = 0
			bot.fascist_policies = 11
			bot.fascist_policies_played = 0
			bot.policies = []
			bot.chancellor_nominee = None
			bot.voting_open = False
			bot.voted_yes = 0
			bot.voted_no = 0
			bot.votes = []
			bot.has_voted = []
			bot.top_three = []
			bot.discarded = []
			bot.current_president = None
			bot.current_chancellor = None
			bot.previous_president = None
			bot.previous_chancellor = None
			bot.hitler = None
			bot.fascists = []
			bot.liberals = []
			bot.pres_power = False
			bot.take_pres_action = None
			bot.election_tracker = 0
			bot.has_election_increased = False
	
			await bot.channel.send("Lobby open! Join the lobby with " + bot.join_emoji + ". \n Leave the lobby with " + bot.leave_emoji + ". \n Check which players are in the lobby with " + bot.players_emoji + ". \n When all players have joined the lobby, start the game with " + bot.start_emoji + "!")
		
		else:
			await bot.channel.send("You can\'t open the lobby while a game is running!")
	else:
		await bot.channel.send("You can\'t use that here!")

# Starts the game (ADD CONFIRMATION PROMPT)	- Doesn't state the deck/discard sizes on this first display. Minor inconvenience, fix later
async def start_game():
	if bot.game_in_session:
		await bot.channel.send("Can\'t start game: one\'s already running!")
		return
	else:
		bot.game_in_session = True
		bot.joinable = False
			
		# Rebuild player list now that changes have been finalized
		bot.players = []
		
		# Create temporory list for assigning roles
		unassigned_players = []
		
		for member in bot.guild.members:
			if bot.sh_role in member.roles: 
				bot.players.append(member)
				unassigned_players.append(member)
		
		print(unassigned_players) # DEBUG
		
		# Check for correct player count
		if not bot.debug_enable:
			if len(unassigned_players) < 5 or len(unassigned_players) > 10:
				await bot.channel.send("Game start failed: there aren\'t between 5 and 10 players!")
				unassigned_players = []
				bot.fascists = []
				bot.liberals = []
				await end_game(None)
				return
			
		await bot.channel.send("Game starting! (Lobby has closed)")
			
		# Generates the deck
		shuffle_deck()
			
		# Displays the game board
		lib_address, fasc_address = display_board()
		await bot.channel.send(file = discord.File(lib_address))
		await bot.channel.send(file = discord.File(fasc_address))
		
		# Decides what distribution of Fascists, Liberals, and Hitler to use based on the player count, and assigns them to people randomly
		# For 9 or 10 players, assign three Fascists + Hitler
		if len(unassigned_players) == 9 or len(unassigned_players) == 10:
			selection = randint(0, len(unassigned_players) - 1)
			member = unassigned_players[selection]
			bot.hitler = member
			await member.create_dm()
			await member.dm_channel.send(f'You are Hitler!')
			await member.dm_channel.send(file = discord.File("/home/pi/Secret-Hitler-Bot/Images/hitler.png"))
			print("{} is Hitler".format(member.mention))
			bot.fascists.append(member)
			unassigned_players.remove(member)
	
			for i in range (0, 3):
				selection = randint(0, len(unassigned_players) - 1)
				member = unassigned_players[selection]
				await member.create_dm()
				await member.dm_channel.send(f'You are a fascist!')
				await member.dm_channel.send(file = discord.File("/home/pi/Secret-Hitler-Bot/Images/fascist.png"))
				await member.dm_channel.send("{} is Hitler".format(bot.hitler.mention))
				bot.fascists.append(member)
				print("{} is a Fascist".format(member.mention))
				unassigned_players.remove(member)
		
		# For 7 or 8 players, assign two Fascists + Hitler
		elif len(unassigned_players) == 7 or len(unassigned_players) == 8:
			selection = randint(0, len(unassigned_players) - 1)
			member = unassigned_players[selection]
			bot.hitler = member
			await member.create_dm()
			await member.dm_channel.send(f'You are Hitler!')
			await member.dm_channel.send(file = discord.File("/home/pi/Secret-Hitler-Bot/Images/hitler.png"))
			print("{} is Hitler".format(member.mention))
			bot.fascists.append(member)
			unassigned_players.remove(member)
	
			for i in range (0, 2):
				selection = randint(0, len(unassigned_players) - 1)
				member = unassigned_players[selection]
				await member.create_dm()
				await member.dm_channel.send(f'You are a fascist!')
				await member.dm_channel.send(file = discord.File("/home/pi/Secret-Hitler-Bot/Images/fascist.png"))
				await member.dm_channel.send("{} is Hitler".format(bot.hitler.mention))
				bot.fascists.append(member)
				print("{} is a Fascist".format(member.mention))
				unassigned_players.remove(member)
	
		# For 5 or 6 players, assign one Fascist + Hitler
		else:
			selection = randint(0, len(unassigned_players) - 1)
			member = unassigned_players[selection]
			bot.hitler = member
			await member.create_dm()
			await member.dm_channel.send(f'You are Hitler!')
			await member.dm_channel.send(file = discord.File("/home/pi/Secret-Hitler-Bot/Images/hitler.png"))
			print("{} is Hitler".format(member.mention))
			bot.fascists.append(member)
			unassigned_players.remove(member)
		
			selection = randint(0, len(unassigned_players) - 1)
			member = unassigned_players[selection]
			await member.create_dm()
			await member.dm_channel.send(f'You are a fascist!')
			await member.dm_channel.send(file = discord.File("/home/pi/Secret-Hitler-Bot/Images/fascist.png"))
			await member.dm_channel.send("{} is Hitler".format(bot.hitler.mention))
			bot.fascists.append(member)
			print("{} is a Fascist".format(member.mention))
			unassigned_players.remove(member)
			
			await bot.hitler.dm_channel.send("Your Fascist ally is {}.".format(bot.fascists[1]))
			
		# For everyone that isn't a Fascist or Hitler, make them a Liberal
		for member in unassigned_players:
			await member.create_dm()
			await member.dm_channel.send(f'You are a liberal!')
			await member.dm_channel.send(file = discord.File("/home/pi/Secret-Hitler-Bot/Images/liberal.png"))
			bot.liberals.append(member)
			print("{} is a Liberal".format(member.mention))
		
		# Reset this counter, just in case. Probably unnecessary
		unassigned_players = []
		
		if len(bot.fascists) > 2:
			for member in bot.fascists:
				if member != bot.hitler:
					temp_fascists = bot.fascists
					temp_fascists.remove(member)
					temp_fascists.remove(bot.hitler)
					await member.dm_channel.send("Your fellow fascists are: ")
					for player in temp_fascists:
						await member.dm_channel.send("{}".format(player))

		# Randomly select a President from the pool of players (MIGHT BE BETTER AS OWN FUNCTION?) BROKEN RIGHT NOWWWWWW?????
		member = bot.players[randint(0, (len(bot.players) - 1))]
		await member.add_roles(bot.president_role)
		bot.current_president = member
		await bot.channel.send("Our first president is... {}!".format(member.mention))
		await bot.channel.send("When you are ready, {}, please nominate a Chancellor with the \"!nominate @nickname\" command!".format(member.mention))
			
	# ADD VETO POWERS!!!!!
	# ADD ARGUMENT EXPLANATION FOR PRESIDENTIAL POWER COMMAND

# Just for fun --------------------------------------------------

@bot.command(name = 'roll_dice', help = 'Simultes rolling dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
	dice = [
		str(randint(1, number_of_sides + 1))
		for _ in range(number_of_dice)
	]
	await bot.channel.send(','.join(dice))	

bot.run(TOKEN)