# bot.py
import os
from random import *

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

bot.guild = discord.utils.get(bot.guilds, name="games")

bot.players = []
bot.game_in_session = False
bot.joinable = False
bot.liberal_policies = 6
bot.liberal_policies_played = 0
bot.fascist_policies = 11
bot.fascist_policies_played = 0
bot.policies = []
bot.drawn_policies = []
bot.discarded_policies = []
bot.chancellor_nominee = None
bot.voting_open = False
bot.voted_yes = 0
bot.voted_no = 0
bot.has_voted = []
bot.top_three = []
bot.current_president = None
bot.current_chancellor = None
bot.hitler = None
bot.fascists = []
bot.liberals = []
bot.presidential_power = False
bot.take_pres_action = None

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

bot.event
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
		await ctx.send(_message)
		return
	elif isinstance(error, commands.CheckFailure):
		await ctx.send("You do not have permission to use this command.")
		return
	elif isinstance(error, commands.UserInputError):
		await ctx.send("Invalid input.")
		return
	elif isinstance(error, commands.DisabledCommand):
		await ctx.send('This command has been disabled.')
		return
	else:
		await ctx.send("The command encountered an unexpected error.")
		return

def debug_list(ctx):
	bot.players = []
	role = discord.utils.get(ctx.message.guild.roles, name="Secret Hitler")
	for member in ctx.message.guild.members:
		if role in member.roles: 
			bot.players.append(member)

# Commands for gameplay ----------------------------------------------------------------------------------------------------

@bot.event
async def on_message(message):
	channel = message.channel
	they_have_voted = False
	if bot.game_in_session:
		if message.content.startswith('ja') or message.content.startswith('nein'):
			for member in bot.has_voted:
				if message.author in bot.has_voted:
					they_have_voted = True
				else:
					they_have_voted = False
			
			if they_have_voted == False:
				if message.content.startswith('ja'):
					if bot.voting_open:
						bot.voted_yes += 1
						bot.has_voted.append(message.author)
						await channel.send("Yes recorded, {}!".format(message.author.mention))
						await channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\ja.png"))
					else:
						await channel.send("Voting isn\'t open yet!")
						return
				
				elif message.content.startswith('nein'):
					if bot.voting_open:
						bot.voted_no += 1
						bot.has_voted.append(message.author)
						await channel.send("No recorded, {}!".format(message.author.mention))
						await channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\nein.png"))
					else:
						await channel.send("Voting isn\'t open yet!")
						return
				else:
					return
			
				if bot.voted_yes + bot.voted_no >= len(bot.players):
					bot.voting_open = False
				
					await channel.send("Everyone has cast their vote! Voting is now closed.")
					await channel.send("There were {} \'ja\' votes, and {} \'nein\' votes.".format(bot.voted_yes, bot.voted_no))

					if bot.voted_yes > bot.voted_no:
						role = discord.utils.get(message.guild.roles, name="Chancellor")
						await bot.chancellor_nominee.add_roles(role)
						bot.current_chancellor = bot.chancellor_nominee
						
						if bot.chancellor_nominee == bot.hitler:
							if bot.fascist_policies_played >= 3:
								end_game()
								await channel.send("Hitler has been elected Chancellor after 3 fascist policies had been passed! The fascists have won!!!")
								await channel.send("Hitler was {}".format(bot.chancellor_nominee.mention))
								return

						await channel.send("The motion passed! {} is now the Chancellor!".format(bot.chancellor_nominee.mention))
						await channel.send("When you are ready, {}, please use the \"!draw_policies\" command to take the top three policies from the deck.".format(bot.current_president.mention))
						await channel.send("They will be sent to you in a private message. Look out for the one from \"Games Bot\"!")
					
					else:
						bot.chancellor_nominee = ""
						await channel.send("The motion failed! No Chancellor has been elected.")
					
					bot.voted_yes = 0
					bot.voted_no = 0
			else:
				await channel.send("You have already voted, {}!".format(message.author.mention))

	await bot.process_commands(message)

#Allows a player to join a game that isn't underway	
@bot.command(pass_context = True, name = 'join_game', help = 'Join the game')
async def join_game(ctx):
	if ctx.guild:
		if not bot.game_in_session:
			if bot.joinable:
				role = discord.utils.get(ctx.guild.roles, name="Secret Hitler")
				if role in ctx.author.roles:
					await ctx.send(f'You\'re already part of the game!')
				else:
					await ctx.author.add_roles(role)
					await ctx.send(":white_check_mark: {} is now in the game!".format(ctx.message.author.mention))
					bot.players.append(ctx.author)
			else:
				await ctx.send("A game has yet to begin / is already in progress!")
	else:
		await ctx.send("You can\'t use that here!")

