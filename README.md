# Sistema de Cálculo Distribuido

Este proyecto implementa un sistema de cálculo distribuido que permite realizar operaciones matemáticas básicas y avanzadas a través de una arquitectura cliente-servidor. El sistema está compuesto por múltiples servidores especializados que trabajan en conjunto para procesar las solicitudes de los clientes.

## Arquitectura del Sistema

El sistema está compuesto por cuatro componentes principales:

1. **Cliente**: Interfaz de usuario que permite enviar solicitudes de cálculo.
2. **Servidor de Cálculo**: Servidor principal que coordina las operaciones y distribuye el trabajo.
3. **Servidor de Operaciones Aritméticas**: Maneja operaciones básicas (suma, resta, multiplicación, división).
4. **Servidor de Operaciones Avanzadas**: Maneja operaciones complejas (potencia, raíz).

## Requisitos

- Python 3.6 o superior
- Conexión de red local (los servidores se ejecutan en localhost por defecto)

## Instalación

1. Clona este repositorio:

bash
`git clone https://github.com/DereKk8/Taller1_Distribuidos.git`
`cd calculo-distribuido`

## Uso

El sistema requiere iniciar múltiples componentes en diferentes terminales. Sigue estos pasos en orden:

1. **Inicia el Servidor de Cálculo**:
   
`python main.py servidor_calculo`

O en su defecto 

`python3 main.py servidor_calculo`

2. **Inicia el Servidor de Operaciones Aritméticas**:

`python main.py servidor_op1`

O en su defecto 

`python3 main.py servidor_op1`

3. **Inicia el Servidor de Operaciones Avanzadas**:
   
`python main.py servidor_op2`

O en su defecto 

`python3 main.py servidor_op2`

4. **Inicia el Cliente**:
   
`python main.py cliente`

O en su defecto 

bash
`python3 main.py cliente`


### Operaciones Disponibles

#### Operaciones Aritméticas (Servidor 1)
- `suma`: Suma dos o más números
- `resta`: Resta dos o más números
- `multiplicacion`: Multiplica dos o más números
- `division`: Divide dos números

#### Operaciones Avanzadas (Servidor 2)
- `potencia`: Calcula la potencia de un número
- `raiz`: Calcula la raíz de un número

#### Operacion Compleja (Servidor 1 - 2)
- `calculo_complejo`: Realiza cálculos que combinan operaciones básicas y avanzadas

### Estructura de Comandos y Ejemplos

#### Operaciones Aritméticas

1. **Suma**
   ```
   Operación: suma
   Operandos: <número1> <número2> [número3 ...]
   
   Ejemplo:
   Operación: suma
   Operandos: 5 3 2
   Resultado: 10
   ```

2. **Resta**
   ```
   Operación: resta
   Operandos: <número1> <número2> [número3 ...]
   (Resta desde el primer número los siguientes)
   
   Ejemplo:
   Operación: resta
   Operandos: 10 3 2
   Resultado: 5  # (10 - 3 - 2 = 5)
   ```

3. **Multiplicación**
   ```
   Operación: multiplicacion
   Operandos: <número1> <número2> [número3 ...]
   
   Ejemplo:
   Operación: multiplicacion
   Operandos: 2 3 4
   Resultado: 24  # (2 * 3 * 4 = 24)
   ```

4. **División**
   ```
   Operación: division
   Operandos: <dividendo> <divisor>
   
   Ejemplo:
   Operación: division
   Operandos: 10 2
   Resultado: 5.0
   ```

#### Operaciones Avanzadas

1. **Potencia**
   ```
   Operación: potencia
   Operandos: <base> <exponente>
   
   Ejemplo:
   Operación: potencia
   Operandos: 2 3
   Resultado: 8.0  # (2³ = 8)
   ```

2. **Raíz**
   ```
   Operación: raiz
   Operandos: <radicando> <índice>
   
   Ejemplo:
   Operación: raiz
   Operandos: 27 3
   Resultado: 3.0  # (∛27 = 3)
   ```

3. **Cálculo Complejo**
   ```
   Operación: calculo_complejo
   Operandos: <num1> <num2> <num3> <num4>
   (Realiza una operación compuesta: (num1 + num2) * (num3^num4))
   
   Ejemplo:
   Operación: calculo_complejo
   Operandos: 2 3 2 2
   Resultado: 20.0  # ((2 + 3) * (2² = 4) = 20)
   ```

### Notas Importantes sobre los Comandos

- Los operandos deben estar separados por espacios
- Use puntos para números decimales (ej: 3.14)
- Para números negativos, use el signo menos (ej: -5)
- El sistema mostrará errores específicos para:
  - División por cero
  - Raíz par de números negativos
  - Formato incorrecto de números
  - Cantidad incorrecta de operandos

### Ejemplo de Uso
1. Inicia el cliente
2. Selecciona una operación
3. Ingresa los operandos separados por espacios
4. Observa el resultado

## Estructura del Proyecto
calculo-distribuido

├── main.py # Punto de entrada principal

├── cliente.py # Implementación del cliente

├── servidor_calculo.py # Servidor principal de coordinación

├── servidor_operacion1.py # Servidor de operaciones aritméticas

├── servidor_operacion2.py # Servidor de operaciones avanzadas

└── README.md # Este archivo


## Características

