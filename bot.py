# bot.py
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

bot.players = []
bot.game_in_session = False
bot.joinable = False
bot.liberal_policies_left = 6
bot.liberal_policies_played = 0
bot.fascist_policies_left = 11
bot.fascist_policies_played = 0
bot.policies = []
bot.drawn_policies = []
bot.discarded_policies = []


@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

# Commands for gameplay ----------------------------------------------------------------------------------------------------

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

# 'Force quits' the game, just in case it gets stuck - NO WORKING YET (ADD CONFIRMATION PROMPT)
@bot.command(pass_context = True, name = 'end_game', help = 'Ends the game')
async def end_game(ctx):
	if ctx.guild:
		if bot.game_in_session:
			bot.game_in_session = False
			for member in bot.players:
					member.remove_roles("Secret Hitler")
					member.remove_roles("President")
					member.remove_roles("Chancellor")
					await ctx.send("{} has left the game".format(member.mention))
			await ctx.send("Game ended.")
		else:
			await ctx.send("Can't end game: one isn\'t running!")

@bot.command(pass_context = True, name = 'player_count', help = 'Reports joined players (mostly for debug)')
async def player_count(ctx):
	if len(bot.players) == 0:
		await ctx.send("There aren\'t any players!")
	else:
		await ctx.send("Players:")
		for player in bot.players:
			await ctx.send(player.mention)
			
# Allows the President to select a new Chancellor
@bot.command(pass_context = True, name = 'appoint', help = 'Allows the President to appoint a Chancellor (@nickname)')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def appoint(ctx, nominee):
	if ctx.guild:
		if bot.game_in_session:
			for member in bot.players:
				if member.mention == nominee:
						member.add_roles("Chancellor")
						await ctx.send(":white_check_mark: {} has been nominated as Chancellor!".format(ctx.member.mention))
		
		
# Allows the President to draw 3 policy cards, and DM's them the result		
@bot.command(pass_context = True, name = 'draw_policies', help = 'Allows the President to draw 3 new policies')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def draw_policies(ctx):
	if ctx.guild:
		if bot.game_in_session:
			member = ctx.message.author
			await member.create_dm()
			await member.dm_channel.send(f'Policies will go here!')

# Allows the Chancellor to play a policy card
@bot.command(pass_context = True, name = 'play_policy', help = 'Allows the Chancellor to play 1 policy, "liberal" or "fascist"')
@commands.has_role('Secret Hitler')
@commands.has_role('Chancellor')
async def play_policy(ctx, policy_type):
	if ctx.guild:
		if bot.game_in_session:
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
	
	
# Runs the game ----------------------------------------------------------------------------------------------------

@bot.command(pass_context = True, name = 'open_game', help = 'Allows players to join game / starts game sequence - DON\'T RUN THIS YET')
async def open_game(ctx):
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
	
	await ctx.send("Game open!")

# Starts the game (ADD CONFIRMATION PROMPT)			
@bot.command(pass_context = True, name = 'start_game', help = 'Starts the game')
async def start_game(ctx):
	if ctx.guild:
		if not bot.game_in_session:
			bot.game_in_session = True
			bot.joinable = False
			await ctx.send("Game started! (Joining has closed)")
		else:
			await ctx.send("Can\'t start game: one\'s already running!")
	
	# Rebuild player list now that changes have been finalized
	bot.players = []
	role = discord.utils.get(ctx.message.guild.roles, name="Secret Hitler")
	for member in ctx.message.guild.members:
			if role in member.roles: 
				bot.players.append(member)
	
	lib_address, fasc_address = display_board()
	await ctx.send(file = discord.File(lib_address))
	await ctx.send(file = discord.File(fasc_address))
	
	# Create temporory list for assigning roles
	unassigned_players = bot.players
	
	if len(unassigned_players) == 5 or len(unassigned_players) == 6:
		selection = random.choice(range(0, len(unassigned_players) - 1))
		member = unassigned_players[selection]
		await member.create_dm()
		await member.dm_channel.send(f'You are Hitler!')
		unassigned_players.remove(member)
		
		selection = random.choice(range(0, len(unassigned_players) - 1))
		member = unassigned_players[selection]
		await member.create_dm()
		await member.dm_channel.send(f'You are a fascist!')
		unassigned_players.remove(member)
		
	elif len(unassigned_players) == 7 or len(unassigned_players) == 8:
		selection = random.choice(range(0, len(unassigned_players) - 1))
		member = unassigned_players[selection]
		await member.create_dm()
		await member.dm_channel.send(f'You are Hitler!')
		unassigned_players.remove(member)
		
		for i in range (0, 2):
			selection = random.choice(range(0, len(unassigned_players) - 1))
			member = unassigned_players[selection]
			await member.create_dm()
			await member.dm_channel.send(f'You are a fascist!')
			unassigned_players.remove(member)
		

	elif len(unassigned_players) == 9 or len(unassigned_players) == 10:
		selection = random.choice(range(0, len(unassigned_players) - 1))
		member = unassigned_players[selection]
		await member.create_dm()
		await member.dm_channel.send(f'You are Hitler!')
		unassigned_players.remove(member)
		
		for i in range (0, 3):
			selection = random.choice(range(0, len(unassigned_players) - 1))
			member = unassigned_players[selection]
			await member.create_dm()
			await member.dm_channel.send(f'You are a fascist!')
			unassigned_players.remove(member)

	selection = random.choice(range(0, len(bot.players) - 1))
	member = bot.players[selection]
	member.add_roles("President")
	await ctx.send("Our first president is... {}!".format(member.mention))
	await ctx.send("When you are ready, {}, please appoint a Chancellor with the \"!appoint @nickname\" command!".format(member.mention))
	
# Voting function right in here -> part of appoint?

# Remind president to draw when ready
# Record drawn policies
# Remove drawn policies from "deck"
# Add played policies to "board"
# Add unplayed policies to discarded policies "deck"
	
# New round
# Reassign president role to next in list
# Take away Chancellor role

# Just for fun --------------------------------------------------

@bot.command(name = 'roll_dice', help = 'Simultes rolling dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
	dice = [
		str(random.choice(range(1, number_of_sides + 1)))
		for _ in range(number_of_dice)
	]
	await ctx.send(','.join(dice))	

bot.run(TOKEN)