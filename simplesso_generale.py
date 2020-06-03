#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division
from fractions import Fraction
from numpy import *
import funzioni_lineari as f
from IPython.display import display, Markdown, Latex, Math

class Tableau:
    #inizializzazione
    def __init__(self, obj, prob_type):
        self.rows = []
        self.cons = []
        self.nonbasis = []
        self.basis=[]
        self.obj=[]
        self.id=[]
        if prob_type == 'max':
            self.obj =[f.l(x) for x in obj]
        elif prob_type == 'min':
            array=[f.l(x) for x in obj]
            for j in range(len(obj)):
                array[j].cambiosegni()
            for j in range(len(obj)):
                self.obj.append(array[j])

    #funzione aggiunge vincoli
    def aggiungi_vincolo(self, expression, value):
        self.cons.append(f.l(value))
        array=[f.l(x) for x in expression]
        for j in range(len(expression)):
            array[j].cambiosegni()
        self.rows.append(array)

    #crea tableau iniziale
    def crea_primo_tableau(self):
        for i in range(len(self.cons)):
            self.rows[i].insert(0,self.cons[i])
        self.obj = array([f.l([0])]+self.obj)
        
        dim = len(self.rows)
        dim2=len(self.obj)
        for i in range(dim):
            self.basis += ["s_"+str(1+i)]
            
        for i in range(1,dim2):
            self.nonbasis += ["x_"+str(i)]
        self.id = [[f.l(0) for r in range(len(self.basis))] for k in range(len(self.basis))]
        for i in range(len(self.basis)):
            self.id[i][i] = f.l(1)
            
    #pivot data etichetta variabile uscente e entrante
    def pivot(self,row,col):
        r=0
        c=0
        #individuo riga e colonna associato a etichette
        while self.basis[r]!=str(row):
            r+=1
        while self.nonbasis[c]!=str(col):
            c+=1
        c=c+1
        e = self.rows[r][c]
        self.basis[r]=str(col)
        self.nonbasis[c-1]=str(row)
        assert e != 0
        #cambio coefficienti tabella tranne riga e colonna pivot
        for i in range(len(self.rows)):
            for j in range(len(self.obj)):
                if i!=r and j!=c:
                    ogg=self.rows[r][j].prod(self.rows[i][c])
                    ogg=ogg.prodinv(e)
                    ogg=ogg.cambiosegno1()
                    self.rows[i][j]=self.rows[i][j].plus(ogg)
        for j in range(len(self.obj)):
                if j!=c:
                    ogg=self.rows[r][j].prod(self.obj[c])
                    ogg=ogg.prodinv(e)
                    ogg=ogg.cambiosegno1()
                    self.obj[j]=self.obj[j].plus(ogg)
        self.obj[c]=self.obj[c].prodinv(e)
        for i in range(len(self.rows)):
            if i!=r:
                self.rows[i][c]=self.rows[i][c].prodinv(e)
        #cambio riga pivot
        for i in range(len(self.obj)):
            if i!=c:
                self.rows[r][i]=self.rows[r][i].cambiosegno1()
                self.rows[r][i]=self.rows[r][i].prodinv(e)
        self.rows[r][c].inv()

    #verifica ottimalità soluzione di base corrente
    def is_optimal(self):
        b=True
        for i in range(1,len(self.obj)):
            if (self.obj[i]).maggiore(f.l(0)):
                b=False
        return b
    
    #verifica se soluzione di base corrente ammissibile
    def is_feasible(self):
        b=True
        for i in range(len(self.cons)):
            if (self.rows[i][0]).minore(f.l(0)):
                b=False
        return b

    #sceglie variabile entrante migliore
    def _variabile_entrante(self):
        low=f.l(0)
        indice=0
        for i in range(1,len(self.obj)):
            if self.obj[i].maggiore(low):
                indice=i
                low=self.obj[i]
        #print(self.nonbasis[indice-1])
        return(indice)

    #sceglie variabile uscente
    def _variabile_uscente(self,ind_entr):
        vettore=[]
        indice=0
        for i in range(len(self.rows)):
            if self.rows[i][ind_entr].diverso(f.l(0)):
                vettore.append(self.rows[i][0].diviso(self.rows[i][ind_entr]))
            else:
                vettore.append(f.l(0))
        low=f.l(0)
        for j in range(len(vettore)):
            if vettore[j].minore(low):
                low=vettore[j]
        for j in range(len(vettore)):
            if vettore[j].minore(f.l(0)):
                if vettore[j].maggioreug(low):
                    indice=j
                    low=vettore[j]

        #print(self.basis[indice])
        return(indice)

    #fa un pivot 'autonomamente'
    def step(self):
        indice_entrante=self._variabile_entrante()
        indice_uscente=self._variabile_uscente(indice_entrante)
        print('Variabile entrante:'+self.nonbasis[indice_entrante-1]+'\nVariabile uscente:'+self.basis[indice_uscente])
        self.pivot(self.basis[indice_uscente],self.nonbasis[indice_entrante-1])


    def stampa_soluzione_base_corrente(self):
        s='('
        for i in range(len(self.basis)):
            s+=self.basis[i]+','
        for i in range(len(self.nonbasis)-1):
            s+=self.nonbasis[i]+','
        s+=self.nonbasis[-1]+')=('
        for i in range(len(self.basis)):
            s+=self.rows[i][0].stringa()+','
        for i in range(len(self.nonbasis)-1):
            s+='0,'
        s+='0)'
        print('Soluzione di base: '+s)

    #da suggerimento
    def prossimo_step(self):
        self.stampa_soluzione_base_corrente()
        if self.is_feasible():
            if self.is_optimal():
                print("Tale soluzione è ammissibile e ottima -> Fine")
            else:
                print("Tale soluzione è ammissibile ma NON è ottima -> Continua con il simplesso primale")
        else:
            if self.is_optimal():
                print("Tale soluzione NON è ammissibile ma soddisfa le condizioni di ottimalità -> Continua con il simplesso duale")
            else:
                print("Tale soluzione NON è né ammissibile né ottima")

    def _formaintermedia_classico(self):
        matrice=[['0' for i in range(len(self.nonbasis)+2)] for j in range(len(self.basis)+2)]
        matrice[0][0]=''
        matrice[0][1]='-'
        for i in range(len(self.nonbasis)):
            matrice[0][2+i]=self.nonbasis[i]
        matrice[1][0]='z'
        for j in range(len(self.basis)):
            matrice[2+j][0]=self.basis[j]
        for i in range(len(self.obj)):
            matrice[1][i+1]=self.obj[i].stringa()
        for i in range(len(self.basis)):
            for j in range(len(self.nonbasis)+1): #ho messo +1 sopra
                matrice[2+i][1+j]=self.rows[i][j].stringa()
        return(matrice)

    def _formaintermedia_completo(self):
        matrice=[['0' for i in range(len(self.nonbasis)+len(self.basis)+2)] for j in range(len(self.basis)+2)]
        matrice[0][0]=''
        for i in range(len(self.nonbasis)):
            matrice[0][1+i]=self.nonbasis[i]
        for i in range(len(self.basis)):
            matrice[0][1+len(self.nonbasis)+i]=self.basis[i]
        matrice[0][-1]='b'
        for j in range(len(self.basis)):
            matrice[1+j][0]=self.basis[j]
        matrice[-1][0]='c.c.r'
        for i in range(len(self.basis)):
            for j in range(1,len(self.nonbasis)+1):
                matrice[1+i][j]=(self.rows[i][j].cambiosegno1()).stringa()
        for i in range(len(self.basis)):
            matrice[1+i][-1]=self.rows[i][0].stringa()
            for j in range(len(self.id)):
                matrice[1+i][1+len(self.nonbasis)+j]=(self.id[i][j]).stringa()
        for i in range(1,len(self.obj)):
            matrice[-1][i]=self.obj[i].stringa()
        matrice[-1][-1]=self.obj[0].cambiosegno1().stringa()
        return(matrice)

    def _formaintermedia(self,tipo):
        if tipo=='classico':
            return self._formaintermedia_classico()
        if tipo=='completo':
            return self._formaintermedia_completo()

            
    def _python(self,matrice):
        s=''
        for i in range(len(matrice)):
            for j in range(len(matrice[0])):
                if j==0:
                    s+=matrice[i][j]
                else:
                    s+='\t'+matrice[i][j]
            s+='\n'
        print(s)

    def _markdown(self,matrice):
        s='|'
        for i in range(len(matrice[0])):
            s+=matrice[0][i]+'|'
        s+='\n|'
        for i in range(len(matrice[0])):
            s+='--|'
        s+='\n'
        for i in range(1,len(matrice)):
            for j in range(len(matrice[0])):
                if j==0:
                    s+='|'+matrice[i][j]+'|'
                else:
                    s+='\t'+matrice[i][j]+'|'
            s+='\n'
        display(Markdown(s))

    def _latex(self,matrice):
        s='\[ \n'
        s+=r'\begin{array}{l'
        for i in range(len(matrice[0])-1):
            s+='c'
        s+='}\n'
        for i in range(1,len(matrice[0])):
            s+='&'+matrice[0][i]
        s+=r'\\'
        for i in range(1,len(matrice)):
            for j in range(len(matrice[0])):
                if j+1==len(matrice[0]):
                    s+=matrice[i][j]+r'\\'+'\n'
                else:
                    s+=matrice[i][j]+'&'
        s+='\n\end{array}\n\]'
        display(Latex(s))
        

    def mostra_tableau(self,tipo,linguaggio):
            matrice=self._formaintermedia(tipo)
            if linguaggio=='latex':
                self._latex(matrice)
            if linguaggio=='python':
                self._python(matrice)
            if linguaggio=='markdown':
                self._markdown(matrice)


                
        
        
        
        
        
        
        
        

                
        
        
    
                
            
            
            
        

            


        
