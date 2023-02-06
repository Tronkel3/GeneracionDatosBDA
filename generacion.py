# -*- coding: utf-8 -*-
"""
Created on Mon Jan 30 18:10:59 2023

@author: javil
"""

import re
import random as r
from bs4 import BeautifulSoup
import requests
import csv

letras = list('TRWAGMYFPDXBNJZSQVHLCKE')
dnis = dict(zip(range(0, 23), letras))

with open('nombres.txt', 'r', encoding='utf-8') as f_nombres:
    nombres = f_nombres.read().split('\n')
    nombres.append('NULL')
            
with open('apellidos.txt', 'r', encoding='utf-8') as f_apellidos:
    apellidos = f_apellidos.read().split('\n')
    apellidos.append('NULL')
       
def dni(num):
    letra = dnis[num%23]
    return str(num)+letra

direcciones = {'Plaza':[], 'Avenida':[], 'Calle':[]}

def carga_direcciones():
    url = 'https://es.wikipedia.org/wiki/Anexo:Calles_de_Valencia'
    respuesta = requests.get(url)
    soup = BeautifulSoup(respuesta.text, 'lxml')
    tabla = soup.table
    rows = tabla.find_all('tr')
    for row in rows[1:]:
        data = row.find_all('td')
        tipo = data[0].text
        nombre = data[1].text
        if ',' in nombre:
            i_coma = nombre.index(',')
            nombre = nombre[:i_coma]
        direcciones[tipo.strip()].append(nombre.strip())

carga_direcciones()

