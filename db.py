from pymongo import MongoClient
import logging
import sys
import config


HOST = config.HOST
PORT = config.PORT
DB_NAME = config.DB_NAME
USER = config.USER
PWD = config.PWD


class Connection():

	def __init__(self, host=HOST, port=PORT):
		try:
			logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

			self.client = MongoClient(host=HOST, port=PORT, username=USER, password=PWD, retryWrites=False, authSource=DB_NAME)

			logging.debug('Connection successful!')
		except Error as e:
			logging.debug('Error in connection')
			logging.debug(e)
			return None

	def insert_workout(self, workout):
		try:
			db = self.client[DB_NAME]
			db.workouts.insert_one(workout)
			logging.debug('Workout inserted!')	
		except Error as e:
			logging.debug('Error in inserting workout')
			logging.debug(e)

	def find_workout(self, workout, sort):
		try:
			logging.debug(workout)
			db = self.client[DB_NAME]
			result = db.workouts.find(workout, limit = 10, sort = sort)
			return result
		except Error as e:
			logging.debug('Error in searching workout')
			logging.debug(e)

	def close(self):
		try:
			self.client.close()
			logging.debug('Connection closed')
		except Error as e:
			logging.debug('Error in closing connection')
			logging.debug(e)

# client = connect_mongo()

# db = client[DB_NAME]

# insert_workout(workout)



