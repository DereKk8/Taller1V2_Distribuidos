# servidor_auxiliar.py
import socket
import json
import math
import threading
import time

class ServidorAuxiliar:
    def __init__(self, host='localhost', puerto=5003):
        self.host = host
        self.puerto = puerto
        self.contador_solicitudes = 0
        # Estado de los servidores de operación
        self.estado_servidores = {
            'aritmetico': {'activo': False, 'ultima_verificacion': 0},
            'avanzado': {'activo': False, 'ultima_verificacion': 0}
        }
        # Información de los servidores de operación
        self.servidores_operacion = {
            'aritmetico': {'host': 'localhost', 'puerto': 5001},
            'avanzado': {'host': 'localhost', 'puerto': 5002}
        }
        
    def iniciar(self):
        """Inicia el servidor auxiliar para escuchar solicitudes y monitorear otros servidores."""
        try:
            # Iniciar hilo de monitoreo
            hilo_monitoreo = threading.Thread(target=self.monitorear_servidores)
            hilo_monitoreo.daemon = True
            hilo_monitoreo.start()
            
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
            print(f"\nError en el servidor auxiliar: {str(e)}")
        finally:
            if 'servidor' in locals() and servidor:
                servidor.close()
    
    def monitorear_servidores(self):
        """Monitorea periódicamente el estado de los servidores de operación."""
        # También monitorear el servidor de cálculo
        servidor_calculo = {'host': 'localhost', 'puerto': 5000}
        estado_servidor_calculo = False
        
        while True:
            # Verificar servidores de operación
            for tipo, info in self.servidores_operacion.items():
                activo = self.verificar_servidor(info['host'], info['puerto'])
                estado_anterior = self.estado_servidores[tipo]['activo']
                self.estado_servidores[tipo]['activo'] = activo
                self.estado_servidores[tipo]['ultima_verificacion'] = time.time()
                
                # Notificar cambios de estado
                if activo != estado_anterior:
                    if activo:
                        print(f"\n✅ Servidor {tipo} está ACTIVO nuevamente")
                    else:
                        print(f"\n❌ Servidor {tipo} está INACTIVO - Asumiendo sus funciones")
            
            # Verificar servidor de cálculo
            activo_calculo = self.verificar_servidor(servidor_calculo['host'], servidor_calculo['puerto'])
            if activo_calculo != estado_servidor_calculo:
                estado_servidor_calculo = activo_calculo
                if activo_calculo:
                    print(f"\n✅ Servidor de cálculo está ACTIVO")
                else:
                    print(f"\n❌ Servidor de cálculo está INACTIVO")
            
            # Mostrar estado actual cada 10 segundos
            if int(time.time()) % 10 == 0:
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
                
                # Intentar recibir respuesta y verificar que sea válida
                try:
                    respuesta_data = s.recv(1024)
                    if not respuesta_data:
                        return False
                    
                    # Intentar decodificar la respuesta como JSON
                    try:
                        respuesta = json.loads(respuesta_data.decode('utf-8'))
                        # Verificar que la respuesta contenga el campo "estado"
                        if 'estado' in respuesta and respuesta['estado'] == 'activo':
                            return True
                        else:
                            return False
                    except json.JSONDecodeError:
                        return False
                        
                except socket.timeout:
                    return False  # Si hay timeout en la respuesta, el servidor no está activo
                    
                return False  # Por defecto, considerar inactivo si no se cumple lo anterior
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False  # Si no se puede conectar, el servidor no está activo
        except Exception as e:
            print(f"Error al verificar servidor {host}:{puerto}: {str(e)}")
            return False  # Cualquier otra excepción, considerar inactivo

    
    def mostrar_estado_servidores(self):
        """Muestra el estado actual de los servidores monitoreados."""
        ancho = 80
        print("\n" + "=" * ancho)
        print(f"{'ESTADO DE LOS SERVIDORES':^{ancho}}")
        print("-" * ancho)
        
        for tipo, estado in self.estado_servidores.items():
            activo = "✅ ACTIVO" if estado['activo'] else "❌ INACTIVO"
            ultima = time.strftime('%H:%M:%S', time.localtime(estado['ultima_verificacion']))
            print(f"Servidor {tipo.upper()}: {activo} (última verificación: {ultima})")
        
        # También mostrar estado del servidor de cálculo
        servidor_calculo = {'host': 'localhost', 'puerto': 5000}
        activo_calculo = self.verificar_servidor(servidor_calculo['host'], servidor_calculo['puerto'])
        print(f"Servidor CÁLCULO: {'✅ ACTIVO' if activo_calculo else '❌ INACTIVO'}")
        
        print("=" * ancho)
    
    def mostrar_encabezado_servidor(self):
        """Muestra un encabezado estilizado para el servidor."""
        ancho = 80
        print("=" * ancho)
        print(f"{'SERVIDOR AUXILIAR CON TOLERANCIA A FALLOS':^{ancho}}")
        print(f"{'Escuchando en ' + self.host + ':' + str(self.puerto):^{ancho}}")
        print(f"{'Operaciones soportadas: todas (respaldo)':^{ancho}}")
        print("-" * ancho)
        print(f"{'Iniciado: ' + time.strftime('%Y-%m-%d %H:%M:%S'):^{ancho}}")
        print("=" * ancho)
                
    def manejar_solicitud(self, cliente_socket, direccion):
        """Maneja una solicitud de cálculo individual."""
        try:
            # Recibir datos
            datos = cliente_socket.recv(4096).decode('utf-8')
            solicitud = json.loads(datos)
            
            # Verificar si es una solicitud de verificación de estado
            if 'operacion' in solicitud and solicitud['operacion'] == 'verificar_estado':
                # Responder directamente sin realizar ningún cálculo
                respuesta = {
                    "estado": "activo",
                    "tipo": "auxiliar"
                }
                cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
                return
            
            # Para solicitudes normales, continuar con el procesamiento habitual
            self.contador_solicitudes += 1
            id_solicitud = self.contador_solicitudes
            hora_recepcion = time.strftime('%H:%M:%S')
            
            # Mostrar información de la solicitud recibida
            self.mostrar_solicitud_recibida(id_solicitud, hora_recepcion, direccion, solicitud)
            
            # Validar solicitud
            if not self.validar_solicitud(solicitud):
                respuesta = {"error": "Solicitud inválida para el servidor auxiliar"}
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
            if 'id_solicitud' in locals():
                self.mostrar_respuesta_enviada(id_solicitud, respuesta, "ERROR")
        except Exception as e:
            respuesta = {"error": f"Error en el cálculo: {str(e)}"}
            cliente_socket.sendall(json.dumps(respuesta).encode('utf-8'))
            if 'id_solicitud' in locals():
                self.mostrar_respuesta_enviada(id_solicitud, respuesta, "ERROR")
        finally:
            cliente_socket.close()
    
    def mostrar_solicitud_recibida(self, id_solicitud, hora, direccion, solicitud):
        """Muestra información detallada sobre la solicitud recibida."""
        ancho = 80
        print("\n" + "*" * ancho)
        print(f"SOLICITUD #{id_solicitud} | {hora} | Cliente: {direccion[0]}:{direccion[1]}")
        print("*" * ancho)
        
        # Detalles de la operación
        if 'operacion' in solicitud and 'operandos' in solicitud:
            op = solicitud['operacion'].upper()
            ops = str(solicitud['operandos'])
            print(f"▶ Operación: {op}")
            print(f"▶ Operandos: {ops}")
            print(f"▶ Tipo: {solicitud.get('tipo', 'No especificado')}")
            
            # Mostrar información adicional específica para cada operación
            if solicitud['operacion'] == 'potencia':
                print(f"   • Base: {solicitud['operandos'][0]}")
                print(f"   • Exponente: {solicitud['operandos'][1]}")
            elif solicitud['operacion'] == 'raiz':
                print(f"   • Radicando: {solicitud['operandos'][0]}")
                print(f"   • Índice: {solicitud['operandos'][1]}")
        else:
            print("▶ Solicitud malformada")
            
        print("*" * ancho)
    
    def mostrar_resultado_calculado(self, id_solicitud, resultado, tiempo_calculo):
        """Muestra el resultado calculado con formato."""
        ancho = 80
        print("\n" + "*" * ancho)
        print(f"CÁLCULO #{id_solicitud} | Tiempo: {tiempo_calculo:.6f} segundos")
        print("*" * ancho)
        
        # Mostrar resultado o error
        if 'error' in resultado:
            print(f"ERROR: {resultado['error']}")
        else:
            print(f"✓ Operación: {resultado['operacion']}")
            print(f"✓ Operandos: {resultado['operandos']}")
            print(f"✓ Resultado: {resultado['resultado']}")
            
            # Mostrar información adicional según la operación
            if resultado['operacion'] == 'potencia':
                if resultado['resultado'].is_integer():
                    print(f"  └ {resultado['operandos'][0]}^{resultado['operandos'][1]} = {int(resultado['resultado'])}")
                else:
                    print(f"  └ {resultado['operandos'][0]}^{resultado['operandos'][1]} = {resultado['resultado']:.6f}")
            elif resultado['operacion'] == 'raiz':
                print(f"  └ {resultado['operandos'][1]}√{resultado['operandos'][0]} = {resultado['resultado']:.6f}")
        
        print("*" * ancho)
    
    def mostrar_respuesta_enviada(self, id_solicitud, respuesta, estado="OK"):
        """Muestra información sobre la respuesta enviada."""
        ancho = 80
        print("\n" + "*" * ancho)
        if estado == "OK":
            print(f"RESPUESTA #{id_solicitud} | ESTADO: ✅ Éxito")
        else:
            print(f"RESPUESTA #{id_solicitud} | ESTADO: ❌ Error")
        print("*" * ancho)
        print(f"Datos enviados: {json.dumps(respuesta, indent=2)}")
        print("*" * ancho)
            
    def validar_solicitud(self, solicitud):
        """Valida que la solicitud tenga el formato correcto."""
        if not isinstance(solicitud, dict) or 'operacion' not in solicitud or 'operandos' not in solicitud:
            return False
            
        # Permitir mensajes de verificación de estado
        if solicitud['operacion'] == 'verificar_estado':
            return True
            
        return isinstance(solicitud['operandos'], list)
        
    def realizar_calculo(self, solicitud):
        """Realiza el cálculo solicitado (aritmético o avanzado)."""
        operacion = solicitud['operacion']
        operandos = solicitud['operandos']

        if operacion == 'verificar_estado':
            return {
                "estado": "activo",
                "tipo": "auxiliar"
            }

        tipo = solicitud.get('tipo', self.determinar_tipo_operacion(operacion))
        
        try:
            # Operaciones aritméticas
            if tipo == 'aritmetico':
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
                    return {"error": f"Operación aritmética no soportada: {operacion}"}
            
            # Operaciones avanzadas
            elif tipo == 'avanzado':
                if operacion == 'potencia':
                    resultado = math.pow(operandos[0], operandos[1])
                elif operacion == 'raiz':
                    if operandos[0] < 0 and operandos[1] % 2 == 0:
                        return {"error": "No se puede calcular raíz par de número negativo"}
                    resultado = math.pow(operandos[0], 1/operandos[1])
                elif operacion == 'logaritmo':
                    if operandos[0] <= 0 or operandos[1] <= 0 or operandos[1] == 1:
                        return {"error": "Argumentos inválidos para logaritmo"}
                    resultado = math.log(operandos[0], operandos[1])
                else:
                    return {"error": f"Operación avanzada no soportada: {operacion}"}
            else:
                return {"error": f"Tipo de operación no reconocido: {tipo}"}
                
            return {
                "operacion": operacion,
                "operandos": operandos,
                "resultado": resultado
            }
            
        except IndexError:
            return {"error": "Número insuficiente de operandos"}
        except Exception as e:
            return {"error": f"Error en el cálculo: {str(e)}"}
    
    def determinar_tipo_operacion(self, operacion):
        """Determina el tipo de operación basado en su nombre."""
        if operacion in ['suma', 'resta', 'multiplicacion', 'division']:
            return 'aritmetico'
        elif operacion in ['potencia', 'raiz', 'logaritmo']:
            return 'avanzado'
        else:
            return 'desconocido'

if __name__ == "__main__":
    servidor = ServidorAuxiliar()
    servidor.iniciar()