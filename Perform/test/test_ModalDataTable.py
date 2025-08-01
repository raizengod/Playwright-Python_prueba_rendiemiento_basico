import random
import pytest
import re
import os
import time
from playwright.sync_api import expect
from Perform.pages.base_page import Funciones_Globales
from Perform.locator.locator_ModalDataTable import ModalDataTableLocatorPage
from Perform.utils import config

def test_buscar_dato(set_up_DataTable):
    """
    Realiza una prueba end-to-end para la funcionalidad de agregar, buscar y verificar
    datos en una tabla interactiva (Datatable) utilizando Playwright.

    La prueba sigue los siguientes pasos:
    1. Lee datos de un archivo Excel.
    2. Itera sobre cada fila del Excel, agregando un nuevo registro a la tabla
       a través de un formulario modal.
    3. Verifica que el mensaje de confirmación de registro sea exitoso.
    4. Después de registrar todos los datos, selecciona aleatoriamente una fila
       de los datos registrados.
    5. Utiliza un valor aleatorio de esa fila (Nombre, Apellido o Teléfono)
       para realizar una búsqueda en el campo de filtro de la tabla.
    6. Verifica que la tabla muestre SÓLO la fila que coincide con el término de búsqueda.
    7. Limpia el campo de búsqueda para restablecer la tabla.
    8. Verifica que la tabla vuelva a mostrar TODOS los registros originales,
       ordenados alfabéticamente por la columna 'Nombre' (ya que la tabla tiene
       esta ordenación por defecto).

    Args: 
        set_up_DataTable (Page): Objeto de página de Playwright, proporcionado por el fixture
        'set_up_DataTable', que ya ha navegado a la URL inicial de la Datatable.
    """
    
    # Inicializa el objeto 'page' de Playwright a partir del fixture.
    # Este objeto permite interactuar directamente con la página web cargada.
    page = set_up_DataTable

    # Instancia de la clase Funciones_Globales para acceder a métodos de interacción
    # genéricos con la interfaz de usuario (clicks, rellenar campos, verificaciones, etc.).
    fg = Funciones_Globales(page)
    
    # Instancia de la clase ModalDataTableLocatorPage para acceder a los localizadores
    # específicos de los elementos de la tabla y el formulario modal (botones, campos de texto, etc.).
    mdt = ModalDataTableLocatorPage(page)
    
    # --- Configuración del archivo Excel ---
    # Define el nombre del archivo Excel que contiene los datos de prueba.
    excel_file_name = "MOCK_DATA.xlsx"
    # Construye la ruta completa al archivo Excel, combinando el directorio base de datos fuente
    # con el nombre del archivo. 'config.SOURCE_FILES_DIR_DATA_FUENTE' debe estar definido en 'config.py'.
    excel_file_path = os.path.join(config.SOURCE_FILES_DIR_DATA_FUENTE, excel_file_name)
    # Especifica el nombre de la hoja dentro del archivo Excel desde la cual se leerán los datos.
    sheet_name = "data"
    # Indica si la primera fila de la hoja de Excel contiene encabezados (True) o no.
    has_header = True

    # Lista para almacenar todos los diccionarios de datos registrados desde el Excel.
    # Esta lista se utilizará posteriormente para buscar y verificar los datos en la tabla.
    datos_registrados = [] 
    
    # Obtiene el número total de filas con datos en el archivo Excel.
    num_filas = fg.num_Filas_excel(excel_file_path, sheet_name, has_header)
    # Determina el índice de la primera fila de datos en el Excel (considerando si hay encabezado o no).
    start_row_index = 2 if has_header else 1

    fg.logger.info("--- Iniciando registro de datos desde Excel en la datatable ---")
    
    # --- Medición de rendimiento: Inicio del bloque de registro de datos ---
    start_time_registro = time.time()

    # Itera sobre cada fila de datos en el archivo Excel para registrarlas en la Datatable.
    for n in range(start_row_index, num_filas + start_row_index):
        # Hace clic en el botón para agregar un nuevo registro a la tabla.
        fg.hacer_click_en_elemento(mdt.botonAgregarRegistro, "hacer_click_en_elemento_agregar_registro", config.SCREENSHOT_DIR)
        
        # Obtiene los datos de 'Nombre', 'Apellidos' y 'Teléfono' de la fila actual del Excel.
        nombre = fg.dato_Columna_excel(excel_file_path, sheet_name, n, "Nombre")
        apellido = fg.dato_Columna_excel(excel_file_path, sheet_name, n, "Apellidos")
        telef = fg.dato_Columna_excel(excel_file_path, sheet_name, n, "Teléfono")

        # Almacena los datos de la fila actual en la lista 'datos_registrados' para su posterior verificación.
        datos_registrados.append({"Nombre": nombre, "Apellidos": apellido, "Teléfono": str(telef)}) 

        fg.logger.info(f"\nProcesando Fila {n}: {nombre}, {apellido}, {telef}")

        # Rellena los campos del formulario modal con los datos obtenidos del Excel.
        fg.rellenar_campo_de_texto(mdt.campoNombre, nombre, f"rellenar_nombre_fila_{n}", config.SCREENSHOT_DIR, 0)
        fg.rellenar_campo_de_texto(mdt.campoApellido, apellido, f"rellenar_apellido_fila_{n}", config.SCREENSHOT_DIR, 0)
        fg.rellenar_campo_de_texto(mdt.campoTelefono, telef, f"rellenar_telefono_fila_{n}", config.SCREENSHOT_DIR, 0)
        
        fg.logger.info(f"Datos de fila {n} cargados: {nombre} {apellido} {telef}")
        
        # Hace clic en el botón "Enviar" del formulario para guardar el registro.
        fg.hacer_click_en_elemento(mdt.botonEnviar, f"enviar_formulario_fila_{n}", config.SCREENSHOT_DIR, "Enviar", 0)
        # Hace clic en el botón para cerrar el modal de registro después del envío.
        fg.hacer_click_en_elemento(mdt.botonCerrar, "hacer_click_en_elemento_botón_cerrar_modal", config.SCREENSHOT_DIR, 0)
        # Verifica que aparezca un mensaje de éxito después de enviar el formulario.
        fg.verificar_texto_contenido(mdt.menExitoso, "Formulario enviado exitosamente", "verificar_texto_contenido_mensaje_exitoso", config.SCREENSHOT_DIR)
        
    # --- Medición de rendimiento: Fin del bloque de registro de datos ---
    end_time_registro = time.time()
    total_time_registro = end_time_registro - start_time_registro
    # Registra el tiempo total que tomó registrar todas las entradas.
    fg.logger.info(f"PERFORMANCE: Tiempo total de registro de {len(datos_registrados)} entradas: {total_time_registro:.2f} segundos.")
    
    fg.logger.info("--- Registro de datos completado. Iniciando búsqueda y verificación ---")

    # Comprueba si se registraron datos; si no hay, la prueba falla.
    if not datos_registrados:
        fg.logger.warning("\n No se registraron datos desde el Excel. No se puede realizar la búsqueda.")
        pytest.fail("\n No hay datos para buscar en la tabla.")

    # Selecciona una fila completa de datos al azar de la lista de datos registrados.
    fila_a_buscar = random.choice(datos_registrados) 
    # Elige aleatoriamente una columna ('Nombre', 'Apellidos' o 'Teléfono')
    # de la fila seleccionada para usar como término de búsqueda.
    campo_a_buscar = random.choice(list(fila_a_buscar.keys())) 
    # Obtiene el valor correspondiente al campo seleccionado.
    valor_a_buscar = fila_a_buscar[campo_a_buscar]

    fg.logger.info(f"\nRealizando búsqueda del '{campo_a_buscar}': '{valor_a_buscar}' (de la fila: {fila_a_buscar})")

    # --- Medición de rendimiento: Inicio de la acción de búsqueda ---
    start_time_busqueda = time.time()
    # Rellena el campo de búsqueda de la tabla con el valor seleccionado aleatoriamente.
    fg.rellenar_campo_de_texto(mdt.campoBuscar, valor_a_buscar, "rellenar_campo_buscar", config.SCREENSHOT_DIR, tiempo=0.5)
    # Espera un breve momento para que la tabla se filtre y se actualice después de la búsqueda.
    page.wait_for_timeout(1000) # (1000 milisegundos = 1 segundo)
    # --- Medición de rendimiento: Fin de la acción de búsqueda ---
    end_time_busqueda = time.time()
    total_time_busqueda = end_time_busqueda - start_time_busqueda
    # Registra el tiempo que tomó ejecutar la búsqueda.
    fg.logger.info(f"PERFORMANCE: Tiempo de ejecución de la búsqueda para '{valor_a_buscar}': {total_time_busqueda:.2f} segundos.")

    fg.logger.info(f"Verificando que la tabla contenga solo la fila con '{valor_a_buscar}'...")
    # Verifica que después de la búsqueda, la tabla muestre SÓLO la fila esperada.
    es_correcto = fg.verificar_datos_filas_tabla(
        mdt.dataTable,           # Localizador de la tabla completa.
        [fila_a_buscar],         # La lista de datos esperados contiene solo la fila que se buscó.
        f"verificacion_busqueda_'{valor_a_buscar}'", # Nombre para la captura de pantalla si hay fallo.
        config.SCREENSHOT_DIR,   # Directorio para guardar capturas.
        1                 # Tiempo de espera para la verificación de cada fila.
    )

    # Si la verificación de la búsqueda es exitosa, se registra. De lo contrario, la prueba falla.
    if es_correcto:
        fg.logger.info(f"Verificación exitosa: La tabla muestra correctamente la fila buscada para '{valor_a_buscar}'.")
    else:
        fg.logger.error(f"Fallo en la verificación: La tabla NO muestra correctamente solo la fila buscada para '{valor_a_buscar}'.")
        pytest.fail(f"La verificación de la búsqueda para '{valor_a_buscar}' falló.")

    # Bloque try-except para manejar errores durante la limpieza del campo de búsqueda y la verificación final.
    try:
        # --- Medición de rendimiento: Inicio del bloque de limpieza y verificación total ---
        start_time_limpieza = time.time()
        # Rellena el campo de búsqueda con una cadena vacía para limpiar el filtro.
        fg.rellenar_campo_de_texto(mdt.campoBuscar, "", "limpiar_campo_buscar", config.SCREENSHOT_DIR, tiempo=0.5)
        fg.logger.info("Campo de búsqueda limpiado.")
        # Espera un momento para que la tabla se restablezca después de limpiar el campo.
        page.wait_for_timeout(1000) 
        
        fg.logger.info("Verificando que la tabla ha vuelto a mostrar todos los registros después de limpiar la búsqueda.")
        
        # Se crea una copia ordenada de 'datos_registrados'. Se ordena por la clave 'Nombre'
        # ya que la tabla de la UI está configurada para ordenar por esta columna por defecto.
        datos_registrados_ordenados = sorted(datos_registrados, key=lambda x: x['Nombre'])

        # Realiza la verificación de todas las filas en la tabla para asegurar que se restableció correctamente.
        es_correcto_total = fg.verificar_datos_filas_tabla(
            mdt.dataTable,                           # Localizador de la tabla.
            datos_registrados_ordenados,             # Lista de todos los datos esperados, ahora en el orden de la UI.
            "verificacion_tabla_completa_despues_limpiar", # Nombre para la captura de pantalla.
            config.SCREENSHOT_DIR,                   # Directorio para guardar capturas.
            1                                 # Tiempo de espera para la verificación.
        )
        # --- Medición de rendimiento: Fin del bloque de limpieza y verificación total ---
        end_time_limpieza = time.time()
        total_time_limpieza = end_time_limpieza - start_time_limpieza
        # Registra el tiempo que tomó limpiar el campo de búsqueda y verificar todos los registros.
        fg.logger.info(f"PERFORMANCE: Tiempo de limpieza y verificación de todos los registros: {total_time_limpieza:.2f} segundos.")

        # Si la verificación final falla, se registra un error y la prueba termina.
        if not es_correcto_total:
            fg.logger.error("Fallo: La tabla no mostró todos los registros después de limpiar la búsqueda.")
            pytest.fail("La tabla no se reseteó correctamente después de limpiar la búsqueda.")
            
    except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante el proceso de limpieza o verificación final.
        fg.logger.error(f"Error al intentar limpiar el campo de búsqueda o verificar el reinicio de la tabla: {e}")
        pytest.fail(f"Fallo en la limpieza del campo de búsqueda o verificación posterior: {e}")

    fg.logger.info("Fin de la prueba de búsqueda y verificación.")

