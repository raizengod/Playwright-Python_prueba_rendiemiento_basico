from playwright.sync_api import Page

class BarraNavLocatorPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector menú hamburguesa en formulario
    @property
    def menuHaburguesaFormulario(self):
        return self.page.get_by_role("button", name="Toggle navigation")
        
    """---------- FORMULARIO TRES ----------"""

    #Selector desplegable nav formulario tres
    @property
    def menuFormularioTres(self):
        return self.page.get_by_role("button", name="Formularios Validación tres")
    
    #Selector opción crud data table
    @property
    def opcionModalDataTable(self):
        return self.page.get_by_role("link", name= "Modal, Datatables")
    
    #Selector opción modal data table
    @property
    def opcionCrudDataTablel(self):
        return self.page.get_by_role("link", name= "Crud, Datatables")
    