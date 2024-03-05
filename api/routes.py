from flask import Flask, jsonify, request, Blueprint

from controllers import Controllers
from errors import HttpNotFoundError, HttpUnprocessableEntityError


bp = Blueprint('clients', __name__, url_prefix='/clientes')
Controllers = Controllers()


@bp.route('/<client_id>/transacoes', methods=['POST'])
def transactions(client_id):
   json_data = request.get_json()
   try:
      if json_data['valor'] < 0: 
         raise HttpUnprocessableEntityError('Valor inválido.')
      
      elif json_data['tipo'] not in ('c', 'd'): 
         raise HttpUnprocessableEntityError('Tipo inválido.')
      
      elif not isinstance(json_data['descricao'], str) or len(json_data['descricao']) not in range(1, 11): 
         raise HttpUnprocessableEntityError('Comprimento inválido para a descrição.')
         
   except (HttpUnprocessableEntityError) as error:
      return jsonify({'message': error.message }), error.status_code

   
   try:
      [balance, limit] = Controllers.make_transactions(client_id=client_id, transaction={
         "values":      json_data['valor'],
         "type":        json_data['tipo'],
         "description": json_data['descricao']
      })
      return jsonify({'limite':limit,'saldo': balance}), 200
   
   except (HttpNotFoundError, HttpUnprocessableEntityError) as error:
      return jsonify({'message': error.message }), error.status_code
   


@bp.route('/<client_id>/extrato', methods=['GET'])
def extract(client_id):
   try:
      response = Controllers.get_extract(client_id=client_id)
      return response, 200
   except (HttpNotFoundError, HttpUnprocessableEntityError) as error:
      return jsonify({'message': error.message }), error.status_code
