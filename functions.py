import validators

def crear_hamburguesa(data):
    #print(data)
    hamburguesa = {}
    hamburguesa_keys = ["nombre", "precio", "descripcion", "imagen"]
    input_keys = []
    for key in hamburguesa_keys:
        # faltan keys
        if key not in data.keys():
            return None
        else:
            hamburguesa[key] = data[key]

    for key in data.keys():
        # sobran keys
        if key not in hamburguesa_keys:
            return None

    # los numeros son numeros:
    if(isinstance(data["precio"],int) == False):
        return None
    if(isinstance(data["nombre"],str) == False):
        return None
    if(isinstance(data["descripcion"],str) == False):
        return None
    if(isinstance(data["imagen"],str) == False):
        return None
    if(validators.url(data["imagen"]) != True):
        return None

    return hamburguesa

def crear_ingrediente(data):

    ingrediente = {}
    ingrediente_keys = ["nombre", "descripcion"]
    input_keys = []
    for key in ingrediente_keys:
        if key not in data.keys():
            return None
        else:
            ingrediente[key] = data[key]

    for key in data.keys():
        if key not in ingrediente_keys:
            return None

    if(isinstance(data["descripcion"],str) == False):
        return None
    if(isinstance(data["nombre"],str) == False):
        return None

    return ingrediente

def validar_patch(data):
    hamburguesa_keys = ["nombre", "precio", "descripcion", "imagen"]
    if "id" in data.keys() or "ingredientes" in data.keys():
        return False
    for key in data.keys():
        if key not in hamburguesa_keys:
            return False
        if (key == "nombre" or key =="descripcion" or key =="imagen") and isinstance(data[key],str) == False:
            return False
        if key == "precio" and isinstance(data[key],int) == False:
            return False
    return True
