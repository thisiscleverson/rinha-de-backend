import psycopg

from psycopg import sql
from datetime import datetime

from db import pool
from errors import HttpNotFoundError, HttpUnprocessableEntityError

class Controllers:
   def __init__(self) -> None:
      self.pool = pool


   def make_transactions(self, client_id, transaction):
      values, type_transaction, description = transaction['values'], transaction['type'], transaction['description']

      with self.pool.connection() as conn:
         cursor = conn.execute(
            'SELECT saldo, limite FROM clientes WHERE id = %s',
            (client_id,)
         )

         client = cursor.fetchone()

         if not client:
            raise HttpNotFoundError('cliente não encontrado')

         [balance, limit] = client

         if type_transaction == 'c':
            balance += values
         elif not (limit_infringed := (balance - values)) < -limit:
            balance = limit_infringed
         else: 
            raise HttpUnprocessableEntityError('O saldo é menor que o limite permitido.')

         cursor = conn.execute(
            'UPDATE clientes SET saldo = %s WHERE id = %s',
            (balance, client_id)
         )

         conn.execute(
            'INSERT INTO transacoes (cliente_id, tipo, valor, descricao) VALUES (%s, %s, %s, %s)',
            (client_id, type_transaction, values, description)
         )
         conn.commit()

         return balance, limit


   def get_extract(self, client_id):
      with self.pool.connection() as conn:
         cursor = conn.execute(
            'SELECT saldo, limite FROM clientes WHERE id = %s',
            (client_id,)
         )
         client = cursor.fetchone()

         if not client:
            raise HttpNotFoundError('cliente não encontrado')

         [balance, limit] = client

         cursor = conn.execute(
            'SELECT * FROM transacoes WHERE cliente_id = %s ORDER BY ID DESC LIMIT 10',
            (client_id,)
         )
         transactions_data = cursor.fetchall()

         return {
         "saldo": {
            "total": balance,
            "data_extrato": datetime.utcnow().isoformat(),
            "limite": limit
         },
         "ultimas_transacoes": [
            {
               "valor": data[2],
               "tipo": data[3],
               "descricao": data[4],
               "realizada_em": data[5].isoformat()
            } 
            for data in transactions_data
         ]
      }