# Allows a player to leave a game that isn't underway
@bot.command(pass_context = True, name = 'leave_game', help = 'Leave the game')		
async def leave_game(ctx):
	if ctx.guild:
		if not bot.game_in_session:
			game_role = discord.utils.get(ctx.guild.roles, name="Secret Hitler")
			chancellor_role = discord.utils.get(ctx.guild.roles, name="Chancellor")
			president_role = discord.utils.get(ctx.guild.roles, name="President")
			if game_role in ctx.author.roles:
				await ctx.author.remove_roles(game_role)
				await ctx.author.remove_roles(chancellor_role)
				await ctx.author.remove_roles(president_role)
				await ctx.send(":white_check_mark: {} has now left the game!".format(ctx.message.author.mention))
				bot.players.remove(ctx.author)
			else:
				await ctx.send(f'You aren\'t part of the game yet!')
		else:
			await ctx.send("A game is currently underway!")
	else:
		await ctx.send("You can\'t use that here!")

# 'Force quits' the game, just in case it gets stuck (ADD CONFIRMATION PROMPT)
@bot.command(pass_context = True, name = 'end_game', help = 'Ends the game')
async def end_game(ctx):
	if ctx.guild:
		if bot.game_in_session:
			bot.game_in_session = False
			for member in bot.players:
				sh_role = discord.utils.get(ctx.guild.roles, name="Secret Hitler")
				president_role = discord.utils.get(ctx.guild.roles, name="President")
				chancellor_role = discord.utils.get(ctx.guild.roles, name="Chancellor")
				#if sh_role in member.roles:
				await member.remove_roles(sh_role)
				#if president_role in member.roles:	
				await member.remove_roles(president_role)
				#if chancellor_role in member.roles:	
				await member.remove_roles(chancellor_role)
				await ctx.send("{} has left the game".format(member.mention))
			await ctx.send("Game ended.")
		else:
			await ctx.send("Can't end game: one isn\'t running!")
	else:
		await ctx.send("You can\'t use that here!")

@bot.command(pass_context = True, name = 'player_count', help = 'Reports players in game / lobby')
async def player_count(ctx):
	if ctx.guild:
		if len(bot.players) == 0:
			await ctx.send("There aren\'t any players!")
		else:
			await ctx.send("Players: " + str(len(bot.players)))
			for player in bot.players:
				await ctx.send(player.mention)
	else:
		await ctx.send("You can\'t use that here!")
			
# Allows the President to select a new Chancellor
@bot.command(pass_context = True, name = 'nominate', help = 'Allows the President to appoint a Chancellor (@nickname)')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def nominate(ctx, nominee):
	debug_list(ctx)
	if ctx.guild:
		if bot.game_in_session:
			# Checks if there is already a Chancellor
			role = discord.utils.get(ctx.guild.roles, name="Chancellor")
			for member in bot.players:
				if role in member.roles:
					bot.chancellor_nominee = member
			
			if bot.chancellor_nominee == None:
				for member in bot.players:
					if member.mention == nominee:
						if ctx.message.author != member:
							bot.chancellor_nominee = member
							bot.voting_open = True
							await ctx.send(":white_check_mark: {} has been nominated by {} as Chancellor!".format(member.mention, ctx.message.author.mention))
							await ctx.send("Voting has opened. Please type either \"ja\" or \"nein\" into this chat to place your vote")
							await ctx.send("The game will continue once all players have voted.")
						else:
							await ctx.send("You can't nominate yourself!")
					elif nominee == None:
						await ctx.send("Can\'t do that: player isn\'t in this game!")
			else:
				await ctx.send("Can\'t do that: a player has already been nominated as Chancellor")
		else:
			await ctx.send("Can\'t do that: game not in session!")
	else:
		await ctx.send("You can\'t use that here!")
		
		
# Allows the President to draw 3 policy cards, and DM's them the result		
@bot.command(pass_context = True, name = 'draw_policies', help = 'Allows the President to draw 3 new policies')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def draw_policies(ctx):
	if ctx.guild:
		if bot.game_in_session:
			# Check if there is an elected Chancellor in the game
			if bot.current_chancellor != None:
				chancellor_check = True
			else:
				chancellor_check = False
					
			if chancellor_check:
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
				await member.dm_channel.send('Type \'!discard_policy\', followed by a space and either \"liberal\" or \"fascist\" to make your decision of which to discard.')
				
			else:
				await ctx.send("There isn't a Chancellor yet!")
			
		else:
			await ctx.send("Can\'t do that: game not in session!")
	else:
		await ctx.send("You can\'t use that here!")

