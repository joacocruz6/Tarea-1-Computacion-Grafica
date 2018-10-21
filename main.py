#CORRER ESTE ARCHIVO
from Planta import *
def resolver(miPlanta,t,eps,n_iteraciones,g):
    assert 0<=t<=24
    miPlanta.solve(t,eps,n_iteraciones,g)
#main: none->none
#hace el programa correr, si no ingresa algun numero como lo pedido falla
def main():
    r=input("Ingrese su digito verificador: ")
    dt=input("Ingrese su paso de discretizacion: ")
    w1=input("Ingrese su coeficiente de relajacion, -1 si quiere utilizar el optimo: ")

    p=Planta(int(dt),int(r),int(w1))
    ok=p.verificar()
    assert ok
    tolerancia=input("Ingrese la tolerancia para el metodo numerico: "); ep=float(tolerancia)
    tiempo=input("Ingrese en que tiempo debe estar (en horas): ");t=int(tiempo)
    it=input("Ingrese el numero de las iteraciones a hacer como maximo: "); iteraciones=int(it)
    funcion=input("Ingrese 1 para la funcion dada en poisson o 0 para laplace: "); h=int(funcion)
    assert h==1 or h==0
    if h==0:
        resolver(p,t,ep,iteraciones,0)
    if h==1:
        resolver(p,t,ep,iteraciones,f)


if __name__=="__main__":
    main()