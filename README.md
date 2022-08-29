# Prueba_AnalyticsEngineer
Prueba técnica Lulo Bank

En los comentarios del archivo .pynb se encuentran instrucciones sobre el funcionamiento del script.

### Propósito:
Creado para fines laborales.  Esta prueba está basado en TVMaze y extrae toda la información necesaria para gestionar la configuración de una base de datos basica alojada en SQLite. Se Utilizo unicamente la API de TVMaze pública.  

## Enfoque General:

* **Mostrar información** (~3K registros)
    1. Configuración inicial: Extraer toda la información necesaria de TVMaze
        1. Nota: Se solicito solo traer todas las series que se emitieron en diciembre del 2020.
    1. Se estandarizan todos los datos en un unico Dataframe
    1. Cada mes (15 días): Actualizar todos los programas  
    
* **Tecnologías**
    1. API de TVMaze.com
    1. Python3
    1. SQLite
