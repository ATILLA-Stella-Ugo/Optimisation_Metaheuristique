#Import libraries
from random import randint,sample,shuffle
import pandas as pd
from math import exp
from copy import deepcopy
import matplotlib.pyplot as plt
#pip install plotly
#pip install -U kaleido
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio


#parameters calculation 

#T_ex(Tij) aka Execution Time
def Tex(T):
    return(T.nbInstruction/T.ComputerRate)

def Cex(X):
    res=0
    for DV in X:
        res+=Tex(DV)*DV.UseCost
    return(res)

def F(X):
    res=0
    for DV in X:
        res+=(Tex(DV)*DV.FailureRate)
    return (exp(-1*res))

def L(X):
    res=0
    for DV in X:
        res+= Tex(DV)+DV.NetworkTime
    return(res)
    


####Classes

#Class for task 
class TaskClass:
    def __init__(self,Id,nbInstruction):
        self.Id=Id
        self.nbInstruction=nbInstruction

#Class for virtual machine
class VMClass:
    def __init__(self,Id,ComputerRate,UseCost,FailureRate,NetworkTime):
        self.Id=Id
        self.ComputerRate=ComputerRate
        self.UseCost=UseCost
        self.FailureRate=FailureRate
        self.NetworkTime=NetworkTime

#Class for decision variable
class DVClass:
    def __init__(self,Task, VM):
        self.Task=Task
        self.VM=VM
        self.TaskId=Task.Id
        self.nbInstruction=Task.nbInstruction
        self.VMId=VM.Id
        self.ComputerRate=VM.ComputerRate
        self.UseCost=VM.UseCost
        self.FailureRate=VM.FailureRate
        self.NetworkTime=VM.NetworkTime
        
#Class for individual
class IndividualClass:
    def __init__(self,individual):
        self.individual = individual
        self.CostEx = Cex(individual)
        self.Reliability = F(individual)
        self.Latency = L(individual)
        self.Rank = None
              
    def setRank(self, rank):
        self.Rank = rank
        
    def show(self):
        string="["
        for DV in self.individual:
            string+='{'+str(DV.TaskId)+','+str(DV.VMId)+'}'
        string+="]"
        print(string)


#function that displays a population
def populationShow(population,printData=False):
    for individual in population:
        individual.show()
        if printData:
            print(individual.CostEx,individual.Reliability,individual.Latency)

#function that reads files to get tasks and virtual machines
def generateTasksAndVMs():
    Tasks=[]
    VMs=[]
    dfTask = pd.read_csv('data/Hybrid15_comp.csv')
    dfVM = pd.read_csv('data/Ressource_car.csv')
    for i,Task in enumerate(dfTask["nbInstruction"]):
        Tasks.append(TaskClass(i,Task))
    for i in range(len(dfVM)):
        VMs.append(VMClass(i,dfVM["ComputerRate"][i],dfVM["UseCost"][i],dfVM["FailureRate"][i],randint(1,20)))
    return(pd.DataFrame(Tasks)[0],pd.DataFrame(VMs)[0])

#function generating a random individual
#a gene is a decision variable
#a individual is  a potential solution
def generate_random_individual(Tasks,VMs):
    nT=len(Tasks)
    nVM=len(VMs)
    individual=[DVClass(Tasks[i],VMs[randint(0,nVM-1)]) for i in range(nT)]
    return(IndividualClass(individual))

#generates a random population of n individuals
def generate_random_population(n,Tasks,VMs):
    return([generate_random_individual(Tasks,VMs) for i in range(n)])