- Procesamiento distribuido de operaciones matemáticas
- Manejo de errores robusto
- Logging detallado de operaciones
- Tiempo de procesamiento para cada operación
- Soporte para operaciones complejas que combinan múltiples cálculos

## Configuración

Los servidores utilizan las siguientes configuraciones por defecto:
- Servidor de Cálculo: `localhost:5000`
- Servidor Aritmético: `localhost:5001`
- Servidor Avanzado: `localhost:5002`
- Servidor Auxiliar: `localhost:5003`

Para modificar estas configuraciones, puedes editar los parámetros en los respectivos archivos de servidor.

## Configuración para Entorno Distribuido

Para ejecutar el sistema en múltiples computadoras, es necesario realizar cambios en las configuraciones de red de cada componente.

### 1. Preparación de la Red

- Asegúrate de que todas las máquinas estén en la misma red y puedan comunicarse entre sí
- Verifica que los puertos utilizados (5000, 5001, 5002, 5003) estén abiertos en los firewalls de todas las máquinas
- Identifica las direcciones IP de cada máquina donde se ejecutará un componente del sistema

### 2. Distribución de Componentes

Decide qué componente se ejecutará en cada máquina:
- Máquina A: Servidor de Cálculo (puerto 5000)
- Máquina B: Servidor de Operaciones Aritméticas (puerto 5001)
- Máquina C: Servidor de Operaciones Avanzadas (puerto 5002)
- Máquina D: Servidor Auxiliar (puerto 5003)
- Máquina E: Cliente

### 3. Cambios Específicos para Cada Componente

#### Para el Servidor de Cálculo (`servidor_calculo.py`)
- Modifica el parámetro `host` en el constructor `__init__`:
  ```python
  def __init__(self, host='0.0.0.0', puerto_escucha=5000):
      self.host = host
      self.puerto_escucha = puerto_escucha
  ```

- Actualiza las direcciones en `self.servidores_operacion` con las IPs reales de las máquinas:
  ```python
  self.servidores_operacion = [
      {'host': '192.168.1.B', 'puerto': 5001, 'tipo': 'aritmetico'},
      {'host': '192.168.1.C', 'puerto': 5002, 'tipo': 'avanzado'},
      {'host': '192.168.1.D', 'puerto': 5003, 'tipo': 'auxiliar'}
  ]
  ```

#### Para el Servidor de Operaciones Aritméticas (`servidor_operacion1.py`)
- Modifica el parámetro `host` en el constructor `__init__`:
  ```python
  def __init__(self, host='0.0.0.0', puerto=5001):
      self.host = host
      self.puerto = puerto
  ```

#### Para el Servidor de Operaciones Avanzadas (`servidor_operacion2.py`)
- Modifica el parámetro `host` en el constructor `__init__`:
  ```python
  def __init__(self, host='0.0.0.0', puerto=5002):
      self.host = host
      self.puerto = puerto
  ```

#### Para el Servidor Auxiliar (`servidor_auxiliar.py`)
- Modifica el parámetro `host` en el constructor `__init__`:
  ```python
  def __init__(self, host='0.0.0.0', puerto=5003):
      self.host = host
      self.puerto = puerto
      self.contador_solicitudes = 0
  ```

- Actualiza las direcciones en `self.servidores_operacion` con las IPs reales:
  ```python
  self.servidores_operacion = {
      'aritmetico': {'host': '192.168.1.B', 'puerto': 5001},
      'avanzado': {'host': '192.168.1.C', 'puerto': 5002}
  }
  ```

- Actualiza la dirección del servidor de cálculo en la función `monitorear_servidores`:
  ```python
  servidor_calculo = {'host': '192.168.1.A', 'puerto': 5000}
  ```

#### Para el Cliente (`cliente.py`)
- Modifica el parámetro `host` en el constructor `__init__` para que apunte al servidor de cálculo:
  ```python
  def __init__(self, host='192.168.1.A', puerto=5000):
      self.host = host
      self.puerto = puerto
  ```

### 4. Ejecución en Entorno Distribuido

1. Copia los archivos necesarios a cada máquina o clona el repositorio en todas ellas
2. En cada máquina, inicia el componente correspondiente:

   - Máquina A (IP: 192.168.1.A):
     ```
     python main.py servidor_calculo
     ```

   - Máquina B (IP: 192.168.1.B):
     ```
     python main.py servidor_op1
     ```

   - Máquina C (IP: 192.168.1.C):
     ```
     python main.py servidor_op2
     ```

   - Máquina D (IP: 192.168.1.D):
     ```
     python main.py servidor_auxiliar
     ```

   - Máquina E (Cliente):
     ```
     python main.py cliente
     ```

### 5. Consideraciones Adicionales

- Si ejecutas el servidor con `host='0.0.0.0'`, escuchará en todas las interfaces de red, lo que es útil para entornos distribuidos
- Asegúrate de que la función `notificar_cambio_estado` el parametro `host` en el servidor auxiliar use la IP correcta del servidor de cálculo
- Verifica que la función `reenviar_a_servidor_auxiliar` en el servidor de cálculo use la IP correcta del servidor auxiliar
- Monitorea los logs de cada componente para detectar posibles problemas de conexión

Link del proyecto: [[https://github.com/DereKk8/Taller1_Distribuidos](https://github.com/DereKk8/Taller1_Distribuidos.git)]
