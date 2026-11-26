"""Respuestas predefinidas del asistente virtual."""
from unidecode import unidecode

# Longitud maxima aceptada para un mensaje del usuario.
MAX_MESSAGE_LENGTH = 500

RESPUESTA_POR_DEFECTO = 'Lo siento, no entendí esa pregunta.'

# Las claves deben estar normalizadas (minusculas, sin tildes, espacios simples).
RESPUESTAS = {
    'hola': '¡Hola! ¿En qué puedo ayudarte?, si tienes alguna duda escribe comandos y se te dara una opcion para que revises en tu carro, recuerda que solo te damos una posible solucion, la opcion ideal seria llevar al mecanico',
    'problema con el motor': '¿Puedes describir el problema con el motor? dalo en solo 1 palabra ejemplo: aceleracion',
    # Antes era una tupla; el frontend la mostraba como "texto1,texto2".
    'aceleracion': ' '.join((
        '¿Has revisado el sistema de combustible o las bujías?',
        'Otra opción podría ser revisar el sistema de escape. ¿Quieres intentar eso?',
    )),
    'velocidad maxima': '¿El motor suena normal cuando alcanzas alta velocidad?',
    'ruido raro': '¿El ruido se escucha al arrancar o cuando el auto está en movimiento? si es un sonido metalico apagalo inmediatamente y llama una grua, se te puede motorear',
    'frenos': '¿Los frenos responden de manera adecuada o hay alguna dificultad para frenarse? si tienes dificultad para frenar prueba a revisar las pastillas o el piston de freno',
    'aceite': '¿Has revisado el nivel de aceite y la calidad del mismo? solo destapa el motor y en la parte superior del motor puedes sacar la tirilla que permite ver el estado del aceite OJO no lo hagas con el motor caliente',
    'agua en el radiador': '¿Has comprobado si hay alguna fuga de agua o si el radiador está sucio? recuerda que esto es vital para su funcionamiento',
    'bateria': '¿La batería se descarga rápidamente o el auto no arranca en la mañana? prueba a ver si tiene fugas de corriente',
    'aire acondicionado': '¿El aire acondicionado está funcionando correctamente o emite ruidos extraños? si es asi prueba a revisar el filtro de aire o sus conexiones',
    'luces': '¿Revisaste el estado de la bateria o las conexiones? las conexiones deja que las revise un mecanico especializado',
    'parabrisas': '¿Ya hiciste un cambio en las plumillas? Prueba con eso',
    'ruedas': '¿Las ruedas están alineadas correctamente? ¿Has revisado la presión de los neumáticos?',
    'cambio de marcha': '¿El cambio de marchas está funcionando sin problemas o hay dificultades al cambiar?',
    'suspension': '¿Has notado ruidos extraños o una sensación inestable al conducir? manda a revisar tus suspensiones o las ballestas',
    'escapes': '¿El sistema de escape emite ruidos o humo inusual? ¿Hay alguna fuga? dame el color de tu humo ejemplo humo gris, humo azul, humo negro, humo blanco, humo naranja o rojo',
    'humo blanco': '''Si el humo blanco aparece solo al inicio y luego desaparece, es probable que solo sea vapor de agua.
                     Sin embargo, si persiste, podría ser una fuga en la junta de culata, lo que permitiría que el refrigerante se mezcle con el aceite o el combustible.
                     Esto podría dañar el motor y generar sobrecalentamiento. Otra posibilidad es que la culata esté agrietada, permitiendo la filtración del refrigerante.
                     ¿Quieres revisar esto más a fondo?''',
    'humo azul': '''El humo azul generalmente indica que el motor está quemando aceite. Esto puede suceder debido al desgaste de los anillos de pistón o las válvulas,
                   lo que permite que el aceite entre en los cilindros y se queme. También puede ser causado por guías de válvulas defectuosas.
                   Si está quemando aceite, es recomendable revisar estas piezas. ¿Quieres que revisemos esto?''',
    'humo negro': '''El humo negro suele indicar que hay una mezcla rica de combustible, es decir, más combustible del necesario.
                    Esto puede ser causado por inyectores defectuosos, un sensor de oxígeno dañado o un regulador de presión defectuoso.
                    También puede ser por un filtro de aire obstruido. Si notas que el motor está funcionando de manera ineficiente o que hay un aumento en el consumo de combustible,
                    puede ser por este problema. ¿Deseas que investiguemos más sobre esto?''',
    'humo gris': '''El humo gris generalmente significa que el motor está quemando aceite. Esto puede ocurrir por desgaste en los anillos de pistón o en las válvulas.
                   Si tu vehículo tiene un turbo, también podría estar relacionado con un problema en este componente.
                   Si el humo gris es constante, es importante revisar el sistema de lubricación del motor. ¿Te gustaría revisar estos componentes?''',
    'humo naranja o rojo': '''Aunque es raro, el humo naranja o rojo puede ser una señal de problemas en el sistema de escape o componentes dañados.
                              Puede que haya algo extraño en el sistema de escape o un componente que necesita revisión.
                              ¿Quieres que revisemos el sistema de escape en detalle?''',
    'comandos': 'Estos son los comandos disponibles: \n- hola\n- problema con el motor\n- aceleracion\n- velocidad maxima\n- ruido raro\n- frenos\n- aceite\n- agua en el radiador\n- bateria\n- aire acondicionado\n- luces\n- parabrisas\n- ruedas\n- cambio de marcha\n- suspension\n- escapes',
}


def normalizar(texto):
    """Pasa a minusculas, quita tildes y colapsa los espacios."""
    return ' '.join(unidecode(texto).lower().split())


def obtener_respuesta(mensaje_usuario):
    """Devuelve la respuesta predefinida o el texto por defecto."""
    return RESPUESTAS.get(normalizar(mensaje_usuario), RESPUESTA_POR_DEFECTO)
