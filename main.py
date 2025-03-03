import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Sistema de Cálculo Distribuido')
    parser.add_argument('componente', choices=['cliente', 'servidor_calculo', 'servidor_op1', 'servidor_op2'],
                       help='Componente a ejecutar')
    args = parser.parse_args()
    
    if args.componente == 'cliente':
        ejecutar_cliente()
    elif args.componente == 'servidor_calculo':
        ejecutar_servidor_calculo()
    elif args.componente == 'servidor_op1':
        ejecutar_servidor_operacion1()
    elif args.componente == 'servidor_op2':
        ejecutar_servidor_operacion2()
    else:
        print("Componente no reconocido")
        sys.exit(1)

def ejecutar_cliente():
    from cliente import Cliente
    
    cliente = Cliente()
    print("Cliente de cálculo distribuido")
    print("Operaciones disponibles: suma, resta, multiplicacion, division, potencia, raiz, calculo_complejo")
    
    while True:
        try:
            operacion = input("\nOperación (o 'salir' para terminar): ")
            if operacion.lower() == 'salir':
                break
                
            operandos_str = input("Operandos (separados por espacio): ")
            operandos = [float(x) for x in operandos_str.split()]
            
            resultado = cliente.enviar_solicitud(operacion, operandos)
            
            if 'error' in resultado:
                print(f"Error: {resultado['error']}")
            else:
                print(f"Resultado: {resultado['resultado']}")
                if 'tiempo_procesamiento' in resultado:
                    print(f"Tiempo de procesamiento: {resultado['tiempo_procesamiento']:.4f} segundos")
                if 'resultados_parciales' in resultado:
                    print(f"Resultados parciales: {resultado['resultados_parciales']}")
                
        except ValueError:
            print("Error: Los operandos deben ser números")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("Cliente finalizado")

def ejecutar_servidor_calculo():
    from servidor_calculo import ServidorCalculo
    
    servidor = ServidorCalculo()
    print("Iniciando servidor de cálculo...")
    servidor.iniciar()

def ejecutar_servidor_operacion1():
    # Ahora importamos directamente del archivo específico
    from servidor_operacion1 import ServidorOperacionAritmetico
    
    servidor = ServidorOperacionAritmetico()
    print("Iniciando servidor de operaciones aritméticas...")
    servidor.iniciar()

def ejecutar_servidor_operacion2():
    # Ahora importamos directamente del archivo específico
    from servidor_operacion2 import ServidorOperacionAvanzado
    
    servidor = ServidorOperacionAvanzado()
    print("Iniciando servidor de operaciones avanzadas...")
    servidor.iniciar()

if __name__ == "__main__":
    main()

# Ejemplo de uso:
# Para iniciar el servidor de cálculo:
# python main.py servidor_calculo
#
# Para iniciar el servidor de operaciones aritméticas:
# python main.py servidor_op1
#
# Para iniciar el servidor de operaciones avanzadas:
# python main.py servidor_op2
#
# Para iniciar el cliente:
# python main.py cliente