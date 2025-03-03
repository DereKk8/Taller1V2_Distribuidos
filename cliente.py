import socket
import json
import time

class Cliente:
    def __init__(self, host='localhost', puerto=5000):
        self.host = host
        self.puerto = puerto

    def enviar_solicitud(self, operacion, operandos):
        """Envía una solicitud de cálculo al servidor principal."""
        try:
            # Crear socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Conectar al servidor
                s.connect((self.host, self.puerto))
                
                # Preparar datos
                solicitud = {
                    'operacion': operacion,
                    'operandos': operandos,
                    'timestamp': time.time()
                }
                
                # Enviar datos
                s.sendall(json.dumps(solicitud).encode('utf-8'))
                
                # Esperar respuesta
                respuesta = s.recv(4096).decode('utf-8')
                return json.loads(respuesta)
                
        except ConnectionRefusedError:
            return {"error": "No se pudo conectar con el servidor de cálculo. Verifique que esté en ejecución."}
        except Exception as e:
            return {"error": f"Error de comunicación: {str(e)}"}