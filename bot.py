from flask import Flask, request, jsonify

# Este archivo será ejecutado como módulo, no requiere que definas app directamente
app = Flask(__name__)

# Base de datos de problemas y soluciones
problemas_carro = {
    "el carro no arranca": "Verifica la batería, revisa el motor de arranque o el sistema eléctrico.",
    "hay un ruido extraño en el motor": "Podría ser una correa floja o problemas en las válvulas. Revisa también el nivel de aceite.",
    "los frenos no funcionan bien": "Revisa el nivel de líquido de frenos y verifica las pastillas de freno.",
    "el aire acondicionado no enfría": "Comprueba el gas refrigerante o posibles fugas en el sistema.",
    "hay humo saliendo del motor": "Puede ser un sobrecalentamiento. Detén el carro y verifica el sistema de refrigeración.",
}

@app.route('/bot/preguntar', methods=['POST'])
def preguntar():
    datos = request.json
    pregunta = datos.get('pregunta', '').lower()

    # Busca una solución
    respuesta = problemas_carro.get(pregunta, "Lo siento, no tengo información sobre ese problema. Te recomiendo visitar un mecánico.")
    
    return jsonify({"respuesta": respuesta})
