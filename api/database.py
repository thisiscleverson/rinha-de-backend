import psycopg2


db_config = {
   'user':     'rinha',
   'host':     'localhost',
   'database': 'rinha',
   'password': 'rinha',
}


db_connection = psycopg2.connect(**db_config)