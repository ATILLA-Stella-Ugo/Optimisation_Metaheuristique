from random import randint,sample,shuffle
import pandas as pd


class task:
    def __init__(self,nbInstruction):
        self.nbInstruction=nbInstruction

class VM:
    def __init__(self,ComputerRate,UseCost,FailureRate,NetworkTime):
        self.ComputerRate=ComputerRate
        self.UseCost=UseCost
        self.FailureRate=FailureRate
        self.NetworkTime=NetworkTime


def generateTasksAndVMs():
    Tasks=[]
    VMs=[]
    dfTask = pd.read_csv('data/Hybrid15_comp.csv')
    dfVM = pd.read_csv('data/Ressource_car.csv')
    for Task in dfTask["nbInstruction"]:
        Tasks.append(task(Task))
    for i in range(len(dfVM)):
        VMs.append(VM(dfVM["ComputerRate"][i],dfVM["UseCost"][i],dfVM["FailureRate"][i],20))
    return(pd.DataFrame(Tasks),pd.DataFrame(VMs))

def generate_random_genome(nT,nVM):
    return([randint(0,nT) for i in range(nVM)])


def generate_random_population(n,nT,nVM):
    return([generate_random_genome(nT,nVM) for i in range(n)])

def croisement(mom,dad,nT,nVM):
    random_genes=sample(range(nT),k=4)
    random_mutation=randint(0,nT-1)
    baby=[]
    for i in range(nT):
        if (i in random_genes):
            baby.append(mom[i])
        else:
            baby.append(dad[i])
        if (i==random_mutation):
            baby[i]=(baby[i]+1)%nVM
    return baby

def reproduction(population):
    babies=[]
    N=len(population)
    for i in range (N):
        mom=population[i]
        dad=population[(i+1)%N]
        babies.append(croisement(mom,dad))
    population=population+babies
    shuffle(population)
    return(population)

def make_subpopulations(population):
    n=len(population)
    return(population[:n//3],population[n//3:2*n//3],population[2*n//3:n])

def tolist(string):
    List=string[1:-1].split(",")
    for i in range (len(List)):
        List[i]=int(List[i])
    return(List)
        
def adapt_res(res):
    newRes=[]
    for elem in res:
        newRes.append(tolist(elem[0]))
    return newRes    
    
def select_salary(subpop,n):
    N=len(subpop)
    dic={}
    for individual in subpop:
        salary=0
        for j in range(len(individual)):
            if (individual[j]):
                salary+=celebrities[j].salary
        dic[str(individual)]=salary
    res=sorted(dic.items(), key=lambda x:x[1])
    return (adapt_res(res[N-n//3:]))
    
def select_publicity(subpop,n):
    N=len(subpop)
    dic={}
    for individual in subpop:
        salary=0
        for j in range(len(individual)):
            if (individual[j]):
                salary+=celebrities[j].publicity
        dic[str(individual)]=salary
    res=sorted(dic.items(), key=lambda x:x[1])
    return (adapt_res(res[N-n//3:]))


def select_weight(subpop,n):
    N=len(subpop)
    dic={}
    for individual in subpop:
        salary=0
        for j in range(len(individual)):
            if (individual[j]):
                salary+=celebrities[j].weight
        dic[str(individual)]=salary
    res=sorted(dic.items(), key=lambda x:x[1])
    return (adapt_res(res[N-n//3:]))

def main(n):
    population=generate_random_population(n)
    for i in range(80):
        print("étape "+str(i)+":")
        sub1,sub2,sub3=make_subpopulations(population)
        sub1=select_salary(sub1,n)
        sub2=select_publicity(sub2,n)
        sub3=select_weight(sub3,n)
        print(sub1[-1],sub2[-1],sub3[-1])
        shuffle(population)
        reproduction(population)
        
        

    