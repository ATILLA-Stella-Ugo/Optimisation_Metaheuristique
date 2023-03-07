#Import libraries
from random import randint,sample,shuffle
import pandas as pd

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

    def setFeetness (self,score):
        self.feetness=score
        
#Class for individual
class IndividualClass:
    feetness=None
    def __init__(self,individual):
        self.individual=individual
    def setFeetness (self,score):
        self.feetness=score
    def show(self):
        string="["
        for DV in self.individual:
            string+='{'+str(DV.TaskId)+','+str(DV.VMId)+'}'
        string+="]"
        print(string)


#function that displays a population
def populationShow(population,printFeetness=False):
    for individual in population:
        individual.show()
        if printFeetness:
            print(individual.feetness)

#function that reads files to get tasks and virtual machines
def generateTasksAndVMs():
    Tasks=[]
    VMs=[]
    dfTask = pd.read_csv('data/Hybrid15_comp.csv')
    dfVM = pd.read_csv('data/Ressource_car.csv')
    for i,Task in enumerate(dfTask["nbInstruction"]):
        Tasks.append(TaskClass(i,Task))
    for i in range(len(dfVM)):
        VMs.append(VMClass(i,dfVM["ComputerRate"][i],dfVM["UseCost"][i],dfVM["FailureRate"][i],20))
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

#sort population by feetness, remove the less feet inividuals
def natural_selection(n,population):
    #TODO retirer le feetness de test
    for individual in population:
        individual.setFeetness(randint(0,1000))
    population.sort(key=lambda x: x.feetness, reverse=True)
    return(population[:n])

def test():
    Tasks,VMs=generateTasksAndVMs()
    population=generate_random_population(10,Tasks,VMs)
    populationShow(population)
    print("reproduction")
    population=reproduction(population,Tasks,VMs)
    populationShow(population)
    print("natural selection")
    population=natural_selection(10, population)
    populationShow(population, printFeetness = True)



# =============================================================================
# 
# def make_subpopulations(population):
#     n=len(population)
#     return(population[:n//3],population[n//3:2*n//3],population[2*n//3:n])
# 
# def tolist(string):
#     List=string[1:-1].split(",")
#     for i in range (len(List)):
#         List[i]=int(List[i])
#     return(List)
#         
# def adapt_res(res):
#     newRes=[]
#     for elem in res:
#         newRes.append(tolist(elem[0]))
#     return newRes    
#     
# def select_salary(subpop,n):
#     N=len(subpop)
#     dic={}
#     for individual in subpop:
#         salary=0
#         for j in range(len(individual)):
#             if (individual[j]):
#                 salary+=celebrities[j].salary
#         dic[str(individual)]=salary
#     res=sorted(dic.items(), key=lambda x:x[1])
#     return (adapt_res(res[N-n//3:]))
#     
# def select_publicity(subpop,n):
#     N=len(subpop)
#     dic={}
#     for individual in subpop:
#         salary=0
#         for j in range(len(individual)):
#             if (individual[j]):
#                 salary+=celebrities[j].publicity
#         dic[str(individual)]=salary
#     res=sorted(dic.items(), key=lambda x:x[1])
#     return (adapt_res(res[N-n//3:]))
# 
# 
# def select_weight(subpop,n):
#     N=len(subpop)
#     dic={}
#     for individual in subpop:
#         salary=0
#         for j in range(len(individual)):
#             if (individual[j]):
#                 salary+=celebrities[j].weight
#         dic[str(individual)]=salary
#     res=sorted(dic.items(), key=lambda x:x[1])
#     return (adapt_res(res[N-n//3:]))
# 
# def main(n):
#     population=generate_random_population(n)
#     for i in range(80):
#         print("étape "+str(i)+":")
#         sub1,sub2,sub3=make_subpopulations(population)
#         sub1=select_salary(sub1,n)
#         sub2=select_publicity(sub2,n)
#         sub3=select_weight(sub3,n)
#         print(sub1[-1],sub2[-1],sub3[-1])
#         shuffle(population)
#         reproduction(population)
#         
#         
# 
#     
# =============================================================================