# Allows the President to forward two of the policies to the Chancellor
@bot.command(pass_context = True, name = 'discard_policy', help = 'Allows the President to pass 2 policies to the Chancellor')
async def discard_policy(ctx, discard):
	if not ctx.guild:
		member = ctx.message.author
		chancellor = bot.current_chancellor
		if discard in bot.top_three:
			bot.top_three.remove(discard)
			await chancellor.dm_channel.send('The President, {}, has passed you these policy cards:'.format(member.mention))
			await member.dm_channel.send('You have sent the Chancellor, {}, these policy cards:'.format(chancellor.mention))
			for card in range(0,2):
				await chancellor.dm_channel.send(bot.top_three[card])
				await member.dm_channel.send(bot.top_three[card])
			await chancellor.dm_channel.send('When you are ready, use the \'!play_policy\' action back in the main channel, followed by a space and the card you would like to play, to place your selection on the board.') # FIX TO WORK IN THE DM CHANNEL!!!!!
			
		else:
			await member.dm_channel.send('You didn\'t draw one of those! Try again.')
	else:
		await ctx.send("You can\'t use that here!")
			
# Allows the Chancellor to play a policy card
@bot.command(pass_context = True, name = 'play_policy', help = 'Allows the Chancellor to play 1 policy, "liberal" or "fascist"')
@commands.has_role('Secret Hitler')
@commands.has_role('Chancellor')
async def play_policy(ctx, policy_type):
	if ctx.guild:
		if bot.game_in_session:
			if policy_type in bot.top_three:
				fascist_before = bot.fascist_policies_played
				await ctx.send("{} played a {} card!".format(ctx.message.author.mention, policy_type))
				if policy_type == "liberal":
					bot.liberal_policies_played += 1
				elif policy_type == "fascist":
					bot.fascist_policies_played += 1
				else:
					return
				lib_address, fasc_address = display_board()
				await ctx.send(file = discord.File(lib_address))
				await ctx.send(file = discord.File(fasc_address))
				await ctx.send("Policies in Deck: " + str(len(bot.policies)))
				await ctx.send("Discarded Policies: " + str(17 - (len(bot.policies) + bot.liberal_policies_played + bot.fascist_policies_played)))
				
				if bot.liberal_policies_played >= 5:
					end_game()
					await ctx.send("The liberals have successfully passed their fifth policy! They win!")
					await ctx.send("Hitler was {}".format(bot.hitler))
				
				if bot.fascist_policies_played >= 6:
					end_game()
					await ctx.send("The fascists have successfully passed their sixth policy! They win!")
					await ctx.send("Hitler was {}".format(bot.hitler))
				
				if bot.fascist_policies_played = 3:
					if fascist_policies_played > fascist_before:
						bot.presidential_power = True
						bot.take_pres_action = bot.current_president
						await ctx.send("President of this round, {}, you must view the tpo three cards of the deck before the game may continue.".format(bot.take_pres_action))
						await ctx.send("Use the \"!view_top_cards\" command to do this. You will receive a private message with the cards.")
				
				# Removes old government and selects a new President (next in the list of players)
				current_index = bot.players.index(bot.current_president)
				if current_index == (len(bot.players) - 1):
					new_index = 0
				else:
					new_index = current_index + 1
				
				await ctx.send("{} and {} have left office.".format(bot.current_president.mention, bot.current_chancellor.mention))
				
				president_role = discord.utils.get(ctx.guild.roles, name="President")
				chancellor_role = discord.utils.get(ctx.guild.roles, name="Chancellor")
				await bot.current_president.remove_roles(president_role)
				await bot.current_chancellor.remove_roles(chancellor_role)
				bot.current_president = None
				bot.current_chancellor = None
				
				bot.current_president = bot.players[new_index]
				await bot.current_president.add_roles(president_role)
				
				await ctx.send("{} is the new President!".format(bot.current_president.mention))
				await ctx.send("When you are ready, {}, please nominate a Chancellor with the \"!nominate @nickname\" command!".format(bot.current_president.mention))
				
				print(bot.players)
				
			else:
				await ctx.send("You didn\'t get passed one of those! Try again.")
		else:
			await ctx.send("Can\'t do that: game not in session!")
	else:
		await ctx.send("Use this in the main game channel!")

