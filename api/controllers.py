import psycopg2

from psycopg2 import sql
from datetime import datetime

from database import db_connection
from errors import HttpNotFoundError, HttpUnprocessableEntityError

class Controllers:
   def __init__(self) -> None:
      self.db_connection = db_connection
      self.cursor        = db_connection.cursor()


   def make_transactions(self, client_id, transaction):
      self.cursor.execute(
         'SELECT saldo, limite FROM clientes WHERE id = %s',
         (client_id)
      )
      client = self.cursor.fetchone()

      if not client:
         raise HttpNotFoundError('cliente não encontrado')

      [balance, limit] = client

      if transaction['type'] == 'c':
         balance += transaction['values']
      else:
         limit_infringed = (balance - transaction['values'])
         if limit_infringed < -limit:
            raise HttpUnprocessableEntityError('O saldo é menor que o limite permitido.')
         balance = limit_infringed

      self.cursor.execute(
         'INSERT INTO transacoes (cliente_id, tipo, valor, descricao) VALUES (%s, %s, %s, %s)',
         (client_id, transaction['type'], transaction['values'], transaction['description'])
      )

      self.cursor.execute(
         'UPDATE clientes SET saldo = %s WHERE id = %s',
         (balance, client_id)
      )
      self.db_connection.commit()

      return balance, limit


   def get_extract(self, client_id):
      self.cursor.execute(
         'SELECT saldo, limite FROM clientes WHERE id = %s',
         (client_id)
      )
      client = self.cursor.fetchone()

      if not client:
         raise HttpNotFoundError('cliente não encontrado')

      [balance, limit] = client

      self.cursor.execute(
         'SELECT * FROM transacoes WHERE cliente_id = %s ORDER BY ID DESC LIMIT 10',
         (client_id)
      )

      transactions_data = self.cursor.fetchall()

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