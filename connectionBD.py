'''
Created on 27/04/2013

@author: Jesus Maria Gonzalez Nava
'''
import MySQLdb
class BD():
    BDconnection = ''
    cursor = ''
    
    def __init__(self):
        self.BDconnection = ''
        self.cursor = ''
        
    def setSocket(self):
        try:
            self.BDconnection =  MySQLdb.connect('localhost', 'root', 'cacopia_1', 'scanner')
            self.cursor = self.BDconnection.cursor()
        except MySQLdb.Error:
            print('Error en la conexion a la BD')
            
    def getDBconnection(self):
        return self.BDconnection
    
    def getCursor(self):
        return self.cursor

             