#crosses randomely genes of two parents to make a baby
#one gene is randomely muteted in the process
def croisement(mom,dad,Tasks,VMs):
    nT=len(Tasks)
    nVM=len(VMs)
    random_genes=sample(range(nT),k=nT//2)
    random_mutation=randint(0,nT-1)
    baby=[]
    for i in range(nT):
        if (i in random_genes):
            baby.append(mom.individual[i])
        else:
            baby.append(dad.individual[i])
        if (i==random_mutation):
            baby[i]=DVClass(Tasks[i],VMs[randint(0,nVM-1)])
    return IndividualClass(baby)

#generation of a new population by breeding the previous one
#the old generation stays and will pass the feetness selection alongside the childrens
def reproduction(population,Tasks,VMs):
    babies=[]
    N=len(population)
    for i in range (N):
        mom=population[i]
        dad=population[(i+1)%N]
        babies.append(croisement(mom,dad,Tasks,VMs))
    population=population+babies
    shuffle(population)
    return(population)

def create_subgroups(population):
    deepcopyPop=deepcopy(population)
    subgroups=[]
    while(len(population)>0):
        subgroup=[]
        for i in reversed(range(len(population))):
            boolean=True
            Xi=population[i]
            for j in range (len(population)):
                Xj=population[j]
                #print(i,j)
                #print(Xi.CostEx <= Xj.CostEx)
                #print(Xi.Reliability>=Xj.Reliability)
                #print(Xi.Latency<=Xj.Latency)
                #if(i==j):
                #    print("i==j")
                if (not(Xi.CostEx <= Xj.CostEx or Xi.Reliability>=Xj.Reliability or Xi.Latency <= Xj.Latency)):
#                if (not(Xi.CostEx <= Xj.CostEx or Xi.Reliability>=Xj.Reliability)):
                   boolean=False 
                   #break
                
            if (boolean):
                subgroup.append(deepcopyPop.pop(i))
        subgroups.append(subgroup)
        population=deepcopy(deepcopyPop)
    return(subgroups)
    
# =============================================================================
# 
# def crowding_distance_sorting(front):
#     n = len(front)
#     distances = [0] * n
#     
#     # Initialize the distances for the first and last individuals as infinity
#     distances[0] = float("inf")
#     distances[n-1] = float("inf")
#     
#     objectivesmin=[front[0].CostEx,front[0].Reliability,front[0].Latency]
#     objectivesmax=[front[0].CostEx,front[0].Reliability,front[0].Latency]
#     # Calculate the distance for each individual in the front
#     for m in range(len(objectivesmin)):
#         front = sorted(front, key=lambda individual: individual.objectives[m])
#         f_min = objectivesmin
#         f_max = objectivesmin
#         
#         # Avoid division by zero
#         if f_max == f_min:
#             continue
#         
#         # Calculate the distance for each individual in the front based on the m-th objective
#         for i in range(1, n-1):
#             distances[i] += (front[i+1].objectives[m] - front[i-1].objectives[m]) / (f_max - f_min)
#     
#     # Assign the crowding distance to each individual in the front
#     for i in range(n):
#         front[i].crowding_distance = distances[i]
#     
#     # Sort the front based on the crowding distance
#     front = sorted(front, key=lambda individual: individual.crowding_distance, reverse=True)
#     
#     return front
# =============================================================================


def giveRank(sub_groups):
    for i,sub_group in enumerate(sub_groups):
#        sub_group=crowding_distance_sorting(sub_group)
        for individual in sub_group:
            individual.setRank(i+1)     
    return(sub_groups)

#sort population by feetness, remove the less feet inividuals
def natural_selection(n,sub_groups):
    newPop=[individual for rank in sub_groups for individual in rank]
    return(newPop[:n])

def display_means(population):
    sumCostEx=sum(individual.CostEx for individual in population)
    sumReliability=sum(individual.Reliability for individual in population)
    sumLatency=sum(individual.Latency for individual in population)
    n=len(population)
    print(sumCostEx/n,sumReliability/n,sumLatency/n)


def test():
    Tasks,VMs=generateTasksAndVMs()
    population=generate_random_population(100,Tasks,VMs)
    populationShow(population)
    print("reproduction")
    population=reproduction(population,Tasks,VMs)
    populationShow(population)
    print("natural selection")
    rankedPop=create_subgroups(population)
    population=natural_selection(100, rankedPop)
    populationShow(population)

def show_Domination_Plot (population, save=False):

    x = []
    y = []
    z = []
    c = []
    for individual in population:
        x.append(individual.CostEx)
        y.append(individual.Reliability)
        z.append(individual.Latency)
        c.append(individual.Rank)
    pio.renderers.default = 'browser'
    fig = px.scatter_3d(x=x, y=y, z=z, color=c, 
                        title='Scatter points showing domination', 
                        labels={'x': 'Execution Cost', 'y': 'Reliability', 'z': 'Latency'})
    fig.update_layout(scene=dict(xaxis=dict(title='Execution Cost'),
                                  yaxis=dict(title='Reliability'),
                                  zaxis=dict(title='Latency')))
    
    if save:
        fig.write_image(f'{save}.png')
        
    fig.show()

def main(population_size=200,nb_generations=100):
    Tasks,VMs=generateTasksAndVMs()
    population=generate_random_population(population_size,Tasks,VMs)
    #populationShow(population, printData=True)
    display_means(population)
    for i in range(nb_generations):
         if (i%10==0):
             print("étape "+str(i))
         shuffle(population)
         population=reproduction(population,Tasks,VMs)
         rankedPop=create_subgroups(population)
         rankedPop=giveRank(rankedPop)
         population=natural_selection(population_size, rankedPop)
         if (i==0 or i==nb_generations-1):
                 show_Domination_Plot(population,save="Plot_generation "+str(i))
    print("final generation")
    #populationShow(population)
    display_means(population)
