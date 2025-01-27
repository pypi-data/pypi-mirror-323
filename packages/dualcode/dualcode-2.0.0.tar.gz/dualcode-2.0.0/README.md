# Mi Paquete

Este es un paquete en Python para gestionar variables y almacenarlas en un archivo JSON.


# Como usar
from dualcode import saveVar, deleteVar, seeAllVar, getVar

hola = 10
adios = 20
saveVar(hola)
saveVar(adios)

print(seeAllVar())  # Shows all saved variables

x = getVar('hola')  # Returns 42
print(x)

deleteVar('adios')
print(seeAllVar())  # Shows all saved variables