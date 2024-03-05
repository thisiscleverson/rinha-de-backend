import psycopg_pool


db_url = 'host={} dbname={} user={} password={}'.format(
   'localhost',
   'rinha',
   'rinha',
   'rinha'   
)

pool = psycopg_pool.ConnectionPool(
   conninfo=db_url,
   min_size=2,
   max_size=20
)