def cliente():
    with open('CLIENTE.sql', 'w') as file:
        for i in range(500):
            dni_cli = '\''+dni(r.randint(10000000, 99999999))+'\''            
            nombre_cli = r.choice(nombres)
            if nombre_cli != 'NULL':
                nombre_cli = '\''+nombre_cli+'\''
            primer_apellido = r.choice(apellidos)
            if primer_apellido == 'NULL':
                apellidos_cli = 'NULL'
            else:
                segundo_apellido = r.choice(apellidos[:-1])
                apellidos_cli = f'\'{primer_apellido} {segundo_apellido}\''
            tipo_via_dir_cli = r.choice(list(direcciones.keys()))
            nombre_via_dir_cli = '\''+r.choice(direcciones[tipo_via_dir_cli])+'\''
            if tipo_via_dir_cli == 'Plaza':
                portal_dir_cli = '\''+str(r.randint(1, 30))+'\''
            elif tipo_via_dir_cli == 'Calle':
                portal_dir_cli = '\''+str(r.randint(1, 125))+'\''
            else:
                portal_dir_cli = '\''+str(r.randint(1, 280))+'\''
            tipo_via_dir_cli = '\''+tipo_via_dir_cli+'\''
            esc_dir_cli = r.choice(['\'A\'', '\'B\'', '\'C\'', '\'D\'',
                                    '\'E\'', 'NULL'])
            puerta_dir_cli = r.randint(1,50)
            piso_dir_cli = '\''+str((puerta_dir_cli // r.randint(3,8)) + 1)+'\''
            p = r.randint(1,100)
            if p > 75:
                piso_dir_cli = 'NULL'
            puerta_dir_cli = str(puerta_dir_cli)
            row = f'''\ninsert into CLIENTE (dni_cli, nombre_cli, apellidos_cli,
            tipo_via_dir_cli, nombre_via_dir_cli, portal_dir_cli, esc_dir_cli,
            puerta_dir_cli, piso_dir_cli) values ({dni_cli}, {nombre_cli},
            {apellidos_cli}, {tipo_via_dir_cli}, {nombre_via_dir_cli},
            {portal_dir_cli}, {esc_dir_cli}, {puerta_dir_cli}, {piso_dir_cli});\n'''
            file.write(row)
            
#cliente()
            
def empleado():
    with open('EMPLEADO.sql', 'w') as file:
        for i in range(75):
            dni_emp = '\''+dni(r.randint(10000000, 99999999))+'\''
            nombre_emp = '\''+r.choice(nombres[:-1])+'\''
            primer_apellido = r.choice(apellidos[:-1])
            segundo_apellido = r.choice(apellidos)
            if segundo_apellido == 'NULL':
                apellidos_emp = '\''+primer_apellido+'\''
            else:
                apellidos_emp = f'\'{primer_apellido} {segundo_apellido}\''
            anyos_contrato_emp = r.choices(range(1,30), range(30,1,-1))[0]
            edad_emp = ('\''+str(r.choices(range(16+anyos_contrato_emp,60),
                                          range(60,16+anyos_contrato_emp,-1))[0])+'\'')
            anyos_contrato_emp = '\''+str(anyos_contrato_emp)+'\''
            activo_emp = '\''+str(r.choices([1,0], [60,20])[0])+'\''
            row = f'''\ninsert into EMPLEADO (dni_emp, nombre_emp, apellidos_emp, 
            anyos_contrato_emp, edad_emp, activo_emp) values ({dni_emp},
            {nombre_emp}, {apellidos_emp}, {anyos_contrato_emp}, {edad_emp},
            {activo_emp});\n'''     
            file.write(row)
        
#empleado()
            
dnis_empleados = []
            
def sacar_dnis_empleados():
    with open('EMPLEADO.sql', 'r') as file:
        for row in file:
            try:
                dnis_empleados.append(re.findall('\d{8}\w', row)[0])
            except:
                pass

sacar_dnis_empleados()

def cocinero(dni):
    with open('OCUPACIONES.sql', 'a') as file:
        dni_coc = '\''+dni+'\''
        titulacion = '\''+r.choice(['Grado Superior', 'Grado Medio', 'FP'])+'\''
        row = f'''\ninsert into COCINERO (dni_coc, titulacion) values ({dni_coc},
        {titulacion});\n'''
        file.write(row)
        
def dependiente(dni):
    with open('OCUPACIONES.sql', 'a') as file:
        dni_dep = '\''+dni+'\''
        row = f'''\ninsert into DEPENDIENTE (dni_dep) values ({dni_dep});\n'''
        file.write(row)
        
def repartidor(dni):
    with open('OCUPACIONES.sql', 'a') as file:
        dni_rep = '\''+dni+'\''
        row = f'''\ninsert into REPARTIDOR (dni_rep) values ({dni_rep});\n'''
        file.write(row)

def ocupaciones():        
    for i, dni in enumerate(dnis_empleados):
        num = i%5
        if num > 3:
            num = r.choice([0,1,2,3])
        if num == 0 or num == 2:
            cocinero(dni)
        elif num == 1:
            dependiente(dni)
        else:
            repartidor(dni)

#ocupaciones()

dni_deps = []
dni_reps = []
dni_cocs = []

def distribuir_dni():
    with open('OCUPACIONES.sql', 'r') as file:
        for row in file:
            try:
                dni = re.findall('\d{8}\w', row)[0]
                tipo = re.findall('insert into (\w+)', row)[0]
                if tipo == 'DEPENDIENTE':
                    dni_deps.append(dni)
                elif tipo == 'COCINERO':
                    dni_cocs.append(dni)
                else:
                    dni_reps.append(dni)
            except:
                pass

distribuir_dni()
           
idiomas = ['Inglés', 'Francés', 'Italiano', 'Ruso', 'Chino', 'Alemán']
props_idioma = [90, 20, 10, 2, 3, 15]
    
def habla_dep():
    with open('HABLA_DEP.sql', 'w') as file:
        for dni in dni_deps:
            dni_dep = '\''+dni+'\''
            idiomas_dep = r.choices(idiomas, props_idioma,
                                k=r.choices(range(1,5), [90, 65, 45, 25])[0])
            for idioma_dep in idiomas_dep:
                idioma_dep = '\''+idioma_dep+'\''
                row = f'''\ninsert into HABLA_DEP (dni_dep, idioma_dep) values
                ({dni_dep}, {idioma_dep});\n'''
                file.write(row)
 
#habla_dep()
                 
dnis_clientes = []

def sacar_dnis_clientes():
    with open('CLIENTE.sql', 'r') as file:
        for row in file:
            try:
                dnis_clientes.append(re.findall('\d{8}\w', row)[0])
            except:
                pass
            
sacar_dnis_clientes()

def random_date():
    year = r.randint(2010, 2022)
    month = r.randint(1, 12)
    d30 = [4, 6, 9, 11]
    d28 = [2]
    if month in d30:
        day = r.randint(1, 30)
    elif month in d28:
        day = r.randint(1, 28)
    else:
        day = r.randint(1, 31)
    return f'{day}/{month}/{year}'

def random_hour():
    hour = str(r.randint(0, 23))
    minutes = str(r.randint(0, 59))
    return '0'*(2-len(hour))+hour+':'+'0'*(2-len(minutes))+minutes
        
def pedido():
    with open('PEDIDO.sql', 'w') as file:
        fechas = {}
        for dni in dnis_clientes:
            for i in range(r.choices(range(1,45), range(45,1,-1))[0]):
                fecha_ped = random_date()
                if fecha_ped in fechas:
                    fechas[fecha_ped] += 1
                else:
                    fechas[fecha_ped] = 1
                numer = fechas[fecha_ped]
                cod_ped = '\''+('0'*(5-len(str(numer))))+str(numer)+'\''
                fecha_ped = '\''+fecha_ped+'\''
                hora_ped = '\''+random_hour()+'\''
                precio_ped_eu = ('\''+str(r.randint(0,150))+','
                                 +str(r.randint(0,99))+'\'')
                valoracion_ped = '\''+str(r.choices(range(0,10), range(0,10))[0])+'\''
                p = r.randint(0, 100)
                if p > 70:
                    valoracion_ped = 'NULL'
                dni_cli = '\''+dni+'\''
                row = f'''\ninsert into PEDIDO (cod_ped, fecha_ped, hora_ped,
                precio_ped_eu, valoracion_ped, dni_cli) values ({cod_ped}, 
                TO_DATE({fecha_ped}, 'DD/MM/YYYY'), {hora_ped},
                {precio_ped_eu}, {valoracion_ped}, {dni_cli});\n'''
                file.write(row)

#pedido()

permisos = ['AM', 'A1', 'A2', 'A', 'B1', 'B', 'C1', 'C', 'D1', 'D', 'BE',
            'C1E', 'CE', 'D1E', 'DE']
props_permisos = [60, 50, 50, 70, 30, 250, 20, 10, 5, 2, 60, 10, 15, 4, 4]


def permiso_rep():
    with open('PERMISO_REP.sql', 'w') as file:
        for dni in dni_reps:
            dni_rep = '\''+dni+'\''
            permisos_rep = r.choices(permisos, props_permisos,
                                k=r.choices(range(1,10), range(10,1,-1))[0])
            for permiso_rep in permisos_rep:
                permiso_rep = '\''+permiso_rep+'\''
                row = f'''\ninsert into PERMISO_REP (dni_rep, permiso_rep) values
                ({dni_rep}, {permiso_rep});\n'''
                file.write(row)

#permiso_rep()

ingredientes_p = {}
precios_p = {}

def carta():
    url = 'https://www.pizzatuttocarballo.com/nuestra-carta-de-pizzas_fr1806.html'
    respuesta = requests.get(url)
    soup = BeautifulSoup(respuesta.text, 'lxml')
    carta = soup.find('ul', class_='carta-lista')
    for i in carta:
        datos = re.split('\n+|,|y', i.text)[1:-1]
        if datos:
            nombre = datos[0].strip()
            precios = re.findall('(\d+,\d+)€', i.text)
            precios_p[nombre] = precios
            a = datos.pop(0)
            a = datos.pop(0)
            if '(o' in a:
                x = re.findall(r'([\w|\s]+)[(]([\w|\s]+)[)]', a)
                ingredientes_p[nombre] = [x[0][0].lower().strip()]
                ingredientes_p[nombre].append(x[0][1][1:].lower().strip())
            else:
                ingredientes_p[nombre] = [a.lower().strip()]           
            while len(a) > 1:
                a = datos.pop(0)
                if len(a) > 1:
                    if '(o' in a:
                        x = re.findall(r'(\w+)\s*\(o\s([\w|\s]+)\)', a)
                        ingredientes_p[nombre].append(x[0][1].lower().strip())
                        ingredientes_p[nombre].append(x[0][1][1:].lower().strip())
                    else:
                        ingredientes_p[nombre].append(a.lower().strip())
carta()
    
def pizza():
    with open('PIZZA.sql', 'w') as file:
        n = 1
        for pizza, precios in precios_p.items():
            nombre_piz = '\''+pizza[0]+pizza[1:].lower()+'\''
            tamanyos = ['Pequeña', 'Mediana', 'Familiar']
            for i, precio in enumerate(precios):
                cod_piz = '\''+'PI'+('0'*(3-len(str(n))))+str(n)+'\''
                precio_piz_eu = '\''+precio+'\''
                tamanyo_piz = '\''+tamanyos[i]+'\''
                n += 1
                row = f'''\ninsert into PIZZA (cod_piz, nombre_piz, precio_piz_eu,
                tamanyo_piz) values ({cod_piz}, {nombre_piz}, {precio_piz_eu},
                {tamanyo_piz});\n'''
                file.write(row)
                
#pizza()

proveedores = []

def carga_proveedores():
    with open('proveedores.csv', 'r', encoding='utf-8') as csvfile:
        for pro in csvfile:
            if pro.strip()[0] == '"':
                proveedores.append(pro.strip()[1:-1])
            else:
                proveedores.append(pro.strip())
 
carga_proveedores()

prefijos_tlf = []

def posibles_prefijos():
    url = 'https://www.spaindata.com/data/1prefijos.html'
    respuesta = requests.get(url)
    soup = BeautifulSoup(respuesta.text, 'lxml')
    tabla = soup.find_all('table')[1]
    rows = tabla.find_all('tr')
    for row in rows:
        data = row.find_all('td')
        prefijos_tlf.append(data[2].text.strip())

posibles_prefijos()
prefijos_tlf = prefijos_tlf[1:]

letras_nif = list(set('ABCDEFGHJNPQRSUVW'))
carga_letra = list(set('NPQRSW'))
control_nif = dict(zip(list(set('1234567890')), list(set('ABCDEFGHIJ'))))

def random_nif():
    letra = r.choice(letras_nif)
    numeros = str(r.randint(1000000, 9999999))
    suma = 0
    for i in range(len(numeros)):
        if i % 2 == 0:
            suma += int(numeros[i])
        else:
            c = int(numeros[i])*2
            if c >= 10:
                c = (c % 10) + 1
            suma += c
    cod_control = str((10 - int(str(suma)[-1])) % 10)
    if letra in carga_letra:
        cod_control = control_nif[cod_control]
    return letra+numeros+cod_control
        
def proveedor():
    with open('PROVEEDOR.sql', 'w') as file:
        n = 0
        while n < 40:
            pro = proveedores[n]
            if len(pro) < 20:
                nif_prov = '\''+random_nif()+'\''
                nombre_prov = '\''+pro+'\''
                prefijo = r.choice(prefijos_tlf)
                if len(prefijo) == 2:
                    tel = int(prefijo) * 10000000 + r.randint(1000000,9999999)
                else:
                    tel = int(prefijo) * 1000000 + r.randint(100000, 999999)
                tlf_prov = '\''+str(tel)+'\''
                row = f'''\ninsert into PROVEEDOR (nif_prov, nombre_prov, tlf_prov)
                values ({nif_prov}, {nombre_prov}, {tlf_prov});\n'''
                file.write(row)
            n += 1

#proveedor()

def tlf_cliente():
    with open('TLF_CLIENTE.sql', 'w') as file:
        for cliente in dnis_clientes:
            for i in range(r.choices(range(1,5), range(5,1,-1))[0]):
                dni_cli = '\''+cliente+'\''
                tlf_cli = '\''+str(6*(10**8)+r.randint(10**7, (10**8)-1))+'\''
                row = f'''\ninsert into TLF_CLIENTE (dni_cli, tlf_cli) values
                ({dni_cli}, {tlf_cli});\n'''
                file.write(row)

#tlf_cliente()
                
vehiculos = {'motos' : ['Aprilia SXR 50',
                        'Motron Breezy 50',
                        'Peugeot Speedfight 50'],
             'coches' : ['Ford Fiesta',
                         'Opel Corsa',
                         'Renault Twingo'],
             'furgonetas' : ['Opel Combo Life 1.5 TD Edition Plus',
                            'Fiat Doblo Combi SX 1.6 Multijet',
                            'Fiat Fiorino Cargo']}

letras_mat = list(set('BCDFGHJKLMNPRSTVWXYZ'))

def random_date_itv():
    year = r.randint(2023, 2028)
    month = r.randint(1, 12)
    d30 = [4, 6, 9, 11]
    d28 = [2]
    if month in d30:
        day = r.randint(1, 30)
    elif month in d28:
        day = r.randint(1, 28)
    else:
        day = r.randint(1, 31)
    return f'{day}/{month}/{year}'

def vehiculo():
    with open('VEHICULO.sql', 'w') as file:
        for i in range(15):
            n = r.randint(0, 9999)
            letra_1 = r.choice(letras_mat[:10])
            letra_2 = r.choice(letras_mat)
            letra_3 = r.choice(letras_mat)
            matricula_veh = '\''+('0'*(4-len(str(n))))+str(n)+letra_1+letra_2+letra_3+'\''
            tipo = r.choice(['motos', 'coches', 'furgonetas', 'motos'])
            if tipo == 'motos':
                capacidad_veh = '\''+str(8)+'\''
            elif tipo == 'coches':
                capacidad_veh = '\''+str(50)+'\''
            else:
                capacidad_veh = '\''+str(200)+'\''
            modelo_veh = '\''+r.choice(vehiculos[tipo])+'\''
            fecha_itv_veh = '\''+random_date_itv()+'\''
            row = f'''\ninsert into VEHICULO (matricula_veh, capacidad_veh,
            modelo_veh, fecha_itv_veh) values ({matricula_veh}, {capacidad_veh},
            {modelo_veh}, TO_DATE({fecha_itv_veh}, 'DD/MM/YYYY'));\n'''
            file.write(row)
            
#vehiculo()

matriculas = []

def carga_matriculas():
    with open('VEHICULO.sql', 'r') as file:
        for row in file:
            try:
                matriculas.append(re.findall('\d{4}\w{3}', row)[0])
            except:
                pass

carga_matriculas()

def conduce():
    with open('CONDUCE.sql', 'w') as file:
        for i in range(r.randint(len(matriculas)*len(dni_reps)-50,
                                 len(matriculas)*len(dni_reps)+50)):
            dni_rep = '\''+r.choice(dni_reps)+'\''
            matricula_veh = '\''+r.choice(matriculas)+'\''
            row = f'''\ninsert into CONDUCE (dni_rep, matricula_veh) values
            ({dni_rep}, {matricula_veh});\n'''
            file.write(row)

#conduce()

pedidos = []

def carga_pedidos():
    with open('PEDIDO.sql', 'r') as file:
        for row in file.read().split('\n\n'):
            try:
                cod_ped = re.findall(r'\'\d{5}\'', row)
                fecha = re.findall(r'\'\d+/\d+/\d+\'', row)
                pedidos.append((cod_ped[0], fecha[0]))
            except:
                pass

carga_pedidos()

cod_pizzas = []

def carga_pizzas():
    with open('PIZZA.sql', 'r') as file:
        for row in file.read().split('\n\n'):
            try:
                a = re.findall(r'(\'PI\d{3}\'), \'([\w|\s]+)\',', row)
                cod_pizzas.append(a[0])
            except:
                pass

carga_pizzas()

def contenido():
    with open('CONTENIDO.sql', 'w') as file:
        for cod_ped, fecha_ped in pedidos:
            pizzas = r.choices(cod_pizzas,
                                k = r.choices(range(1,5), 
                                              range(5,1,-1))[0])
            for cod_piz, pizza in pizzas:
                cantidad = '\''+str(r.choices(range(1,5), range(5,1,-1))[0])+'\''
                row = f'''\ninsert into CONTENIDO (cod_ped, fecha_ped, cod_piz,
                cantidad) values ({cod_ped}, {fecha_ped}, {cod_piz}, {cantidad});\n'''
                file.write(row)
            
#contenido()

conduce = []

def carga_conduce():
    with open('CONDUCE.sql', 'r') as file:
        for row in file.read().split('\n\n'):
            try:
                dni_rep = re.findall(r'\'\d{8}\w\'', row)
                matricula_veh = re.findall(r'\'\d{4}\w{3}\'', row)
                conduce.append((dni_rep[0], matricula_veh[0]))
            except:
                pass

carga_conduce()
              
def entrega():
    with open('ENTREGA.sql', 'w') as file:
        for cod_ped, fecha_ped in pedidos:
            transportes = r.choices(conduce, k = r.choices([1,2,3],[20,2,1])[0])
            for dni_rep, matricula_veh in transportes:
                hora_entrega = '\''+random_hour()+'\''
                row = f'''\ninsert into ENTREGA (dni_rep, matricula_veh,
                cod_ped, fecha_ped, hora_entrega_ped) values ({dni_rep},
                {matricula_veh}, {cod_ped}, TO_DATE({fecha_ped}, 'DD/MM/YYYY'), 
                {hora_entrega});\n'''
                file.write(row)
                
#entrega()

cods_bebidas = []

def carga_bebida():
    with open('BEBIDA.sql', 'r') as file:
        for row in file:
            try:
                cods_bebidas.append(re.findall(r'\'BE-\d\d\'', row)[0])
            except:
                pass
            
carga_bebida()

def incluye_beb():
    with open('INCLUYE_BEB.sql', 'w') as file:
        for cod_ped, fecha_ped in pedidos:
            bebidas = r.choices(cods_bebidas, k = r.choices(range(1,6), 
                                                            range(6,1,-1))[0])
            p = r.randint(0,100)
            if p < 95:
                for cod_beb in bebidas:
                    cantidad = '\''+str(r.choices(range(1,3), range(3,1,-1))[0])+'\''
                    row = f'''\ninsert into INCLUYE_BEB (cod_ped, fecha_ped,
                    cod_beb, cantidad) values ({cod_ped}, {fecha_ped}, {cod_beb},
                    {cantidad});\n'''
                    file.write(row)
                
#incluye_beb()

nifs_proveedores = []

def carga_proveedores():
    with open('PROVEEDOR.sql', 'r') as file:
        for row in file:
            try:
                nifs_proveedores.append(re.findall(r'\'\w\d{7}\w\'', row)[0])
            except:
                pass

carga_proveedores()

ingredientes = set()
for l in ingredientes_p.values():
    for i in l:
        ingredientes.add(i)
    
ingredientes = list(ingredientes)

def ingrediente():
    with open('INGREDIENTE.sql', 'w') as file:
        d = dict(zip(nifs_proveedores, [1]*len(nifs_proveedores)))
        for i in ingredientes:
            nifs = r.choices(nifs_proveedores, k = r.choices(range(1,4), range(4,1,-1))[0])
            for nif_prov in nifs:
                nif_prov = r.choice(nifs_proveedores)
                cod_ing = ('\''+'IN'+('0'*(3-len(str(d[nif_prov]))))+str(d[nif_prov])+'\'')
                nombre_ing = '\''+i[0].upper()+i[1:]+'\''
                precio_ing_eukg = '\''+str(r.randint(1,3))+','+str(r.randint(0,99))+'\''
                ing_despensa_kg = '\''+str(r.randint(50,150))+','+str(r.randint(0,99))+'\''
                row = f'''\ninsert into INGREDIENTE (nif_prov, cod_ing, nombre_ing,
                precio_ing_eukg, ing_despensa_kg) values ({nif_prov}, {cod_ing},
                {nombre_ing}, {precio_ing_eukg}, {ing_despensa_kg});\n'''
                file.write(row)
                d[nif_prov] += 1

#ingrediente()

ing_prov = {}

def carga_ing_prov():
    with open('export.csv', 'r', encoding='Cp1252') as csvreader:
        reader = csv.reader(csvreader, delimiter=',')
        next(reader)
        for line in reader:
            line = line[0].split(',')
            nif_prov = '\''+line[0]+'\''
            cod_ing = '\''+line[1][1:-1]+'\''
            nombre_ing = line[2][1:-1]
            if nombre_ing not in ing_prov:   
                ing_prov[nombre_ing] = [(cod_ing, nif_prov)]
            else:
                ing_prov[nombre_ing].append((cod_ing, nif_prov))
            
carga_ing_prov()

def lleva():
    with open('LLEVA.sql', 'w') as file:
        for cod_piz, nombre_piz in cod_pizzas:
            for nombre_ing in ingredientes_p[nombre_piz.upper()]:
                if nombre_ing == 'orégano.':
                    nombre_ing = 'orégano'
                elif nombre_ing == 'oregano':
                    nombre_ing = 'orégano'
                elif nombre_ing == 'orégano (cerrada)':
                    nombre_ing = 'orégano'
                for cod_ing, nif_prov in ing_prov[nombre_ing[0].upper()+nombre_ing[1:]]:
                    row = f'''\ninsert into LLEVA (cod_piz, cod_ing, nif_prov)
                    values ({cod_piz}, {cod_ing}, {nif_prov});\n'''
                    file.write(row)

#lleva()

def suministro():
    with open('SUMINISTRO.sql', 'w') as file:
        for ingrediente in ing_prov.values():
            for cod_ing, nif_prov in ingrediente:
                for i in range(r.choices(range(3,15), range(15,3,-1))[0]):
                    dia_sum = '\''+random_date()+'\''
                    hora = r.randint(0,23)
                    horas = '0'*(2-len(str(hora)))+str(hora)
                    minuto = r.randint(0,99)
                    minutos = '0'*(2-len(str(minuto)))+str(minuto)
                    hora_sum = '\''+horas+':'+minutos+'\''
                    cantidad_sum_kg = '\''+str(r.randint(10,50))+','+str(r.randint(0,99))+'\''
                    dni_dep = r.choice(dni_deps)
                    row = f'''\ninsert into SUMINISTRO (nif_prov, cod_ing,
                    dia_sum, hora_sum, cantidad_sum_kg, dni_dep) values
                    ({nif_prov}, {cod_ing}, TO_DATE({dia_sum}, 'DD/MM/YYYY'),
                    {hora_sum}, {cantidad_sum_kg}, '{dni_dep}');\n'''
                    file.write(row)
                    
#suministro()

def transporte():
    with open('TRANSPORTE.sql', 'w') as file:
        for dni_rep, matricula_veh in conduce:
            for i in range(r.randint(1,30)):
                dia_trans = '\''+random_date()+'\''
                hora_salida_trans = random_hour()
                dif = r.randint(5,45)
                minutos = int(hora_salida_trans[-2:]) + dif
                if minutos > 59:
                    minutos -= 60
                    hora = int(hora_salida_trans[:2]) + 1
                    if hora == 24:
                        hora = 0
                else:
                    hora = int(hora_salida_trans[:2])
                hora = str(hora)
                minutos = str(minutos)
                hora_llegada_trans = '0'*(2-len(hora))+hora+':'+'0'*(2-len(minutos))+minutos
                distancia_trans_km = str(round((1/3)*dif*(r.randint(10,15)/10), 2))
                row = f'''\ninsert into TRANSPORTE (dni_rep, matricula_veh,
                dia_trans, hora_salida_trans, hora_llegada_trans,
                distancia_trans_km) values ({dni_rep}, {matricula_veh},
                TO_DATE({dia_trans}, 'DD/MM/YYYY'), '{hora_salida_trans}',
                '{hora_llegada_trans}', {distancia_trans_km});\n'''
                file.write(row)
                
#transporte()

def tiene_mem():
    with open('TIENE_MEM.sql', 'w') as file:
        for i in range(r.randint(40, 80)):
            dni_cli = r.choice(dnis_clientes)
            nombre_mem = r.choice(['Oro', 'Plata', 'Bronce'])
            row = f'''\ninsert into TIENE_MEM (dni_cli, nombre_mem) values
            ('{dni_cli}', '{nombre_mem}');\n'''
            file.write(row)

#tiene_mem()

tiene_mem = []

def carga_tiene_mem():
    with open('TIENE_MEM.sql', 'r') as file:
        for row in file.read().split('\n\n'):
            try:
                x = re.findall(r'\'\w+\'', row)
                tiene_mem.append((x[0], x[1]))
            except:
                pass

carga_tiene_mem()

meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
         'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

def meses_mem():
    with open('MESES_MEM.sql', 'w') as file:
        for dni_cli, nombre_mem in tiene_mem:
            for i in range(r.randint(1,20)):
                mes_mem = r.choice(meses)
                anyo_mem = str(r.randint(2010,2022))
                row = f'''\ninsert into MESES_MEM (dni_cli, nombre_mem,
                mes_mem, anyo_mem) values ({dni_cli}, {nombre_mem},
                '{mes_mem}', '{anyo_mem}');\n'''
                file.write(row)
           
#meses_mem()

            
                       
                    



        