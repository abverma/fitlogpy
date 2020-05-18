from datetime import date
from datetime import datetime
from db import Connection
from subprocess import call
import pymongo

current_date = datetime.utcnow()
current_date_str = current_date.strftime('%Y-%m-%d')
meta_map = [{
	'key': 'name',
	'required': True,
	'default': None,
	'prompt': 'Enter workout name: ',
	'type': 'string'
}, {
	'key': 'type',
	'required': True,
	'default': None,
	'prompt': 'Enter workout type (strengh/cardio/mobility): ',
	'type': 'string'
}, {
	'key': 'duration',
	'required': False,
	'default': None,
	'prompt': 'Enter workout duration in minutes: ',
	'type': 'string'
}, {
	'key': 'date',
	'required': True,
	'default': current_date,
	'prompt': 'Enter workout date (yyyy-mm-dd): ',
	'type': 'date'
}, {
	'key': 'comments',
	'required': False,
	'default': None,
	'prompt': 'Enter workout comments if any: ',
	'type': 'string'
}]

prompt_by_type = {
	'strength': [{
		'name': 'category',
		'prompt': 'Enter category (bodyweight/weights): ',
		'required': False
	}, {
		'name': 'split',
		'prompt': 'Enter split (full body/upper/lower/push/pull): ',
		'required': False
	}, {
		'name': 'upper_volume',
		'prompt': 'Average upper body volume : ',
		'required': False
	}, {
		'name': 'lower_volume',
		'prompt': 'Average lower body volume : ',
		'required': False
	}]
}

def clear():
	call(["clear"])

def prompt(workout):
	for meta in meta_map:
		value = None
		if not meta['key'] in workout.keys():

			if 'prompt' in meta:
				value = input(meta['prompt'])
			else:
				value = meta['default']

			if meta['key'] == 'type' and value in prompt_by_type:
				for strenghtMeta in prompt_by_type[value]:
					typeValue = input(strenghtMeta['prompt'])
					workout[strenghtMeta['name']] = typeValue

			if meta['required']:
				if not value and not meta['default']:
					print(meta['key'], 'is required')
					return prompt()
				elif not value and meta['default']:
					value = meta['default']

			if meta['type'] == date:
				workout[meta['key']] = datetime.strptime(value, '%Y-%m-%d')
			else:
				workout[meta['key']] = value

	workout['creation_date'] = current_date
	workout['date_str'] = current_date_str

	return workout

def save_workout(workout):
	con.insert_workout(workout)
	print('New workout saved.')

def delete_workout(workout):
	con.delete_workout(workout)
	print('Workout deleted')

def copy_workout(workout):
	del workout['_id']
	workout['date'] = current_date
	workout['creation_date'] = current_date
	con.insert_workout(workout)
	print('Workout copy created')

def print_result(result):
	result_str = ''
	idx = 0
	workout_list = []
	for rec in result:
		workout_list.insert(idx, rec)

		idx += 1
		result_str += str(idx) + '. '

		for key in rec.keys():
			if key not in ['_id','date_str', 'creation_date']:
				if type(rec[key]) is datetime:
					result_str += key.title().replace('_', ' ') + ': ' + rec[key].strftime('%a %-d %b,  %Y') + '\n'
				elif 'date' in key and type(rec[key]) is str :
					result_str += key.title().replace('_', ' ') + ': ' + datetime.strptime(rec[key], '%Y-%m-%d').strftime('%a %-d %b,  %Y') + '\n'
				else:
					result_str += key.title().replace('_', ' ') + ': ' + rec[key] + '\n'

		result_str +=  '\n'

	if not len(result_str):
		result_str = 'No records found'			
		
	print('\n')
	print('-'*20)
	print('Result')
	print('-'*20)
	print(result_str)

	return workout_list

def take_action(result):

	
	idx = input('Choose workout # to copy/delete/edit: ')

	if not idx:
		return
	else: 
		idx = int(idx) - 1

		print(idx)

		workout = result[idx]

		print(workout)

		choice = input('Choose one of the following options\n1. Copy \n2. Delete \n3. Edit\n')

		if not choice:
			return 
		elif choice == '1':
			copy_workout(workout)
		elif choice == '2':
			ans = input('Are you sure? (y/n): ')
			if ans.lower() == 'y':
				delete_workout(workout)

def search_workout(workout, sort = None, limit = 0):
	print('Searching...')
	result = con.find_workout(workout, sort, limit)
	workout_list = print_result(result)
	take_action(workout_list)


def search_prompt():
	query = None
	choice = input('Search workout (name/type/duration/comments/year): ')
	if choice:
		query = { '$text': { '$search': '\"'+choice+'\"' } }
	
	return query
	
clear()
print('#'*40)
print('#' + ' '*15 +'WORKOUTS' + ' '*15 + '#')
print('#'*40)

con = Connection()

choice = input('Choose one of the following options\n1. Enter new workout\n2. Search workout\n3. List last 5 workouts\n')

clear()

if choice == '1':
	workout = prompt({})	
	save_workout(workout)
elif choice == '2':
	query = search_prompt()
	if query:
		search_workout(query)
elif choice == '3':
	search_workout({}, [('date', pymongo.DESCENDING)], 5)
else:
	print('Invalid choice')

con.close()

