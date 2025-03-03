import socket
import json
import threading
import time

class ServidorCalculo:
    def __init__(self, host='localhost', puerto_escucha=5000):
        self.host = host
        self.puerto_escucha = puerto_escucha
        # Configuración para los servidores de operación
        self.servidores_operacion = [
            {'host': 'localhost', 'puerto': 5001, 'tipo': 'aritmetico'},
            {'host': 'localhost', 'puerto': 5002, 'tipo': 'avanzado'},
            {'host': 'localhost', 'puerto': 5003, 'tipo': 'auxiliar'}  # Servidor auxiliar como respaldo
        ]
        # Estado de los servidores
        self.estado_servidores = {
            'aritmetico': {'activo': False, 'ultima_verificacion': 0},
            'avanzado': {'activo': False, 'ultima_verificacion': 0},
            'auxiliar': {'activo': False, 'ultima_verificacion': 0}
        }

    def iniciar(self):
        """Inicia el servidor de cálculo para escuchar solicitudes."""
        try:
            # Iniciar hilo de monitoreo de servidores
            hilo_monitoreo = threading.Thread(target=self.monitorear_servidores)
            hilo_monitoreo.daemon = True
            hilo_monitoreo.start()
            
            # Crear socket del servidor
            servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Permitir reutilizar la dirección
            servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Vincular socket a dirección y puerto
            servidor.bind((self.host, self.puerto_escucha))
            # Escuchar conexiones entrantes (máximo 5 en cola)
            servidor.listen(5)
            print(f"Servidor de cálculo iniciado en {self.host}:{self.puerto_escucha}")
            
            # Ciclo de aceptación de conexiones
            while True:
                cliente_socket, direccion = servidor.accept()
                print(f"Conexión aceptada desde {direccion}")
                # Crear hilo para manejar la solicitud
                hilo_cliente = threading.Thread(
                    target=self.manejar_solicitud,
                    args=(cliente_socket,)
                )
                hilo_cliente.daemon = True
                hilo_cliente.start()
                
        except KeyboardInterrupt:
            print("Servidor detenido manualmente")
        except Exception as e:
            print(f"Error en el servidor: {str(e)}")
        finally:
            if 'servidor' in locals() and servidor:
                servidor.close()

    def monitorear_servidores(self):
            "Monitorea periódicamente el estado de los servidores de operación."
            while True:
                for servidor in self.servidores_operacion:
                    tipo = servidor['tipo']
                    activo = self.verificar_servidor(servidor['host'], servidor['puerto'])
                    estado_anterior = self.estado_servidores[tipo]['activo']
                    self.estado_servidores[tipo]['activo'] = activo
                    self.estado_servidores[tipo]['ultima_verificacion'] = time.time()
                    
                    # Notificar cambios de estado
                    if activo != estado_anterior:
                        if activo:
                            print(f"Servidor {tipo} está ACTIVO nuevamente")
                        else:
                            print(f"Servidor {tipo} está INACTIVO")
                
                # Mostrar estado actual cada 30 segundos
                if int(time.time()) % 30 == 0:
                    self.mostrar_estado_servidores()
                    
                # Esperar antes de la próxima verificación
                time.sleep(5)

    def verificar_servidor(self, host, puerto):
        """Verifica si un servidor está activo intentando conectarse a él y enviando un mensaje de verificación."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)  # Timeout de 2 segundos
                s.connect((host, puerto))
                
                # Enviar un mensaje de verificación con formato JSON válido
                mensaje_verificacion = {
                    "operacion": "verificar_estado",
                    "operandos": []
                }
                s.sendall(json.dumps(mensaje_verificacion).encode('utf-8'))
                
                # Intentar recibir respuesta (no es necesario procesarla)
                try:
                    s.recv(1024)
                except socket.timeout:
                    pass  # Ignoramos timeout en la respuesta
                    
                return True
        except:
            return False

    def mostrar_estado_servidores(self):
        """Muestra el estado actual de los servidores monitoreados."""
        print("\n=== ESTADO DE LOS SERVIDORES ===")
        for tipo, estado in self.estado_servidores.items():
            activo = "ACTIVO" if estado['activo'] else "INACTIVO"
            ultima = time.strftime('%H:%M:%S', time.localtime(estado['ultima_verificacion']))
            print(f"Servidor {tipo}: {activo} (última verificación: {ultima})")
        print("================================\n")
                
    def manejar_solicitud(self, cliente_socket):
        """Maneja una solicitud de cálculo individual."""
        try:
            # Recibir datos del cliente
            datos = cliente_socket.recv(4096).decode('utf-8')
            solicitud = json.loads(datos)
            
            # Verificar si es una solicitud de verificación de estado
            if 'operacion' in solicitud and solicitud['operacion'] == 'verificar_estado':
                respuesta = {
                    "estado": "activo",
                    "tipo": "calculo"
                }
                cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
                return
            
            print("-----------------------------------------------------------------------------")
            print(f"Solicitud recibida: {solicitud['operacion']} {solicitud['operandos']}")
            
            # Validar solicitud
            if not self.validar_solicitud(solicitud):
                respuesta = {"error": "Solicitud inválida. Formato requerido: {'operacion': string, 'operandos': list}"}
                cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
                print(f"Solicitud inválida: {solicitud}")
                return
                
            # Determinar el tipo de operación y dividir la tarea
            subtareas = self.dividir_tarea(solicitud)
            resultados_parciales = []
            
            # Enviar subtareas a servidores de operación
            for subtarea in subtareas:
                servidor_destino = self.seleccionar_servidor(subtarea['tipo'])
                resultado = self.enviar_a_servidor_operacion(subtarea, servidor_destino)
                resultados_parciales.append(resultado)
                
            # Ensamblar resultado final
            resultado_final = self.ensamblar_resultado(resultados_parciales, solicitud)
            print(f"Resultado final: {solicitud['operacion']} {solicitud['operandos']} = {resultado_final['resultado']}")
            print("-----------------------------------------------------------------------------")
            
            # Enviar resultado al cliente
            cliente_socket.sendall(json.dumps(resultado_final).encode('utf-8'))
            
        except json.JSONDecodeError:
            respuesta = {"error": "Formato JSON inválido"}
            cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
            print("Error: Formato JSON inválido")
        except Exception as e:
            respuesta = {"error": f"Error en el procesamiento: {str(e)}"}
            cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
            print(f"Error en el procesamiento: {str(e)}")
        finally:
            cliente_socket.close()

    def seleccionar_servidor(self, tipo_operacion):
        """Selecciona el servidor adecuado según el tipo de operación y disponibilidad."""
        # Primero intentar con el servidor específico para el tipo de operación
        for servidor in self.servidores_operacion:
            if servidor['tipo'] == tipo_operacion and self.estado_servidores[tipo_operacion]['activo']:
                return servidor
        
        # Si el servidor específico no está disponible, usar el servidor auxiliar
        if self.estado_servidores['auxiliar']['activo']:
            for servidor in self.servidores_operacion:
                if servidor['tipo'] == 'auxiliar':
                    print(f"Usando servidor auxiliar para operación de tipo {tipo_operacion}")
                    return servidor
        
        # Si ningún servidor está disponible, lanzar excepción
        raise ValueError(f"No hay servidores disponibles para operaciones de tipo: {tipo_operacion}")
            
    def validar_solicitud(self, solicitud):
        """Valida que la solicitud tenga el formato correcto."""
        return (isinstance(solicitud, dict) and
                'operacion' in solicitud and
                'operandos' in solicitud and
                isinstance(solicitud['operandos'], list))
                
    def dividir_tarea(self, solicitud):
        """Divide la solicitud en subtareas para los servidores de operación."""
        operacion = solicitud['operacion']
        operandos = solicitud['operandos']
        
        if operacion in ['suma', 'resta', 'multiplicacion', 'division']:
            # Operaciones básicas van al servidor 1
            return [{'tipo': 'aritmetico', 'operacion': operacion, 'operandos': operandos}]
        elif operacion in ['potencia', 'raiz', 'logaritmo']:
            # Operaciones avanzadas van al servidor 2
            return [{'tipo': 'avanzado', 'operacion': operacion, 'operandos': operandos}]
        elif operacion == 'calculo_complejo':
            # Dividir en múltiples subtareas según la jerarquía de operaciones
            return [
                {'tipo': 'aritmetico', 'operacion': 'suma', 'operandos': operandos[0:2]},
                {'tipo': 'avanzado', 'operacion': 'potencia', 'operandos': [operandos[2], operandos[3]]},
            ]
        else:
            # Operación no reconocida
            raise ValueError(f"Operación no soportada: {operacion}")
            
    def seleccionar_servidor(self, tipo_operacion):
        """Selecciona el servidor adecuado según el tipo de operación."""
        for servidor in self.servidores_operacion:
            if servidor['tipo'] == tipo_operacion:
                return servidor
        raise ValueError(f"No hay servidor disponible para operaciones de tipo: {tipo_operacion}")
        
    def enviar_a_servidor_operacion(self, subtarea, servidor_destino):
        """Envía una subtarea al servidor de operación correspondiente."""
        try:
            # Crear socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Conectar al servidor de operación
                s.connect((servidor_destino['host'], servidor_destino['puerto']))
                
                # Enviar subtarea
                s.sendall(json.dumps(subtarea).encode('utf-8'))
                
                # Recibir respuesta
                respuesta = s.recv(4096).decode('utf-8')
                return json.loads(respuesta)
                
        except ConnectionRefusedError:
            error_msg = f"No se pudo conectar con el servidor de operación ({servidor_destino['tipo']})."
            print(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Error al comunicarse con servidor de operación: {str(e)}"
            print(error_msg)
            return {"error": error_msg}
            
    def ensamblar_resultado(self, resultados_parciales, solicitud_original):
        """Ensambla el resultado final a partir de los resultados parciales."""
        # Verificar si hay errores en los resultados parciales
        for resultado in resultados_parciales:
            if 'error' in resultado:
                error_msg = f"Error en cálculo parcial: {resultado['error']}"
                print(error_msg)
                return {"error": error_msg}
                
        # Si solo hay un resultado, devolverlo directamente
        if len(resultados_parciales) == 1:
            resultado_final = {
                'operacion': solicitud_original['operacion'],
                'operandos': solicitud_original['operandos'],
                'resultado': resultados_parciales[0]['resultado'],
                'tiempo_procesamiento': time.time() - solicitud_original.get('timestamp', time.time())
            }
            return resultado_final
            
        # Si hay múltiples resultados, combinarlos según la operación
        if solicitud_original['operacion'] == 'calculo_complejo':
            # Ejemplo: Combinar resultados de diferentes operaciones
            resultado_final = resultados_parciales[0]['resultado'] * resultados_parciales[1]['resultado']
            resultado_final_ensamblado = {
                'operacion': solicitud_original['operacion'],
                'operandos': solicitud_original['operandos'],
                'resultado': resultado_final,
                'resultados_parciales': [r.get('resultado') for r in resultados_parciales],
                'tiempo_procesamiento': time.time() - solicitud_original.get('timestamp', time.time())
            }
            return resultado_final_ensamblado
        else:
            # Para otros casos
            resultado_final = {
                'operacion': solicitud_original['operacion'],
                'resultado': resultados_parciales[0]['resultado'],
                'tiempo_procesamiento': time.time() - solicitud_original.get('timestamp', time.time())
            }
            return resultado_final