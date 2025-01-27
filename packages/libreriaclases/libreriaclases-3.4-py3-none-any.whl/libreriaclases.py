import numpy as np
import pandas as pd
from scipy.stats import kstest
import sys
import time
from IPython.display import display

class DataAnalysis():
    def __init__(self, ruta, sep=','):
        self.ruta = ruta
        self.media = []
        self.mediana = []
        self.moda = []
        self.borrar = []
        self.bfil = []
        self.dataset=0
        self.var1=0.3
        self.var2=0.05
        self.sep=sep
    def info():
        print('This are the steps to be followed to do the datasets cleaning\n\n')
        # print('Estos son tus pasos a seguir para hacer tu limpieza de dataset:\n\n')
        time.sleep(1)
        print('1.Introduce the route in the class --> ex: Variable = library.DataAnalysis(path)\n\n')
        # print('1. Introduce tu ruta en la clase. --> ex:  Variable = libreria.DataAnalisis(ruta)\n\n')
        print('2. Write your data with pandas')
        # print('2. Lee tus datos con pandas')
        print('   - CSV: use the function Variable.csv()')
        print('   - Excel: use the function Variale.excel()\n')
        # print('   - CSV: usa la función Variable.csv()')
        # print('   - Excel: usa la función Variable.excel()\n')
        time.sleep(2)
        print('3. Start the cleaning of the dataset using the method Variable.analyse()\n')
        # print('3. Inicia la limpieza del dataset usando el método Variable.analizar()\n')
        time.sleep(1)
        # print('4. Para visualizar el dataframe usa la funcion Variable.visualizar()\n')
        print('4. Visualize the dataframe using the function Variable.visualize()\n')
        time.sleep(1)
        print('5. Save the dataframe using Variable.save()')
        # print('5. Para guardar el dataframe usa Variable.guardar()')
    def limpieza(self):
        for i in self.borrar:
            self.dataset.drop(columns = [i],inplace=True, axis=1)
        for i in self.media:
            self.dataset.fillna({i:self.dataset[i].mean()}, inplace=True)
        for i in self.moda:
            self.dataset.fillna({i:self.dataset[i].mode().iloc[0]}, inplace=True)
        for i in self.mediana:
            self.dataset.fillna({i:self.dataset[i].median()}, inplace=True)
        for i in self.bfil:
            self.dataset.fillna({i:self.dataset[i].bfill()}, inplace=True)
            self.dataset.fillna({i:self.dataset[i].ffill()}, inplace=True)
            self.dataset.fillna({i:self.dataset[i].mode().iloc[0]}, inplace=True)
        # print('La limpieza se ha realizado correctamente\n\n')  
        print('The cleaning has been done correctly.\n\n')  
    def excel(self):
        try:
            self.dataset = pd.read_excel(self.ruta)
            print('The file has been saved correctly.')
            # print("El archivo se ha cargado correctamente.")
        except FileNotFoundError:
            print(f"Error: The file with the route '{self.ruta}' has not been found.")
            # print(f"Error: El archivo con la ruta '{self.ruta}' no se ha encontrado.")
            sys.exit()
        except Exception as e:
            print('Unexpected error.')
            # print("Error inesperado")
            sys.exit()
    def personalizado(self):
        self.media = []
        self.mediana = []
        self.moda = []
        self.borrar = []
        self.bfil = []
        for i in self.dataset.columns:
            porcentaje=(self.dataset[i].isna().mean())
            if self.dataset[i].dtype == 'int64' or self.dataset[i].dtype == 'float64':
                stat, p_value = kstest(self.dataset[i], 'norm', args=(self.dataset[i].mean(), self.dataset[i].std())) 
                if p_value > self.var2: 
                    if np.abs(self.dataset[i].skew())>1:
                        print(f'\The column {i} is numeric and has a skewed distribution and a empty 'f'data percentaje of {porcentaje}%. ¿What would you like to do with it?\n')
                        # print(f'\nLa columna {i} es numérica y tiene una distribución sesgada y un porcentaje de datos ' 
                        # f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                        
                    else:
                        print(f'\nThe column {i} is numeric and has a normal distribution and a 'f'empty data percentage of {porcentaje}%. ¿What would you like to do with it?')
                        # print(f'\nLa columna {i} es numérica y tiene una distribución normal y un porcentaje de datos ' 
                        # f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                    
                else:
                    print(f'\nThe column {i} is numeric and has either a normal distribution nor a skewed distribution, it has an 'f'empty data percentage of {porcentaje}%. ¿Qué te gustaría hacer con ella?') 
                    # print(f'\nLa columna {i} es numérica y no tiene distribución normal ni sesgada, tiene un porcentaje de datos ' 
                    #         f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                respuesta = input('0:Drop it\n1:Mode\n2:Median\n3:Mean\n4:Fill it with the surrounding ones')
                # respuesta=input('0:Borrarla\n1:Moda\n2:Mediana\n3:Media\n4:Rellenarlo con los de alrededor\n' )
                if int(respuesta)not in [0,1,2,3,4]:
                    print('The answer is not possible. Answer correctly.')
                    # print('La respuesta no es posible. Responda una respuesta correcta.')
                    respuesta = input('0:Drop it \n1:Mode \n2:Median \n3:Mean \n4:Fill it with the surrounding ones')
                    # respuesta=input('0:Borrarla\n1:Moda\n2:Mediana\n3:Media\n4:Rellenarlo con los de alrededor\n' )
                if int(respuesta)==0:
                    self.borrar.append(i)
                elif int(respuesta)==1:
                    self.moda.append(i)
                elif int(respuesta)==2:
                    self.mediana.append(i)
                elif int(respuesta)==3:
                    self.media.append(i)
                elif int(respuesta)==4:
                    self.bfil.append(i)
                else:
                    sys.exit('ERROR: Not possible answer.')
                    # sys.exit("ERROR: Respuesta no posible")
                    
            else:
                print(f'\The column {i} is categorical and has an empty 'f'data percentaje of {porcentaje}%. ¿What would you like to do with it?')
                # print(f'\nLa columna {i} es categórica y tiene un porcentaje de datos' 
                #         f'vacíos del {porcentaje}%. ¿Qué te gustaría hacer con ella?\n')
                respuesta = input('0:Drop it \n1:Mode \n2:Fill it with the surrounding ones')
                # respuesta=input('0:Borrarla\n1:Moda\n2:Rellenarlo con los de alrededor\n' )
                if int(respuesta)!=0 and int(respuesta)!=1 and int(respuesta)!=2:
                    print('The answer is not possible. Answer correctly.')
                    # print('La respuesta no es posible. Responda una respuesta correcta.')
                    respuesta = input('0:Drop it \n1:Mode \n2:Fill it with the surrounding ones')
                    # respuesta=input('0:Borrarla\n1:Moda\n2:Rellenarlo con los de alrededor\n' )
                if int(respuesta)==0:
                    self.borrar.append(i)
                elif int(respuesta)==1:
                    self.moda.append(i)
                elif int(respuesta)==2:
                    self.bfil.append(i)
                else:
                    sys.exit('ERROR: The anwer is not possible.')
                    # sys.exit("ERROR: Respuesta no posible")
        print('Starting cleaning...\n')
        # print('Iniciando limpieza...\n')
        self.limpieza()

    def csv(self):
        try:
            self.dataset = pd.read_csv(self.ruta, sep=self.sep)
            print('The file has loaded correctly.')
            # print("El archivo se ha cargado correctamente.")
        except FileNotFoundError:
            print(f"Error: The file with the route '{self.ruta}' has not be found.")
            # print(f"Error: El archivo con la ruta '{self.ruta}' no se ha encontrado.")
            sys.exit()
        except Exception as e:
            print('Unexpected error.')
            # print("Error inesperado")
            sys.exit()
    def analyze(self):
        try:
            with open('values.txt', 'r') as file:
                for linea in file:
                    palabras = linea.strip().split(',')
                    if len(palabras)>=2:
                        try:
                            self.var1=float(palabras[0])
                            self.var2=float(palabras[1])
                            break
                        except ValueError:
                            pass
        except FileNotFoundError:
            pass
        self.dataset=pd.DataFrame(self.dataset)
        for i in self.dataset.columns:
            if ((self.dataset[i].isna().mean()))>self.var1:
                self.borrar.append(i)
            elif self.dataset[i].dtype == 'int64' or self.dataset[i].dtype == 'float64':
                stat, p_value = kstest(self.dataset[i], 'norm', args=(self.dataset[i].mean(), self.dataset[i].std())) 
                if p_value > self.var2: 
                    if np.abs(self.dataset[i].skew())>1:
                        self.mediana.append(i)
                    else:
                        self.media.append(i)
                else:
                    self.bfil.append(i)
                
            else:
                self.moda.append(i)
        print('The DataFrame has been analized and it is recommended to do the following imputations: \n')
        # print('Tu DataFrame ha sido analizado y se recomienda hacer la siguiente imputación:\n')
        if self.borrar:
            print(f'Drop the columns{self.borrar}\n')
            # print(f'Borrar las columnas {self.media}\n')
        if self.media:
            print(f'Fill the columns {self.media} with the mean\n')
            # print(f'Rellenas las columnas {self.media} con la media\n')
        if self.mediana:
            print(f'Fill the columns {self.mediana} with the median\n')
            # print(f'Rellenas las columnas {self.mediana} con la mediana\n')
        if self.bfil:
            print(f'Fill the columns {self.bfil} with the surronding data\n')
            # print(f'Rellenas las columnas {self.bfil} con los datos de alrededor\n')
        if self.moda:
            print(f'Fill the columns {self.moda} with the mode\n')
            # print(f'Rellenas las columnas {self.moda} con la moda\n')
        respuesta = input('If you want to follow the recommendations write -->yes<--, if you do NOT want to follow the recommendations write -->no<--\n')
        # respuesta=input('Si desea seguir las recomendaciones escriba -->si<--, si NO desea seguir las recomendaciones escriba -->no<--\n')
        if respuesta=='yes':
            print('Starting the recommended cleaning...\n')
            # print('Iniciando limpieza recomendada...\n')  
            self.limpieza()
        elif respuesta=='no':
            print('Starting personalized cleaning...\n')
            # print('Iniciando limpieza personalizada...\n')
            self.personalizado()
        else:
            print('ERROR: incorrect answer.\n\n')
            # print('ERROR: respuesta incorrecta\n\n')
    def visualize(self):
        if isinstance(self.dataset, pd.DataFrame):
            display(self.dataset)
        else:
            print('The dataset has not been uploaded.')
            # print('No se ha cargado el dataset')
    def save(self):
        try:
            self.dataset.to_csv('corrected_'+self.ruta.split('\\')[-1])
            print('It has been saved correctly.')
            # print('Se ha guardado correctamente.')
        except Exception as e:
            print('There has been an error: %s',e)
            # print('Ha habido un error: %s',e)



    

   
