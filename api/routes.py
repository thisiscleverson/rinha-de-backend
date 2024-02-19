from flask import Flask, jsonify, request, Blueprint

from controllers import Controllers
from errors import HttpNotFoundError, HttpUnprocessableEntityError


bp = Blueprint('clients', __name__, url_prefix='/clientes')


@bp.route('/<client_id>/transacoes', methods=['POST'])
def transactions(client_id):
   try:
      if request.json['valor'] < 0: 
         raise HttpUnprocessableEntityError('Valor inválido.')
      
      if not request.json['tipo'] in ('c', 'd'): 
         raise HttpUnprocessableEntityError('Tipo inválido.')
      
      if len(request.json['descricao']) == 0 or len(request.json['descricao']) > 10: 
         raise HttpUnprocessableEntityError('Comprimento inválido para a descrição.')
         
   except (HttpUnprocessableEntityError) as error:
      return jsonify({'message': error.message }), error.status_code

   
   try:
      [balance, limit] = Controllers().make_transactions(client_id=client_id, transaction={
         "values": request.json['valor'],
         "type": request.json['tipo'],
         "description": request.json['descricao']
      })
      return jsonify({'limite':limit,'saldo': balance}), 200
   
   except (HttpNotFoundError, HttpUnprocessableEntityError) as error:
      return jsonify({'message': error.message }), error.status_code
   


@bp.route('/<client_id>/extrato', methods=['GET'])
def extract(client_id):
   try:
      response = Controllers().get_extract(client_id)
      return response, 200
   except (HttpNotFoundError, HttpUnprocessableEntityError) as error:
      return jsonify({'message': error.message }), error.status_code
