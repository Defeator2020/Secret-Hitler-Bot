from random import *

def shuffle_deck():
	liberal_policies = 6
	fascist_policies = 11
	policies = []
	
	for card in range(0, (liberal_policies + fascist_policies)):
		random_bin = randint(0, 2)
		if random_bin == 0:
			if liberal_policies > 0:
				liberal_policies -= 1
				policies.append("liberal")
			else:
				if fascist_policies > 0:
					fascist_policies -= 1
					policies.append("fascist")
		elif random_bin >= 1:
			if fascist_policies > 0:
				fascist_policies -= 1
				policies.append("fascist")
			else:
				if liberal_policies > 0:
					liberal_policies -= 1
					policies.append("liberal")
	
	print(policies)

shuffle_deck()