def test_registrar_data_xml(set_up_DataTable):
    """
    Realiza una prueba end-to-end para registrar datos desde un archivo XML en una tabla
    interactiva (Datatable), seleccionar una opción de paginación y verificar la información
    de conteo de entradas de la tabla.

    La prueba sigue los siguientes pasos:
    1. Lee datos de un archivo XML ('dataset.xml').
    2. Itera sobre cada registro del XML, agregando un nuevo registro a la tabla
        a través de un formulario modal.
    3. Verifica el mensaje de confirmación de registro exitoso para cada entrada.
    4. Después de registrar todos los datos, selecciona una opción específica
        en el ComboBox de paginación ('Show entries').
    5. Extrae y parsea el texto de información de la tabla ("Showing N to X of Y entries").
    6. Compara que el número total de entradas (Y) coincida con la cantidad de registros
        exitosos realizados.
    7. Compara que el rango de entradas mostradas (N y X) sea consistente con la
        opción seleccionada en el ComboBox y el total de registros.

    Args: set_up_DataTable (Page): Objeto de página de Playwright, proporcionado por el fixture
    'set_up_DataTable', que ya ha navegado a la URL inicial de la Datatable.
    """
    
    # Inicializa el objeto 'page' de Playwright a partir del fixture.
    # Este objeto permite interactuar directamente con la página web cargada.
    page = set_up_DataTable

    # Instancia de la clase Funciones_Globales para acceder a métodos de interacción
    # genéricos con la interfaz de usuario (clicks, rellenar campos, verificaciones, etc.).
    fg = Funciones_Globales(page)
    
    # Instancia de la clase ModalDataTableLocatorPage para acceder a los localizadores
    # específicos de los elementos de la tabla y el formulario modal (botones, campos de texto, etc.).
    mdt = ModalDataTableLocatorPage(page)

    # Inicializa un contador para los registros que se añaden exitosamente a la tabla.
    reg = 0 
    
    # --- Configuración del archivo XML ---
    # Define el nombre del archivo XML que contiene los datos de prueba.
    xml_file_name = "dataset.xml"
    # Construye la ruta completa al archivo XML, combinando el directorio base de datos fuente
    # con el nombre del archivo. 'config.SOURCE_FILES_DIR_DATA_FUENTE' debe estar definido en 'config.py'.
    xml_file_path = os.path.join(config.SOURCE_FILES_DIR_DATA_FUENTE, xml_file_name)

    # Bloque try-except para manejar errores durante la lectura y procesamiento del XML.
    try:
        # --- Medición de rendimiento: Inicio de la fase de lectura y registro de datos XML ---
        start_time_xml_registro = time.time()

        # Intenta leer el archivo XML. Se espera que la función 'leer_xml' devuelva el elemento raíz.
        root_element = fg.leer_xml(xml_file_path)

        # Verifica si el elemento raíz se pudo leer correctamente. Si no, registra un error y lanza una excepción.
        if root_element is None:
            fg.logger.error("\n ❌ Error: No se pudo leer el archivo XML o está vacío/mal formado.")
            raise ValueError("No se pudo procesar el archivo XML.")

        # Busca todos los elementos 'record' dentro del XML. Se asume que cada 'record' representa una fila de datos.
        records = root_element.findall('record')

        # Si no se encuentran registros '<record>', se registra una advertencia y la función termina.
        if not records:
            fg.logger.warning(f"\n ⚠️ Advertencia: El archivo XML '{xml_file_path}' no contiene elementos '<record>' o está vacío.")
            return # Termina la prueba si no hay datos para procesar

        fg.logger.info("--- Iniciando registro de datos desde XML en la datatable ---")
        # Itera sobre cada elemento 'record' encontrado en el XML.
        for i, record_element in enumerate(records):
            # Hace clic en el botón para abrir el formulario de agregar un nuevo registro.
            fg.hacer_click_en_elemento(mdt.botonAgregarRegistro, "hacer_click_en_elemento_agregar_registro", config.SCREENSHOT_DIR)

            # Obtiene los datos de 'Nombre', 'Apellido' y 'Teléfono' del elemento 'record' actual.
            # Se usa .find('TagName').text para obtener el contenido, y se añade una verificación
            # para 'None' para evitar errores si un tag no existe.
            nombre = record_element.find('Nombre').text if record_element.find('Nombre') is not None else ""
            apellido = record_element.find('Apellido').text if record_element.find('Apellido') is not None else ""
            tlf = record_element.find('Teléfono').text if record_element.find('Teléfono') is not None else ""

            # La 'fila lógica' se usa para propósitos de log y capturas de pantalla, indicando
            # la posición del registro actual en el XML.
            n_logical_xml_row = i + 1
            fg.logger.info(f"\nProcesando Fila Lógica XML {n_logical_xml_row}: {nombre}, {apellido}, {tlf}")

            # Rellena los campos del formulario modal con los datos obtenidos del XML.
            # Se añade '_xml' al nombre de la captura para diferenciarla de otras pruebas.
            fg.rellenar_campo_de_texto(mdt.campoNombre, nombre, f"rellenar_nombre_fila_{n_logical_xml_row}_xml", config.SCREENSHOT_DIR, 0)
            fg.rellenar_campo_de_texto(mdt.campoApellido, apellido, f"rellenar_apellido_fila_{n_logical_xml_row}_xml", config.SCREENSHOT_DIR, 0)
            fg.rellenar_campo_de_texto(mdt.campoTelefono, tlf, f"rellenar_telefono_fila_{n_logical_xml_row}_xml", config.SCREENSHOT_DIR, 0)

            fg.logger.info(f"\nDatos de fila XML {n_logical_xml_row} cargados: {nombre} {apellido} {tlf}")

            # Hace clic en el botón "Enviar" del formulario para guardar el registro.
            fg.hacer_click_en_elemento(mdt.botonEnviar, f"enviar_formulario_fila_{n_logical_xml_row}_xml", config.SCREENSHOT_DIR, "Enviar", 0)
            
            # Hace clic en el botón para cerrar el modal de registro después del envío.
            fg.hacer_click_en_elemento(mdt.botonCerrar, "hacer_click_en_elemento_botón_cerrar_modal", config.SCREENSHOT_DIR, 0)
            # Verifica que aparezca un mensaje de éxito después de enviar el formulario.
            fg.verificar_texto_contenido(mdt.menExitoso, "Formulario enviado exitosamente", "verificar_texto_contenido_mensaje_exitoso", config.SCREENSHOT_DIR)
            
            # Incrementa el contador de registros exitosos.
            reg += 1
            
    except Exception as e:
        # Captura cualquier excepción inesperada que ocurra durante el procesamiento del XML.
        fg.logger.error(f"\n ❌ Ocurrió un error inesperado durante el procesamiento del XML: {e}")
        raise # Re-lanza la excepción para que Pytest marque la prueba como fallida

    # --- Medición de rendimiento: Fin de la fase de lectura y registro XML ---
    end_time_xml_registro = time.time()
    total_time_xml_registro = end_time_xml_registro - start_time_xml_registro
    # Registra el tiempo total que tomó registrar todas las entradas desde el XML.
    fg.logger.info(f"PERFORMANCE: Tiempo total de registro de {reg} entradas desde XML: {total_time_xml_registro:.2f} segundos.")

    fg.logger.info(f"\n--- Registro de datos completado. Se registraron {reg} entradas. ---")

    # --- Parte de Verificación de ComboBox y Conteo de Entradas ---

    # Define el número de entradas que se desea mostrar por página en el ComboBox.
    entries_to_show = "10" 
    fg.logger.info(f"Seleccionando '{entries_to_show}' en el ComboBox de paginación.")
    
    # --- Medición de rendimiento: Inicio de la selección del ComboBox de paginación ---
    start_time_paginacion = time.time()
    # Selecciona la opción deseada en el ComboBox de paginación.
    fg.seleccionar_opcion_por_valor(mdt.comboBoxMostrar, entries_to_show, f"seleccionar_opcion_por_valor_{entries_to_show}", config.SCREENSHOT_DIR)
    # Espera un momento para que la tabla se actualice después de la selección.
    page.wait_for_timeout(1000)
    # --- Medición de rendimiento: Fin de la selección del ComboBox de paginación ---
    end_time_paginacion = time.time()
    total_time_paginacion = end_time_paginacion - start_time_paginacion
    # Registra el tiempo que tomó seleccionar la paginación y que la tabla se actualizara.
    fg.logger.info(f"PERFORMANCE: Tiempo para seleccionar paginación '{entries_to_show}': {total_time_paginacion:.2f} segundos.")


    fg.logger.info("Verificando el texto de información de la tabla.")
    
    # Obtiene el texto completo del elemento que muestra la información de paginación de la tabla.
    info_text = fg.obtener_valor_elemento(mdt.infoDataTable, "obtener_valor_elemento_info_data_table", config.SCREENSHOT_DIR)
    fg.logger.info(f"Texto de información de la tabla encontrado: '{info_text}'")

    # Utiliza una expresión regular para extraer los números (N, X, Y) del texto.
    # El patrón busca "Showing N to X of Y entries"
    match = re.search(r"Showing (\d+) to (\d+) of (\d+) entries", info_text)

    # Verifica si la expresión regular encontró el patrón deseado.
    if match:
        # Extrae los grupos capturados por la expresión regular y los convierte a enteros.
        n_displayed = int(match.group(1)) # N: Primer número (ej. 1)
        x_displayed = int(match.group(2)) # X: Segundo número (ej. 10 o el total si es menor)
        y_total = int(match.group(3))      # Y: Tercer número (total de entradas)

        fg.logger.info(f"Valores extraídos: N={n_displayed}, X={x_displayed}, Y={y_total}")
        
        # Verifica que N sea 1 (primera entrada en la vista actual).
        assert n_displayed == 1, f"FALLO: El inicio de las entradas mostradas es {n_displayed}, se esperaba 1."
        fg.logger.info(f"Verificación exitosa: El inicio de las entradas mostradas es {n_displayed}.")

        # Calcula el valor esperado para X_displayed (el fin del rango mostrado).
        # Debe ser el mínimo entre el número de entradas a mostrar (entries_to_show) y el total de registros (reg).
        expected_x_displayed = min(int(entries_to_show), reg)
        assert x_displayed == expected_x_displayed, f"FALLO: El fin de las entradas mostradas ({x_displayed}) NO es el esperado ({expected_x_displayed})."
        fg.logger.info(f"Verificación exitosa: El fin de las entradas mostradas ({x_displayed}) es el esperado ({expected_x_displayed}).")

        # Verifica que el número total de entradas (Y) coincida con la cantidad de registros exitosos (reg).
        assert y_total == reg, f"FALLO: El total de entradas en la tabla ({y_total}) NO coincide con los registros exitosos ({reg})."
        fg.logger.info(f"Verificación exitosa: El total de entradas en la tabla ({y_total}) coincide con los registros ({reg}).")
    else:
        # Si la expresión regular no encuentra el patrón, la prueba falla y registra un error.
        fg.logger.error(f"❌ FALLO: No se pudo parsear el texto de información de la tabla: '{info_text}'. El patrón 'Showing \\d+ to \\d+ of \\d+ entries' no fue encontrado.")
        pytest.fail("No se pudo verificar el conteo de entradas de la tabla. El formato del texto de información no coincide.")

    fg.logger.info("Fin de la prueba de registro de datos XML y verificación de paginación.")
