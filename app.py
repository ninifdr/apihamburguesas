from flask import Flask, request, jsonify
from pymongo import MongoClient
from functions import crear_hamburguesa, validar_patch, crear_ingrediente
import ssl
import threading

app = Flask(__name__)

uri = "mongodb+srv://bfernandezdelrio1:Luzmi2961965@hamburguesas-tqxw6.mongodb.net/test?retryWrites=true&w=majority"
#uri = "mongodb://bfernandezdelrio1:Luzmi2961965@hamburguesas-shard-00-00-tqxw6.mongodb.net:27017,hamburguesas-shard-00-01-tqxw6.mongodb.net:27017,hamburguesas-shard-00-02-tqxw6.mongodb.net:27017/test?ssl=true&replicaSet=Hamburguesas-shard-0&authSource=admin&retryWrites=true&w=majority"
client = MongoClient(uri, ssl_cert_reqs=ssl.CERT_NONE)
db = client.get_database()
#pag = "http://localhost:5000"
pag = "https://ninihamburguesasapi.herokuapp.com"

hamburguesas = db.hamburguesas
ingredientes = db.ingredientes
hamburguesa_ingrediente = db.hamburguesa_ingrediente
id_hamburguesa = 0
id_ingrediente = 0
lock = threading.Lock()

@app.route('/hamburguesa', methods=['GET'])
def get_hamburguesa():
    all_hamburguesas = list(hamburguesas.find({}, {"_id":0}))
    for hamburguesa in all_hamburguesas:
        all_ingredientes = list(hamburguesa_ingrediente.find({"id_h":hamburguesa["id"]}, {"_id":0}))
        if(len(all_ingredientes) > 0):
            for ingrediente in all_ingredientes:
                hamburguesa["ingredientes"].append({"path": pag+"/ingrediente/"+str(ingrediente["id_i"])})
    return jsonify(all_hamburguesas), 200

@app.route('/relations', methods=['GET'])
def get_relations():
    all_hamburguesas = list(hamburguesa_ingrediente.find({}, {"_id":0}))
    return jsonify(all_hamburguesas), 200

@app.route('/hamburguesa', methods=['POST'])
def post_hamburguesa():
    lock.acquire()
    global id_hamburguesa
    print(id_hamburguesa)
    data = request.get_json()
    new_hamburguesa = crear_hamburguesa(data)

    if new_hamburguesa is not None:
        new_hamburguesa["id"] = id_hamburguesa
        new_hamburguesa["ingredientes"] = []
        id_hamburguesa += 1
        inserted_hamburguer = hamburguesas.insert_one(new_hamburguesa)
        if inserted_hamburguer is None:
            lock.release()
            return jsonify(), 404
        else:
            hamburguesa = list(hamburguesas.find({"id":new_hamburguesa["id"]}, {"_id":0}))
            lock.release()
            return jsonify(hamburguesa[0]), 201
    response = {'message': 'Input inválido'}
    lock.release()
    return jsonify(response), 400

@app.route('/hamburguesa/<id>', methods=['GET'])
def get_hamburguesa_id(id):
    try:
        id = int(id)
    except:
        response = {'message': 'Id inválido'}
        return jsonify(response), 400
    hamburguesa = list(hamburguesas.find({"id":id}, {"_id":0}))
    all_ingredientes = list(hamburguesa_ingrediente.find({"id_h":id}, {"_id":0}))
    if(len(hamburguesa)>0):
        if(len(all_ingredientes) > 0):
            for ingrediente in all_ingredientes:
                hamburguesa[0]["ingredientes"].append({"path": pag+"/ingrediente/"+str(ingrediente["id_i"])})
        return jsonify(hamburguesa[0]), 200
    else:
        response = {'message': 'Hamburguesa inexistente'}
        return jsonify(response), 404

@app.route('/hamburguesa/<id>', methods=['DELETE'])
def delete_hamburguesa_id(id):
    try:
        id = int(id)
    except:
        response = {'message': 'Id inválido'}
        return jsonify(response), 400
    all_hamburguesas = list(hamburguesas.find({"id":id}, {"_id":0}))
    if(len(all_hamburguesas)) != 0:
        hamburguesas.delete_many({"id": id})
        hamburguesa_ingrediente.delete_many({"id_h": id})
        response = {'message': 'Hamburguesa eliminada'}
        return jsonify(response), 200
    else:
        response = {'message': 'Hamburguesa inexistente'}
        return jsonify(response), 404

@app.route('/hamburguesa/<id>', methods=['PATCH'])
def patch_hamburguesa_id(id):
    try:
        id = int(id)
    except:
        response = {'message': 'Id inválido'}
        return jsonify(response), 400
    data = request.get_json()
    valido = validar_patch(data)
    all_hamburguesas = list(hamburguesas.find({"id":id}, {"_id":0}))

    if(len(all_hamburguesas) == 0):
        response = {'message': 'Hamburguesa inexistente'}
        return jsonify(response), 404
    elif(valido == True):
        for key in data.keys():
            myquery = {"id": id}
            newvalues = { "$set": { key: data[key] } }
            hamburguesas.update_one(myquery, newvalues)
        all_hamburguesas = list(hamburguesas.find({"id":id}, {"_id":0}))
        return jsonify(all_hamburguesas[0]), 200
    else:
        response = {'message': 'Parámetros inválidos'}
        return jsonify(response), 400


