# inventario2dataset
Herramienta para convertir listados de inventarios en un dataset

## Ficheros de entrada
Los ficheros de entrada para esta herramienta proceden del departamento de contabilidad. Estos tienen un formato optimo para impresión pero muy malo para importaciones automáticas. Tiene ejemplos de estos ficheros en el directorio test.

## La herramienta
la aplicación examina todos los ficheros nombrados con el patron *.csv en el directorio actual. Examina cada fichero, primero procura encontrar algunos campos de la cabecera, luego en la sección detallada intenta identificar los item. Por ultimo comprueba que la cantidad total y el total del importe corresponda con los documentos

La cabecera contiene campos útiles para las relaciones entre tablas de la db.

## Por haces
- Agregar identificación de los archivos, para que no se produzcan errores procesando ficheros que no tengan el formato adecuado.
- Pulir el sistema de login. de forma que un parámetro defina el nivel de registro
- Mejorar la función 'procesar_file', probablemente dividiéndola en partes mas pequeñas para claridad del código y facilitar las pruebas.
- Limpiar las características de acceso a db, ya que se decidió separar funcionalidades en dos partes, una herramienta  que construye el dataset y luego en el sitio de Djando se procesa el dataset. Esto facilita la interoperatividad ya que desde Django se puede trabajar con diferentes motores de db. También facilita la uniformidad porque en el sitio solo se trabajara con dataset, no importa de donde venga.
