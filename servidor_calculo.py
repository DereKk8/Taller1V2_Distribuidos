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
            'auxiliar': {'activo': False, 'ultima_verificacion': 0}  # Añadir estado para el servidor auxiliar
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
        
    def verificar_servidores(self):
        """Verifica periódicamente el estado de los servidores de operación."""
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
                        print(f"\n✅ Servidor {tipo} está ACTIVO")
                    else:
                        print(f"\n❌ Servidor {tipo} está INACTIVO")
                        
                        # Si un servidor principal falla, verificar que el auxiliar esté activo
                        if tipo in ['aritmetico', 'avanzado'] and not activo:
                            auxiliar_activo = False
                            for s in self.servidores_operacion:
                                if s['tipo'] == 'auxiliar':
                                    auxiliar_activo = self.verificar_servidor(s['host'], s['puerto'])
                                    self.estado_servidores['auxiliar']['activo'] = auxiliar_activo
                                    break
                                    
                            if auxiliar_activo:
                                print(f"✅ Servidor auxiliar disponible para reemplazar a {tipo}")
                            else:
                                print(f"❌ Servidor auxiliar NO disponible para reemplazar a {tipo}")
            
            # Mostrar estado actual
            self.mostrar_estado_servidores()
            
            # Esperar antes de la próxima verificación
            time.sleep(5)

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
                
            # Verificar si es una notificación de cambio de estado
            if 'operacion' in solicitud and solicitud['operacion'] == 'notificar_estado':
                self.procesar_notificacion_estado(solicitud)
                respuesta = {"estado": "recibido"}
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

    def procesar_notificacion_estado(self, notificacion):
        """Procesa una notificación de cambio de estado de un servidor."""
        tipo_servidor = notificacion['tipo_servidor']
        activo = notificacion['activo']
        
        # Actualizar estado del servidor
        self.estado_servidores[tipo_servidor]['activo'] = activo
        self.estado_servidores[tipo_servidor]['ultima_verificacion'] = time.time()
        
        # Actualizar configuración de enrutamiento si es necesario
        if not activo and notificacion.get('auxiliar_disponible', False):
            print(f"\n⚠️ Servidor {tipo_servidor} está INACTIVO - Redirigiendo solicitudes al servidor auxiliar")
            # Asegurarse de que el servidor auxiliar esté en la lista de servidores
            servidor_auxiliar_encontrado = False
            for servidor in self.servidores_operacion:
                if servidor['tipo'] == 'auxiliar':
                    servidor_auxiliar_encontrado = True
                    break
                    
            if not servidor_auxiliar_encontrado:
                self.servidores_operacion.append({
                    'host': 'localhost',  # Ajustar según configuración
                    'puerto': 5003,       # Ajustar según configuración
                    'tipo': 'auxiliar'
                })
                
            # Marcar el servidor auxiliar como activo
            self.estado_servidores['auxiliar']['activo'] = True
        elif activo:
            print(f"\n✅ Servidor {tipo_servidor} está ACTIVO nuevamente - Restaurando enrutamiento normal")
        
        # Mostrar estado actual
        self.mostrar_estado_servidores()

    def seleccionar_servidor(self, tipo_operacion):
        """Selecciona el servidor adecuado según el tipo de operación y disponibilidad."""
        # Verificar si el servidor específico está activo
        if self.estado_servidores[tipo_operacion]['activo']:
            # Buscar el servidor específico
            for servidor in self.servidores_operacion:
                if servidor['tipo'] == tipo_operacion:
                    return servidor
        
        # Si el servidor específico no está disponible, usar el servidor auxiliar
        if self.estado_servidores['auxiliar']['activo']:
            # Buscar el servidor auxiliar
            for servidor in self.servidores_operacion:
                if servidor['tipo'] == 'auxiliar':
                    print(f"⚠️ Usando servidor auxiliar para operación de tipo {tipo_operacion}")
                    # Crear una copia del servidor auxiliar pero con el tipo de operación correcto
                    servidor_auxiliar = servidor.copy()
                    servidor_auxiliar['tipo_original'] = 'auxiliar'  # Guardar tipo original
                    servidor_auxiliar['tipo'] = tipo_operacion  # Cambiar tipo para que el auxiliar sepa qué operación realizar
                    return servidor_auxiliar
        
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
        """Envía una subtarea a un servidor de operación y recibe el resultado."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # Timeout de 5 segundos
                s.connect((servidor_destino['host'], servidor_destino['puerto']))
                
                # Si estamos usando el servidor auxiliar, asegurarse de que sepa qué tipo de operación realizar
                if 'tipo_original' in servidor_destino and servidor_destino['tipo_original'] == 'auxiliar':
                    subtarea['tipo'] = servidor_destino['tipo']  # Añadir el tipo de operación a la subtarea
                
                # Enviar subtarea
                s.sendall(json.dumps(subtarea).encode('utf-8'))
                
                # Recibir resultado
                resultado_data = s.recv(4096)
                resultado = json.loads(resultado_data.decode('utf-8'))
                
                # Verificar si hay error
                if 'error' in resultado:
                    print(f"Error en servidor {servidor_destino['tipo']}: {resultado['error']}")
                    raise Exception(resultado['error'])
                    
                return resultado
        except Exception as e:
            print(f"Error al comunicarse con servidor {servidor_destino['tipo']}: {str(e)}")
            # Marcar el servidor como inactivo
            self.estado_servidores[servidor_destino['tipo']]['activo'] = False
            # Intentar con el servidor auxiliar si no estábamos ya usándolo
            if 'tipo_original' not in servidor_destino or servidor_destino['tipo_original'] != 'auxiliar':
                print(f"Intentando con servidor auxiliar para operación {subtarea['operacion']}")
                return self.reenviar_a_servidor_auxiliar(subtarea)
            else:
                raise Exception(f"No se pudo completar la operación: {str(e)}")

    def reenviar_a_servidor_auxiliar(self, subtarea):
        """Reenvía una subtarea al servidor auxiliar cuando el servidor original falla."""
        # Buscar el servidor auxiliar
        servidor_auxiliar = None
        for servidor in self.servidores_operacion:
            if servidor['tipo'] == 'auxiliar':
                servidor_auxiliar = servidor
                break
        
        if not servidor_auxiliar or not self.estado_servidores['auxiliar']['activo']:
            raise Exception("Servidor auxiliar no disponible")
        
        # Añadir el tipo de operación a la subtarea
        subtarea['tipo'] = subtarea.get('tipo', self.determinar_tipo_operacion(subtarea['operacion']))
        
        # Enviar al servidor auxiliar
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((servidor_auxiliar['host'], servidor_auxiliar['puerto']))
                s.sendall(json.dumps(subtarea).encode('utf-8'))
                resultado_data = s.recv(4096)
                resultado = json.loads(resultado_data.decode('utf-8'))
                
                if 'error' in resultado:
                    raise Exception(resultado['error'])
                    
                return resultado
        except Exception as e:
            self.estado_servidores['auxiliar']['activo'] = False
            raise Exception(f"Error al comunicarse con servidor auxiliar: {str(e)}")

    def determinar_tipo_operacion(self, operacion):
        """Determina el tipo de operación basado en su nombre."""
        if operacion in ['suma', 'resta', 'multiplicacion', 'division']:
            return 'aritmetico'
        elif operacion in ['potencia', 'raiz', 'logaritmo']:
            return 'avanzado'
        else:
            return 'desconocido'
            
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