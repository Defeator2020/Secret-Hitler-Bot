# bot.py
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

players = []
game_in_session = False
liberal_policies_left = 6
liberal_policies_played = 0
fascist_policies_left = 11
fascist_policies_played = 0
policies = []
drawn_policies = []
discarded_policies = []

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

# Commands for gameplay ----------------------------------------------------------------------------------------------------

#Allows a player to join a game that isn't underway	
@bot.command(pass_context = True, name = 'join_game', help = 'Join the game')
async def join_game(ctx):
	if ctx.guild:
		if not game_in_session:
			role = discord.utils.get(ctx.guild.roles, name="Secret Hitler")
			if role in ctx.author.roles:
				await ctx.send(f'You\'re already part of the game!')
			else:
				await ctx.author.add_roles(role)
				await ctx.send(":white_check_mark: {} is now in the game!".format(ctx.message.author.mention))
		else:
			await ctx.send("A game is already in progress!")

# Allows a player to leave a game that isn't underway
@bot.command(pass_context = True, name = 'leave_game', help = 'Leave the game')		
async def leave_game(ctx):
	if ctx.guild:
		if not game_in_session:
			game_role = discord.utils.get(ctx.guild.roles, name="Secret Hitler")
			chancellor_role = discord.utils.get(ctx.guild.roles, name="Chancellor")
			president_role = discord.utils.get(ctx.guild.roles, name="President")
			if game_role in ctx.author.roles:
				await ctx.author.remove_roles(game_role)
				await ctx.author.remove_roles(chancellor_role)
				await ctx.author.remove_roles(president_role)
				await ctx.send(":white_check_mark: {} has now left the game!".format(ctx.message.author.mention))
			else:
				await ctx.send(f'You aren\'t part of the game yet!')

# Starts the game (ADD CONFIRMATION PROMPT)			
@bot.command(pass_context = True, name = 'start_game', help = 'Starts the game')
async def start_game(ctx):
	if ctx.guild:
		if not game_in_session:
			game_in_session = True

# 'Force quits' the game, just in case it gets stuck - NO WORKING YET (ADD CONFIRMATION PROMPT)
@bot.command(pass_context = True, name = 'end_game', help = 'Ends the game')
async def end_game(ctx):
	if ctx.guild:
		if game_in_session:
			game_in_session = False

# Allows the President to select a new Chancellor
@bot.command(pass_context = True, name = 'appoint', help = 'Allows the President to appoint a Chancellor (@Nickname)')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def appoint(ctx, nominee):
	if ctx.guild:
		for member in players:
			if member.mention == nominee:
					ctx.member.add_roles("Chancellor")
					await ctx.send(":white_check_mark: {} has been nominated as Chancellor!".format(ctx.member.mention))
		
		
# Allows the President to draw 3 policy cards, and DM's them the result		
@bot.command(pass_context = True, name = 'draw_policies', help = 'Allows the President to draw 3 new policies')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def draw_policies(ctx):
	if ctx.guild:
		member = ctx.message.author
		await member.create_dm()
		await member.dm_channel.send(f'Policies will go here!')

# Allows the Chancellor to play a policy card
@bot.command(pass_context = True, name = 'play_policy', help = 'Allows the Chancellor to play 1 policy, "liberal" or "fascist"')
@commands.has_role('Secret Hitler')
@commands.has_role('Chancellor')
async def play_policy(ctx, policy_type):
	if ctx.guild:
		await ctx.send("{} played a {} card!".format(ctx.message.author.mention, policy_type))
		if policy_type == "liberal":
			liberal_policies_played += 1
		elif policy_type == "fascist":
			fascist_policies_played += 1
		else:
			return

# Runs the game ----------------------------------------------------------------------------------------------------

@bot.command(pass_context = True, name = 'open_game', help = 'Allows players to join game / starts game sequence - DON\'T RUN THIS YET')
async def open_game(ctx):
	players = []
	game_in_session = False
	liberal_policies = 6
	fascist_policies = 11
	liberal_policies_played = 0
	fascist_policies_played = 0
	policies = []
	drawn_policies = []
	discarded_policies = []
	
	# Wait until game is started by command
	while not game_in_session:
		pass
	
	# Make a player list (list?)
	# Assign roles and DM them to everyone
	role = discord.utils.get(ctx.message.guild.roles, name="Secret Hitler")
	for member in ctx.message.guild.members:
			if role in member.roles: 
				players.append(member)
	
	# Make president first person in list
	# Allow president to name a chancellor
	# Voting
	
	# Remind president to draw when ready
	# Record drawn policies
	# Remove drawn policies from "deck"
	# Add played policies to "board"
	# Add unplayed policies to discarded policies "deck"
	
	# New round
	# Reassign president role to next in list
	# Take away Chancellor role

bot.run(TOKEN)