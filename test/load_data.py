from config import MYSQL_HOST, MYSQL_PORT, MYSQL_PASSWORD, MYSQL_USERNAME, MYSQL_DB_NAME, ARTICLE_TABLE_NAME, USER_TABLE_NAME, DEFAULT_USER_NAME
import sys, os, json
from monsql import MonSQL
from datetime import datetime
import hashlib
from config import DATA_FILE
from util import md5


def load_data():
	return [json.loads(line) for line in open(DATA_FILE).read().split('\n') if line]

def main():

	data = load_data()

	db = MonSQL(MYSQL_HOST, MYSQL_PORT, username=MYSQL_USERNAME, password=MYSQL_PASSWORD, dbname=MYSQL_DB_NAME)
	db.set_foreign_key_check(False)
	user_table, article_table = db.get(USER_TABLE_NAME), db.get(ARTICLE_TABLE_NAME)

	article_table.remove()
	user_table.remove()

	for item in data:
		if item['author'] is None:
			item['author'] = DEFAULT_USER_NAME
		else:
			item['author'] = item['author'].replace(' ', '.')

	# Insert users
	users = [{'username': username, 'password': md5(username), 'email': '%s@gmail.com' %username, 'role': 2, 'deleted': 0} \
	          for username in set([item['author'] for item in data])]
	# Inser a bunch of zombie users
	#users += [{'username': username, 'password': md5(username), 'email': '%s@gmail.com' %username, 'role': 2, 'deleted': 0} \
	#          for username in ['zombie.user%d' % i for i in range(1000)]]

	user_ids = user_table.insert(users)
	db.commit()

	user_name_to_id_map = {}
	for user, user_id in zip(users, user_ids):
		user_name_to_id_map[user['username']] = user_id

	# Insert articles
	for article in data:
		article_table.insert({'author_id': user_name_to_id_map[article['author']],
			                  'title': article['title'],
			                  'content': article['content'],
			                  'time_create': datetime.strptime(article['time'], '%Y-%m-%d %H:%M:%S'),
			                  'time_update': datetime.now(),
			                  'state': 2, 
			                  'deleted': 0})

	db.commit()


if __name__ == '__main__':
	main()