# Displays the current game boards
def display_board():
	liberal_board = ['Liberal0.png', 'Liberal1.png', 'Liberal2.png', 'Liberal3.png', 'Liberal4.png', 'Liberal5.png']
	fascist_board_56 = ['Fascist(5,6)0.png', 'Fascist(5,6)1.png', 'Fascist(5,6)2.png', 'Fascist3.png', 'Fascist4.png', 'Fascist5.png', 'Fascist6.png']
	fascist_board_78 = ['Fascist(7,8)0.png', 'Fascist(7,8,9,10)1.png', 'Fascist(7,8,9,10)2.png', 'Fascist3.png', 'Fascist4.png', 'Fascist5.png', 'Fascist6.png']
	fascist_board_910 = ['Fascist(9,10)0.png', 'Fascist(7,8,9,10)1.png', 'Fascist(7,8,9,10)2.png', 'Fascist3.png', 'Fascist4.png', 'Fascist5.png', 'Fascist6.png']
	if len(bot.players) < 7:
		liberal_address = liberal_board[bot.liberal_policies_played]
		liberal_address = os.path.join(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images", liberal_address)
		
		fascist_address = fascist_board_56[bot.fascist_policies_played]
		fascist_address = os.path.join(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images", fascist_address)
		
	elif len(bot.players) < 9:
		liberal_address = liberal_board[bot.liberal_policies_played]
		liberal_address = os.path.join(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images", liberal_address)
		
		fascist_address = fascist_board_78[bot.fascist_policies_played]
		fascist_address = os.path.join(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images", fascist_address)
		
	else:
		liberal_address = liberal_board[bot.liberal_policies_played]
		liberal_address = os.path.join(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images", liberal_address)
		
		fascist_address = fascist_board_910[bot.fascist_policies_played]
		fascist_address = os.path.join(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images", fascist_address)

	return liberal_address, fascist_address
	
# Presidential powers --------------------------------------------------

@bot.command(pass_context = True, name = 'view_top_cards', help = 'Allows the president to inspect the top three cards of the deck')

@bot.command(pass_context = True, name = 'inspect_player', help = 'Allows the president to inspect a player\'s allegiance')
async def inspect_player():
	return
	
# Runs the game ----------------------------------------------------------------------------------------------------

def shuffle_deck():
	bot.liberal_policies = 6 - bot.liberal_policies_played
	bot.fascist_policies = 11 - bot.fascist_policies_played
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

@bot.command(pass_context = True, name = 'open_lobby', help = 'Allows players to join game / starts game sequence')
async def open_lobby(ctx):
	if ctx.guild:
		bot.players = []
		bot.game_in_session = False
		bot.joinable = True
		bot.liberal_policies = 6
		bot.fascist_policies = 11
		bot.liberal_policies_played = 0
		bot.fascist_policies_played = 0
		bot.policies = []
		bot.drawn_policies = []
		bot.discarded_policies = []
		bot.chancellor_nominee = None
		bot.voting_open = False
		bot.voted_yes = 0
		bot.voted_no = 0
		bot.has_voted = []
		bot.top_three = []
		bot.current_president = None
		bot.current_chancellor = None
		bot.Hitler = None
		bot.fascists = []
		bot.liberals = []
		bot.presidential_power = False
		bot.take_pres_action = None
	
		await ctx.send("Lobby open!")
		await ctx.send("Join the lobby with the \"!join_game\" command!")
		await ctx.send("Leave the lobby with the \"!leave_game\" command!")
		await ctx.send("Check which players are in the lobby with the \"!player_count\" command!")
		await ctx.send("When all players have joined the lobby, start the game with the \"!start_game\" command!")

	else:
		await ctx.send("You can\'t use that here!")

# Starts the game (ADD CONFIRMATION PROMPT)			
@bot.command(pass_context = True, name = 'start_game', help = 'Starts the game')
async def start_game(ctx):
	if ctx.guild:
		if bot.game_in_session:
			await ctx.send("Can\'t start game: one\'s already running!")
			return
		else:
			bot.game_in_session = True
			bot.joinable = False
			
			# Rebuild player list now that changes have been finalized
			bot.players = []
			role = discord.utils.get(ctx.message.guild.roles, name="Secret Hitler")
			for member in ctx.message.guild.members:
				if role in member.roles: 
					bot.players.append(member)
			
			# Create temporory list for assigning roles
			unassigned_players = bot.players
			
			# Check for correct player count
			if len(unassigned_players) < 5 or len(unassigned_players) > 10:
				await ctx.send("Game start failed: there aren\'t between 5 and 10 players!")
				unassigned_players = []
				await end_game(ctx)
				return
			
			await ctx.send("Game starting! (Lobby has closed)")
			
			# Generates the deck
			shuffle_deck()
			
			# Displays the game board
			lib_address, fasc_address = display_board()
			await ctx.send(file = discord.File(lib_address))
			await ctx.send(file = discord.File(fasc_address))
			
			# Decides what distribution of Fascists, Liberals, and Hitler to use based on the player count, and assigns them to people randomly
			# For 5 or 6 players, assign one Fascist + Hitler
			if len(unassigned_players) == 5 or len(unassigned_players) == 6:
				selection = randint(0, len(unassigned_players) - 1)
				member = unassigned_players[selection]
				bot.hitler = member
				await member.create_dm()
				await member.dm_channel.send(f'You are Hitler!')
				await member.dm_channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\hitler.png"))
				print("{} is Hitler".format(member.mention))
				unassigned_players.remove(member)
		
				selection = randint(0, len(unassigned_players) - 1)
				member = unassigned_players[selection]
				await member.create_dm()
				await member.dm_channel.send(f'You are a fascist!')
				await member.dm_channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\fascist.png"))
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
				await member.dm_channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\hitler.png"))
				print("{} is Hitler".format(member.mention))
				unassigned_players.remove(member)
		
				for i in range (0, 2):
					selection = randint(0, len(unassigned_players) - 1)
					member = unassigned_players[selection]
					await member.create_dm()
					await member.dm_channel.send(f'You are a fascist!')
					await member.dm_channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\fascist.png"))
					await member.dm_channel.send("{} is Hitler".format(bot.hitler.mention))
					bot.fascists.append(member)
					print("{} is a Fascist".format(member.mention))
					unassigned_players.remove(member)
		
			# For 9 or 10 players, assign three Fascists + Hitler
			else:
				selection = randint(0, len(unassigned_players) - 1)
				member = unassigned_players[selection]
				bot.hitler = member
				await member.create_dm()
				await member.dm_channel.send(f'You are Hitler!')
				await member.dm_channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\hitler.png"))
				print("{} is Hitler".format(member.mention))
				unassigned_players.remove(member)
	
				for i in range (0, 3):
					selection = randint(0, len(unassigned_players) - 1)
					member = unassigned_players[selection]
					await member.create_dm()
					await member.dm_channel.send(f'You are a fascist!')
					await member.dm_channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\fascist.png"))
					await member.dm_channel.send("{} is Hitler".format(bot.hitler.mention))
					bot.fascists.append(member)
					print("{} is a Fascist".format(member.mention))
					unassigned_players.remove(member)
			
			# For everyone that isn't a Fascist or Hitler, make them a Liberal
			for member in unassigned_players:
				await member.create_dm()
				await member.dm_channel.send(f'You are a liberal!')
				await member.dm_channel.send(file = discord.File(r"D:\Projects\Discord\Bots\Games_Bot\Secret-Hitler-Bot\Images\liberal.png"))
				bot.liberals.append(member)
				print("{} is a Liberal".format(member.mention))
			
			if bot.fascists > 1:
				for member in bot.fascists:
					temp_fascists = bot.fascists
					temp_fascists.remove(member)
					await member.dm_channel.send("Your fellow fascists are: ")
					for player in temp_fascists:
						await player.dm_channel.send("{}".format(member))
			
			# Randomly select a President from the pool of players (MIGHT BE BETTER AS OWN FUNCTION?)
			role = discord.utils.get(ctx.guild.roles, name="President")
			member = bot.players[randint(0, (len(bot.players) - 1))]
			await member.add_roles(role)
			bot.current_president = member
			await ctx.send("Our first president is... {}!".format(member.mention))
			await ctx.send("When you are ready, {}, please nominate a Chancellor with the \"!nominate @nickname\" command!".format(member.mention))
			
			print(bot.players) #This is still broken right here. Figuring out why is important. Then you can delete these weird print statements
			
	else:
		await ctx.send("You can\'t use that here!")

# Just for fun --------------------------------------------------

@bot.command(name = 'roll_dice', help = 'Simultes rolling dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
	dice = [
		str(randint(1, number_of_sides + 1))
		for _ in range(number_of_dice)
	]
	await ctx.send(','.join(dice))	

bot.run(TOKEN)