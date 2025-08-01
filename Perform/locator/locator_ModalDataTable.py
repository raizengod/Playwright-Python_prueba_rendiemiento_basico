from playwright.sync_api import Page

class ModalDataTableLocatorPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector botón agregar registro
    @property
    def botonAgregarRegistro(self):
        return self.page.get_by_role("button", name= "Agregar Registro")
    
    #Selector comboBox mostrar
    @property
    def comboBoxMostrar(self):
        return self.page.get_by_role("combobox", name= "Show entries")
    
    #Selector tabla
    @property
    def dataTable(self):
        return self.page.locator("#dataTable")
    
    #Selector campo buscar
    @property
    def campoBuscar(self):
        return self.page.get_by_role("searchbox", name="Search")
    
    
    #Selector paginación previa
    @property
    def paginaPrevia(self):
        return self.page.get_by_text('Previous')
    
    #Selector paginación Siguiente
    @property
    def paginaSiguiente(self):
        return self.page.get_by_text('Next')
    
    #Selector campo nombre
    @property
    def campoNombre(self):
        return self.page.get_by_role("textbox", name= "Nombre")
    
    #Selector campo apellido
    @property
    def campoApellido(self):
        return self.page.get_by_role("textbox", name= "Apellidos")
    
    #Selector campo teléfono
    @property
    def campoTelefono(self):
        return self.page.get_by_role("textbox", name= "Teléfono")
    
    #Selector botón teléfono
    @property
    def botonEnviar(self):
        return self.page.get_by_role("button", name= "Enviar")
    
    #Selector botón limpiar
    @property
    def botonLimpiar(self):
        return self.page.get_by_role("button", name= "Limpiar")
    
    #Selector botón cerrar
    @property
    def botonCerrar(self):
        return self.page.locator("//*[@id='addRecordModal']/div/div/div[1]/button")
    
    #Selector mensaje exitoso
    @property
    def menExitoso(self):
        return self.page.locator("#flashMessage")
    
    #Selector info data table
    @property
    def infoDataTable(self):
        return self.page.locator("//*[@id='dataTable_info']")