try:
    import numpy as np
except:
    raise Exception("Porfavor instale numpy")

import math as m
try:
    import matplotlib.pyplot as pl
except:
    raise Exception("Porfavor instale matplotlib")
try:
    import tqdm
except:
    raise Exception("Porfavor instale tqdm")
try:
    import time
except:
    raise Exception("Porfavor instale time")


class Planta:
    def __init__(self,_dh,_rrr,_w):
        """
        inicializa el objeto que va a resolver el problema
        :param _dh: int
        :param _rrr: int
        """
        self._largo=4000 #dado que el largo es fijo en el problema no le pido al usuario ingresarlo
        self._altura=2000
        self._dh=_dh
        self._h=int(float(self._altura)/_dh) #transformo el largo y ancho a coordenadas
        self._l=int(float(self._largo)/_dh)
        self._grilla=np.zeros((self._h,self._l)) #creo la grilla que se va a utilizar para las iteraciones
        self._matriz=np.zeros((self._h,self._l)) #creo matriz que se va a mostrar
        self._rrr=_rrr*(10**(-3)) #ingreso el digito verificador a decimales
        self._pos_ini_planta = int((1200 + 400 * self._rrr) / self._dh)  # posicion de inicio de la planta
        self._pos_fin_planta = self._pos_ini_planta + int(120 / self._dh)
        self._bordesterreno=[] #memoria para los bordes del terreno
        self._optimo=False
        if _w==-1:
            self._w=4/(2+(4-(m.cos(m.pi/(self._l-1))+m.cos(m.pi/(self._h-1)))**2)**0.5)
            self._optimo=True
        else:
            self._w=_w
        self._terreno=False
    def verificar(self):
        """
        true si esta todo ok! para resolver el problema
        :return: boolean
        """
        if self._dh>2000:
            return False
        if not self._optimo:
            if not (0<self._w<=2):
                return False
        return True
    def __cbmar(self,t):
        """
        funcion privada que establece las condiciones de borde para el mar
        :param t: int
        :return: int
        """
        if t<=8 and t>=0:
            return 4
        if t>8 and t<=16:
            return 2*t-12
        if t>16 and t<=24:
            return -2*t+52
    def __cbterreno(self,posy):
        """
        Funcion privada que establece las condiciones de borde para el terreno
        :param posy: int
        :return: int
        """
        #notemos por nuestro sistema de referencia que nos interesa cuando la posy es mayor a 200 mts a escala
        alt=200/self._dh #sacamos la coordenada y
        if posy<alt:
            return 0
        else:
            return 20
    def __cbplanta(self,t):
        """
        Establece las condiciones de borde para la planta en un t inicial dado
        :param t: int
        :return:float
        """
        return  450*(m.cos(m.pi*t/12)+2)
    def __cbatmosfera(self,y,t):
        """
        crea las condiciones de borde para la atmosfera, con y la altura en ese punto
        :param t:int
        :return: int
        """
        return int(-6*y/1000)+self.__cbmar(t)
    def __xdes(self,posx):
        """
        funcion interna del programa para corregir los ejes de las rectas al generar terreno
        :param posx: it
        :return: int
        """
        return posx-self._pos_fin_planta
    def crearTerreno(self):
        """
        Crea el terreno segun los datos de geografia pedidos
        :return: void
        """
        #en general, lo hice graficando rectas desde el origen (pos_fin_planta,0)
        #una complicacion fue medir desde un nuevo eje de referencia el terreno, dado que TODO tuvo que ser desplazado
        #para eso se tienen que correr las coordenadas por el nuevo eje coordenado
        #entonces en todas las iteraciones voy a tener ejes corregidos para hacer que funcione
        #primero iteramos desde la planta en el primer tramo
        m1=100/300  #creamos la pendiente, notemos que la recta que describe esto es y=m*x
        pos_fin1=self._pos_fin_planta+int(400/self._dh) #creo la hasta que x va a generar esta parte del terreno
        for x in range(self._pos_fin_planta,pos_fin1): #empezamos para todos los x en el primer tramo
            x_d=self.__xdes(x) #desplazo su posicion para que coincidan los ejes
            h_max=self._h-1-int(x_d*m1) #creo la variable y medida desde el final de la grilla
            for y in range(h_max,self._h): #para cada y desde la altura maxima hasta el final
                self._grilla[y][x]=np.nan #son todos NAN

        #veamos ahora el segundo tramo
        #primero, definimos hasta donde llega el segundo tramo:
        pos_fin2=pos_fin1+int(800/self._dh)
        altura2=1500+200*self._rrr #alturas maxima del primer tramo, es la altura final
        posa2=altura2/self._dh #la transformo a coordenadas
        m2=(posa2-pos_fin1*m1)/(pos_fin2-pos_fin1) #creo la pendiente de la ecuacion de las mayores y
        pos_fin1_des=self.__xdes(pos_fin1) #del primer tramo desplazo los ejes de su posicion final
        n2=pos_fin1_des*m1-pos_fin1_des*m2 #creo su coeficionte de posicion a partir de la condicion de continuidad del terreno
        for x in range(pos_fin1,pos_fin2): #iteramos...
            x_d=self.__xdes(x) #muevo el eje para generar la recta
            h_max=self._h-1-int(x_d*m2+n2) #genero desde que y a partir de la ecuacion de la recta encontrada
            for y in range(h_max,self._h): #iteramos para y
                self._grilla[y][x]=np.nan #todos son NAN


        #ahora vemos que pasa en el tercer tramo
        pos_fin3=pos_fin2+int(300/self._dh) #posicion final del tercer tramo a partir del segundo
        altura3 = 1300 + 200 * self._rrr
        posa3=altura3/self._dh
        m3=(posa2-posa3)/(pos_fin2-pos_fin3) #creo la pendiente de esta curva
        #sacamos n3 usando la continuidad de la recta
        pos_fin2_des=self.__xdes(pos_fin2) #desplazamos la posicion final del tramo anterior
        n3=m2*pos_fin2_des+n2-m3*pos_fin2_des #sacamos el n de la ecuacion de la recta por la continuidad
        for x in range(pos_fin2,pos_fin3): #iteramos...
            x_d=self.__xdes(x) #desplazo el x
            h_max=self._h-1-int(x_d*m3+n3) #genero la altura maximo
            for y in range(h_max,self._h): #itero el y..
                self._grilla[y][x]=np.nan #son todos NAN
        pos_fin4=pos_fin2+int(500/self._dh) #posicion final del cuarto tramo a partir del tercero
        altura4=1850+100*self._rrr
        posa4=altura4/self._dh #pasamos la altura a coordenadas
        m4=(posa3-posa4)/(pos_fin3-pos_fin4) #creamos la pendiente del tramo
        pos_fin3_des=self.__xdes(pos_fin3) #desplazamos la posicion final del tramo anterior
        n4=m3*pos_fin3_des+n3-m4*pos_fin3_des #genero para el cuarto tramo el n de la ecuacion de la recta
        for x in range(pos_fin3,pos_fin4): #iteramos
            x_d=self.__xdes(x) #desplazo el eje x
            h_max=self._h-1-int(x_d*m4+n4) #creo la altura maxima
            for y in range(h_max,self._h): #itero para y
                self._grilla[y][x]=np.nan #son todos NAN
        #para el ultimo tramo, hare que baje perpendicularmente hasta el final
        #para ello usare la condicion de perpendicularidad de las rectas
        #m1*m2 =-1, entonces:
        m5=-1/m4
        pos_fin4_des=self.__xdes(pos_fin4) #desplazamos los ejes x
        n5=m4*pos_fin4_des+n4-pos_fin4_des*m5  #usamos la continuidad para determinar el n
        y_ultimo=0
        for x in range(pos_fin4,self._l): #iteramos...
            x_d=self.__xdes(x)
            h_max=self._h-1-int(x_d*m5+n5)
            for y in range(h_max,self._h):
                self._grilla[y][x]=np.nan
        self._terreno=True
        self._matriz=self._grilla #se modifica despues la matriz para que sea la misma que la grilla
    def __nearnan(self,x,y):
        """
        True si en las coordenadas cercanas a (x,y) hay un NAN (None).
        :param x: int
        :param y: int
        :return: bool
        """
        #borde de arriba+esquinas
        if y==0:
            abajo=np.isnan(self._grilla[y+1][x])
            #veo los casos de las orillas
            if x==0:
                der= np.isnan(self._grilla[y][x+1])
                return abajo or der
            if x==self._l-1:
                izq= np.isnan(self._grilla[y][x-1])
                return abajo or izq
            else:
                izq= np.isnan(self._grilla[y][x-1])
                der= np.isnan(self._grilla[y][x+1])
                return abajo or izq or der
        #borde de abajo+ esquinas
        if y==self._h-1:
            arriba= np.isnan(self._grilla[y-1][x])
            if x==0:
                der= np.isnan(self._grilla[y][x+1])
                return arriba or der
            if x==self._l-1:
                izq= np.isnan(self._grilla[y][x-1])
                return arriba or izq
            else:
                izq= np.isnan(self._grilla[y][x-1])
                der= np.isnan(self._grilla[y][x+1])
                return arriba or izq or der
        #borde de la izquierda sin esquinas

        if x==0:
            arriba= np.isnan(self._grilla[y-1][x])
            abajo= np.isnan(self._grilla[y+1][x])
            der= np.isnan(self._grilla[y][x+1])
            return arriba or abajo or der
        #borde de la derecha sin esquinas
        if x==self._l-1:
            arriba= np.isnan(self._grilla[y-1][x])
            abajo= np.isnan(self._grilla[y+1][x])
            izq= np.isnan(self._grilla[y][x-1])
            return arriba or abajo or izq
        #caso general
        else:
            arriba= np.isnan(self._grilla[y-1][x])
            izq= np.isnan(self._grilla[y][x-1])
            abajo= np.isnan(self._grilla[y+1][x])
            der= np.isnan(self._grilla[y][x+1])
            return arriba or izq or abajo or der
    def __getbordeterreno(self):
        """
        ve que es borde del terreno y lo agnade a la lista de bordes, luego alfinal la ordena
        :return:
        """
        if not self._terreno:
            print("[Error]: No existe terreno")
        else:
            for x in range(self._pos_fin_planta+1,self._l):
                for y in range(self._h):
                    #veo si donde estoy parado es un terreno
                    es_terreno=not np.isnan(self._grilla[y][x])
                    if es_terreno: #si estoy parado en un terreno
                        #veo si hay un NAN cerca
                        NAN=self.__nearnan(x,y)
                        if NAN: #si lo hay
                            self._bordesterreno.append((x,y)) #agnado su coordenada a la lista
            self._bordesterreno.sort()
    def __whereNAN(self,x,y):
        """
        Indica donde hay un NAN cerca de (x,y) en la grilla.
        Retorna una lista de strings de donde estan.
        :param x: int
        :param y: int
        :return: list
        """
        #creo lista a devolver con las posiciones
        a=[]
        #si estoy en un borde derecho
        if x==self._l-1:
            #si estoy la esquina derecha
            if y==0:
                izq=np.isnan(self._grilla[y][x-1])
                abajo=np.isnan(self._grilla[y+1][x])
                if abajo:
                    a.append("abajo")
                if izq:
                    a.append("izquierda")
            elif y==self._h-1:
                arriba= np.isnan(self._grilla[y-1][x])
                izq= np.isnan(self._grilla[y][x-1])
                if arriba:
                    a.append("arriba")
                if izq:
                    a.append("izquierda")
            else:
                arriba= np.isnan(self._grilla[y-1][x])
                izq= np.isnan(self._grilla[y][x-1])
                abajo= np.isnan(self._grilla[y+1][x])
                if arriba:
                    a.append("arriba")
                if izq:
                    a.append("izquierda")
                if abajo:
                    a.append("abajo")
        #si estoy en el borde izquierdo
        elif x==0:
            if y==0:
                der= np.isnan(self._grilla[y][x+1])
                abajo= np.isnan(self._grilla[y+1][x])
                if der:
                    a.append("derecha")
                if abajo:
                    a.append("abajo")
            elif y==self._h-1:
                arriba= np.isnan(self._grilla[y-1][x])
                der= np.isnan(self._grilla[y][x+1])
                if arriba:
                    a.append("arriba")
                if der:
                    a.append("derecha")
        #si estoy en el borde de arriba
        elif y==0:
            izq= np.isnan(self._grilla[y][x-1])
            abajo= np.isnan(self._grilla[y+1][x])
            der= np.isnan(self._grilla[y][x+1])
            if izq:
                a.append("izquierda")
            if abajo:
                a.append("abajo")
            if der:
                a.append("derecha")
        #si estoy en el borde de abajo
        elif y==self._h-1:
            arriba= np.isnan(self._grilla[y-1][x])
            izq= np.isnan(self._grilla[y][x-1])
            der= np.isnan(self._grilla[y][x+1])
            if arriba:
                a.append("arriba")
            if izq:
                a.append("izquierda")
            if der:
                a.append("derecha")
        #caso general:
        else:
            arriba=np.isnan(self._grilla[y-1][x])
            izq=np.isnan(self._grilla[y][x-1])
            abajo=np.isnan(self._grilla[y+1][x])
            der=np.isnan(self._grilla[y][x+1])
            if arriba:
                a.append("arriba")
            if izq:
                a.append("izquierda")
            if abajo:
                a.append("abajo")
            if der:
                a.append("derecha")
        return a
    def cb(self,t):
        """
        Establece las condiciones de borde del problema iniciales para un tiempo dado.
        :param t: int
        :return: void
        """
        #partamos por los bordes de la matriz
        #primero el mar.
        for x in range(self._pos_ini_planta):
            self._grilla[self._h-1][x]=self.__cbmar(t)
        #luego las montagnas
        self.__getbordeterreno()
        for (x,y) in self._bordesterreno:
            self._grilla[y][x]=self.__cbterreno(y)
        #ahora la planta,notemos que la planta es borde de la montagna pero aca
        #dominara la planta por sobre la montagna
        for x in range(self._pos_ini_planta,self._pos_fin_planta):
            self._grilla[self._h-1][x]=self.__cbplanta(t)
        #por ultimo, utilizamos la condicion de borde sobre la atmosfera
        for x in range(self._l):
            for y in range(self._h-1):
                a=self.__whereNAN(x,y)
                if "abajo" in a:
                    break
                else:
                    self._grilla[y][x]=self.__cbatmosfera(self._h-y,t)
        #ahora usamos que:
        self._matriz=self._grilla
    def __relajacion_sucesiva(self,x,y,epsilon,rho):
        """
        Aplica el metodo de relajacion sucesiva devolviendo el valor de la matriz en ese punto
        y el cambio producido en esa iteracion con respecto a lo anterior.
        :param x: int
        :param y: int
        :param epsilon: float
        :param rho: function
        :return: (num,float)
        """
        #notacion x1=x+1 e 1x=x-1, por que para los bordes vamos a tener problemas.
        #partimos con todos estos valores en infinito
        u_i1_j=np.inf
        u_1i_j=np.inf
        u_i_j1=np.inf
        u_i_1j=np.inf
        nearNAN=self.__nearnan(x,y) #veo si existe un nan cerca
        if nearNAN:
            arreglo=self.__whereNAN(x,y) #veo en donde se ubican esos nan
            if "arriba" in arreglo:
                u_i_j1=self._grilla[y+1][x] #luego establesco el valor opuesto de la matriz!
            if "izquierda" in arreglo:
                u_1i_j=self._grilla[y][x+1]
            if "abajo" in arreglo:
                u_i_1j=self._grilla[y-1][x]
            if "derecha" in arreglo:
                u_i1_j=self._grilla[y][x-1]
        #luego veo si queda alguien como infinito, si lo es, le doy su valor normal.
        if  np.isinf(u_i1_j):
            u_i1_j=self._grilla[y][x+1]
        if np.isinf(u_1i_j):
            u_1i_j=self._grilla[y][x-1]
        if np.isinf(u_i_j1):
            u_i_j1=self._grilla[y-1][x]
        if np.isinf(u_i_1j):
            u_i_1j=self._grilla[y+1][x]
        if rho==0: #si la funcion es 0, uso relajacion sucesiva para Laplace
            r = self._w * (u_i1_j + u_1i_j + u_i_j1 + u_i_1j - 4 * self._grilla[y][x]) / 4
        else: #sino, uso relajacion sucesiva para Poisson
            xmetros=x*self._dh
            ymetros=self._altura-y*self._dh
            r=self._w * ( u_i1_j + u_1i_j + u_i_j1 + u_i_1j - 4*self._grilla[y][x] - (self._dh**2) * rho (xmetros,ymetros) ) / 4
        n=self._matriz[y][x]+r
        e=abs(r) #veo su cambio
        if e<epsilon: #si es menor a la tolerancia
            epsilon=e #le doy un  nuevo valor
        return (n,epsilon)
    def itera(self,tolerancia,rho,n_iteraciones=1000):
        e=1 #definimos primero, un epsilon alto para que entre al bucle
        iteracion=0 #genero un contador para las iteraciones
        while e>tolerancia and iteracion<=n_iteraciones:
            for x in range(1,self._l-1):
                for y in range(1,self._h-1):
                   if np.isnan(self._grilla[y][x]):
                       break
                   else:
                       (self._matriz[y][x],e)=self.__relajacion_sucesiva(x,y,e,rho)
            iteracion+=1
            self._grilla=self._matriz #se actualiza la matriz de valores anteriores fijo

    def plot(self):
        """
        Grafica
        :return: None
        """
        fig = pl.figure()
        ax = fig.add_subplot(111)
        # Se agrega grafico al plot
        cax = ax.imshow(self._matriz, interpolation='nearest')
        fig.colorbar(cax)
        pl.show()
    def solve(self,t,epsilon,iteraciones_max,g):
        """
        Junta todas las funciones para generar solucion al problema planteado
        :param t:
        :param epsilon:
        :param n_iteraciones:
        :param g: 0 o f
        :return:
        """
        self.crearTerreno()
        self.cb(t)
        self.itera(epsilon, g, iteraciones_max)
        self.plot()
def f(x,y):#x,y en metros asi que ojo!
    """
    :param x: medida en metros de la coordenada x
    :param y: medida en metros de la coordenada y
    :return: valor de la funcion rho mostrada en el enunciado
    """
    return 1/((x**2+y**2+120)**0.5)
def test():
    p=Planta(25,692,-1)
    p.solve(20,0.001,1000,0)
#test()
#era para hacer un test del metodo






