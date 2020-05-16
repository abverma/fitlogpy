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

def print_result(result):
	result_str = ''
	idx = 0
	
	for rec in result:
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

def search_workout(workout, sort):
	result = con.find_workout(workout, sort)
	print_result(result)


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

choice = input('Choose one of the following options\n1. Enter new workout\n2. Search workout\n3. List last 10 workouts\n')

clear()

if choice == '1':
	workout = prompt({})	
	save_workout(workout)
elif choice == '2':
	query = search_prompt()
	if query:
		search_workout(query, [])
elif choice == '3':
	search_workout({}, [('date', pymongo.DESCENDING)])
else:
	print('Invalid choice')

con.close()

