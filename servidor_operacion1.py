# servidor_operacion1.py
import socket
import json
import threading
import time

class ServidorOperacionAritmetico:
    def __init__(self, host='localhost', puerto=5001):
        self.host = host
        self.puerto = puerto
        self.contador_solicitudes = 0
        
    def iniciar(self):
        """Inicia el servidor de operaciones aritméticas para escuchar solicitudes."""
        try:
            # Crear socket del servidor
            servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Permitir reutilizar la dirección
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Vincular socket a dirección y puerto
            servidor.bind((self.host, self.puerto))
            # Escuchar conexiones entrantes (máximo 5 en cola)
            servidor.listen(5)
            
            # Mostrar encabezado del servidor
            self.mostrar_encabezado_servidor()
            
            # Ciclo de aceptación de conexiones
            while True:
                cliente_socket, direccion = servidor.accept()
                print(f"\nConexión aceptada desde {direccion[0]}:{direccion[1]}")
                # Crear hilo para manejar la solicitud
                hilo_cliente = threading.Thread(
                    target=self.manejar_solicitud,
                    args=(cliente_socket, direccion)
                )
                hilo_cliente.daemon = True
                hilo_cliente.start()
                
        except KeyboardInterrupt:
            print("\nServidor detenido manualmente")
        except Exception as e:
            print(f"\nError en el servidor de operación: {str(e)}")
        finally:
            if 'servidor' in locals() and servidor:
                servidor.close()
    
    def mostrar_encabezado_servidor(self):
        """Muestra un encabezado estilizado para el servidor."""
        ancho = 80
        print("=" * ancho)
        print(f"{'SERVIDOR DE OPERACIONES ARITMÉTICAS':^{ancho}}")
        print(f"{'Escuchando en ' + self.host + ':' + str(self.puerto):^{ancho}}")
        print(f"{'Operaciones soportadas: suma, resta, multiplicacion, division':^{ancho}}")
        print("-" * ancho)
        print(f"{'Iniciado: ' + time.strftime('%Y-%m-%d %H:%M:%S'):^{ancho}}")
        print("=" * ancho)
                
    def manejar_solicitud(self, cliente_socket, direccion):
        """Maneja una solicitud de cálculo individual."""
        self.contador_solicitudes += 1
        id_solicitud = self.contador_solicitudes
        hora_recepcion = time.strftime('%H:%M:%S')
        
        try:
            # Recibir datos
            datos = cliente_socket.recv(4096).decode('utf-8')
            solicitud = json.loads(datos)
            
            # Verificar si es una solicitud de verificación de estado
            if 'operacion' in solicitud and solicitud['operacion'] == 'verificar_estado':
                respuesta = {
                    "estado": "activo",
                    "tipo": "aritmetico"
                }
                cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
                return
            
            # Mostrar información de la solicitud recibida
            self.mostrar_solicitud_recibida(id_solicitud, hora_recepcion, direccion, solicitud)
            
            # Validar solicitud
            if not self.validar_solicitud(solicitud):
                respuesta = {"error": "Solicitud inválida para el servidor de operaciones aritméticas"}
                cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
                self.mostrar_respuesta_enviada(id_solicitud, respuesta, "ERROR")
                return
                
            # Realizar cálculo
            tiempo_inicio = time.time()
            resultado = self.realizar_calculo(solicitud)
            tiempo_fin = time.time()
            tiempo_calculo = tiempo_fin - tiempo_inicio
            
            # Mostrar resultado calculado
            self.mostrar_resultado_calculado(id_solicitud, resultado, tiempo_calculo)
            
            # Enviar resultado
            cliente_socket.sendall(json.dumps(resultado).encode('utf-8'))
            
        except json.JSONDecodeError:
            respuesta = {"error": "Formato JSON inválido"}
            cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
            self.mostrar_respuesta_enviada(id_solicitud, respuesta, "ERROR")
        except Exception as e:
            respuesta = {"error": f"Error en el cálculo: {str(e)}"}
            cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
            self.mostrar_respuesta_enviada(id_solicitud, respuesta, "ERROR")
        finally:
            cliente_socket.close()
    
    def mostrar_solicitud_recibida(self, id_solicitud, hora, direccion, solicitud):
        """Muestra información detallada sobre la solicitud recibida."""
        ancho = 80
        print("\n" + "-" * ancho)
        print(f"SOLICITUD #{id_solicitud} | {hora} | Cliente: {direccion[0]}:{direccion[1]}")
        print("-" * ancho)
        
        # Detalles de la operación
        if 'operacion' in solicitud and 'operandos' in solicitud:
            op = solicitud['operacion'].upper()
            ops = str(solicitud['operandos'])
            print(f"▶ Operación: {op}")
            print(f"▶ Operandos: {ops}")
        else:
            print("▶ Solicitud malformada")
            
        print("-" * ancho)
    
    def mostrar_resultado_calculado(self, id_solicitud, resultado, tiempo_calculo):
        """Muestra el resultado calculado con formato."""
        ancho = 80
        print("\n" + "-" * ancho)
        print(f" CÁLCULO #{id_solicitud} | Tiempo: {tiempo_calculo:.6f} segundos")
        print("-" * ancho)
        
        # Mostrar resultado o error
        if 'error' in resultado:
            print(f" ERROR: {resultado['error']}")
        else:
            print(f"✓ Operación: {resultado['operacion']}")
            print(f"✓ Operandos: {resultado['operandos']}")
            print(f"✓ Resultado: {resultado['resultado']}")
        
        print("-" * ancho)
    
    def mostrar_respuesta_enviada(self, id_solicitud, respuesta, estado="OK"):
        """Muestra información sobre la respuesta enviada."""
        ancho = 80
        print("\n" + "-" * ancho)
        if estado == "OK":
            print(f"RESPUESTA #{id_solicitud} | ESTADO: ✅ Éxito")
        else:
            print(f"RESPUESTA #{id_solicitud} | ESTADO: ❌ Error")
        print("-" * ancho)
        print(f"Datos enviados: {json.dumps(respuesta, indent=2)}")
        print("-" * ancho)
            
    def validar_solicitud(self, solicitud):
        """Valida que la solicitud sea adecuada para este servidor."""
        if not isinstance(solicitud, dict) or 'operacion' not in solicitud or 'operandos' not in solicitud:
            return False
            
        # Permitir mensajes de verificación de estado
        if solicitud['operacion'] == 'verificar_estado':
            return True
            
        # Validar que el tipo de operación corresponda a este servidor (aritméticas)
        return solicitud['operacion'] in ['suma', 'resta', 'multiplicacion', 'division']
        
    def realizar_calculo(self, solicitud):
        """Realiza el cálculo aritmético solicitado."""
        operacion = solicitud['operacion']
        operandos = solicitud['operandos']

        # Responder a verificación de estado
        if operacion == 'verificar_estado':
            return {
                "estado": "activo",
                "tipo": "aritmetico"
            }
        
        try:
            if operacion == 'suma':
                resultado = sum(operandos)
            elif operacion == 'resta':
                resultado = operandos[0] - sum(operandos[1:])
            elif operacion == 'multiplicacion':
                resultado = 1
                for operando in operandos:
                    resultado *= operando
            elif operacion == 'division':
                if operandos[1] == 0:
                    return {"error": "División por cero"}
                resultado = operandos[0] / operandos[1]
            else:
                return {"error": f"Operación no soportada: {operacion}"}
                
            return {
                "operacion": operacion,
                "operandos": operandos,
                "resultado": resultado
            }
            
        except IndexError:
            return {"error": "Número insuficiente de operandos"}
        except Exception as e:
            return {"error": f"Error en el cálculo: {str(e)}"}

if __name__ == "__main__":
    servidor = ServidorOperacionAritmetico()
    servidor.iniciar()