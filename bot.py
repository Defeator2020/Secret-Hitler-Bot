# bot.py
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

liberal_policies_left = 0
fascist_policies_left = 0
players = []
game_in_session = False

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
	print(f'{bot.user.name} has connected to Discord!')

@bot.command(pass_context=True, name = 'draw_policies', help='Allows the President to draw 3 new policies')
@commands.has_role('Secret Hitler')
@commands.has_role('President')
async def draw_policies(ctx):
	member = ctx.message.author
	await member.create_dm()
	await member.dm_channel.send(f'Policies will go here!')

def initialize_game():
	game_in_session = False
	liberal_policies_left = 11
	fascist_policies_left = 6
	# Call function that figures out who is playing (registers new players), and assigns them the 'Secret Hitler' role
	
	game_in_session = True

@bot.command(pass_context=True, name = 'join_game', help='Join the game')
async def join_game(ctx):
	if not game_in_session:
		role = discord.utils.get(ctx.guild.roles, name="Secret Hitler")
		if role in ctx.author.roles:
			await ctx.send(f'You\'re already part of the game!')
		else:
			await ctx.author.add_roles(role)
			await ctx.send(":white_check_mark: {} is now in the game!".format(ctx.message.author.mention))
	else:
		await ctx.send("A game is already in progress!")

@bot.command(pass_context=True, name = 'leave_game', help='Leave the game')		
async def leave_game(ctx):
	if not game_in_session:
		role = discord.utils.get(ctx.guild.roles, name="Secret Hitler")
		if role in ctx.author.roles:
			await ctx.author.remove_roles(role)
			await ctx.send(":white_check_mark: {} has now left the game!".format(ctx.message.author.mention))
		else:
			await ctx.send(f'You aren\'t part of the game yet!')

bot.run(TOKEN)