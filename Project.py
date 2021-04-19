# -*- coding: iso-8859-15
'''
Created on 02/05/2013

@author: Jesus Maria Gonzalez Nava
'''
from Scanner import *
import sys
if __name__ == '__main__':
        credential = int(sys.argv[1])
        print('Valor de credential: ' + str(credential))
        if credential == 1:
            objMineria = MineriaDatos()
            objMineria.setConnectionBD()
            objMineria.setNameScan(sys.argv[2])
            objMineria.setUrl(sys.argv[6])
            objMineria.setCretedBy(sys.argv[7])
            objMineria.setMechanizeAuth(sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
            #                          URLAutenticar,   User,      Password,     Url Analizar
        else:
            objMineria = MineriaDatos()
            objMineria.setConnectionBD()
            objMineria.setNameScan(sys.argv[3])
            objMineria.setUrl(sys.argv[2])
            objMineria.setCretedBy(sys.argv[4])
            objMineria.setMechanize(sys.argv[2])#url para analizar
 
            