@app.route('/hamburguesa/<id_h>/ingrediente/<id_i>', methods=['DELETE'])
def delete_hamburguesa_id_ingrediente_id(id_h,id_i):
    try:
        id_h = int(id_h)
        id_i = int(id_i)
    except:
        response = {'message': 'Id inválido'}
        return jsonify(response), 400
    all_hamburguesas = list(hamburguesas.find({"id":id_h}, {"_id":0}))
    all_ingredientes = list(ingredientes.find({"id":id_i}, {"_id":0}))
    if(len(all_hamburguesas) == 0):
        response = {'message': 'Id hamburguesa inválido'}
        return jsonify(response), 400
    all_ingredientes_hamburguesas = list(hamburguesa_ingrediente.find({"id_i":id_i, "id_h": id_h}, {"_id":0}))
    if(len(all_ingredientes_hamburguesas) == 0):
        response = {'message': 'Ingrediente inexistente en la hamburguesa'}
        return jsonify(response), 404
    hamburguesa_ingrediente.delete_many({"id_h": id_h, "id_i": id_i})
    response = {'message': 'Ingrediente retirado'}
    return jsonify(response), 200

@app.route('/hamburguesa/<id_h>/ingrediente/<id_i>', methods=['PUT'])
def put_hamburguesa_id_ingrediente_id(id_h,id_i):
    try:
        id_h = int(id_h)
        id_i = int(id_i)
    except:
        response = {'message': 'Id inválido'}
        return jsonify(response), 400
    all_hamburguesas = list(hamburguesas.find({"id":id_h}, {"_id":0}))
    all_ingredientes = list(ingredientes.find({"id":id_i}, {"_id":0}))
    if(len(all_hamburguesas) == 0):
        response = {'message': 'Hamburguesa inexistenteZ'}
        return jsonify(response), 404
    elif(len(all_ingredientes) == 0):
        response = {'message': 'Ingrediente inexistente'}
        return jsonify(response), 404
    else:
        hamb_ingr = list(hamburguesa_ingrediente.find({"id_h":id_h,"id_i":id_i}, {"_id":0}))
        if(len(hamb_ingr) == 0):
            hamburguesa_ingrediente.insert_one({"id_h": id_h, "id_i": id_i})
        response = {'message': 'Ingrediente agregado'}
        return jsonify(response), 201

@app.route('/ingrediente', methods=['GET'])
def get_ingrediente():
    all_ingredientes = list(ingredientes.find({}, {"_id":0}))
    return jsonify(all_ingredientes), 200

@app.route('/ingrediente', methods=['POST'])
def post_ingrediente():
    lock.acquire()
    global id_ingrediente
    data = request.get_json()
    new_ingrediente = crear_ingrediente(data)

    if new_ingrediente is not None:
        new_ingrediente["id"] = id_ingrediente
        id_ingrediente += 1
        inserted_ingrediente = ingredientes.insert_one(new_ingrediente)
        if inserted_ingrediente is None:
            lock.release()
            return jsonify(), 404
        else:
            ingrediente = list(ingredientes.find({"id":new_ingrediente["id"]}, {"_id":0}))
            lock.release()
            return jsonify(ingrediente[0]), 201
    response = {'message': 'Input inválido'}
    lock.release()
    return jsonify(response), 400

@app.route('/ingrediente/<id>', methods=['GET'])
def get_ingrediente_id(id):
    try:
        id = int(id)
    except:
        response = {'message': 'Id inválido'}
        return jsonify(response), 400
    ingrediente = list(ingredientes.find({"id":id}, {"_id":0}))
    if(len(ingrediente) == 0):
        response = {'message': 'Ingrediente inexistente'}
        return jsonify(response), 404
    #print(hamburguesa)
    return jsonify(ingrediente[0]), 200

@app.route('/ingrediente/<id>', methods=['DELETE'])
def delete_ingrediente_id(id):
    try:
        id = int(id)
    except:
        response = {'message': 'Id inválido'}
        return jsonify(response), 400
    all_ingredientes = list(ingredientes.find({"id":id}, {"_id":0}))
    all_ingredientes_hamburguesas = list(hamburguesa_ingrediente.find({"id_i":id}, {"_id":0}))
    if(len(all_ingredientes_hamburguesas) > 0):
        response = {'message': 'Ingrediente no se puede borrar, se encuentra presente en una hamburguesa'}
        return jsonify(response), 409
    elif(len(all_ingredientes)) != 0:
        ingredientes.delete_many({"id": id})
        response = {'message': 'Ingrediente eliminado'}
        return jsonify(response), 200
    else:
        response = {'message': 'Ingrediente inexistente'}
        return jsonify(response), 404

if __name__ == '__main__':
    app.run(debug=True)
