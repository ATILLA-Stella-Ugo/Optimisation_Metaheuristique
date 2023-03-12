#Import libraries
from random import randint,sample,shuffle
import pandas as pd
from math import exp
from copy import deepcopy
import matplotlib.pyplot as plt
#pip install plotly
#pip install -U kaleido
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
        self.Crowding_distance=None
              
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
        VMs.append(VMClass(i,dfVM["ComputerRate"][i],dfVM["UseCost"][i],dfVM["FailureRate"][i],dfVM["NetworkTime"][i]))
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

def create_subgroups(population,removeParameter=False):
    deepcopyPop=deepcopy(population)
    subgroups=[]
    while(len(population)>0):
        subgroup=[]
        for i in reversed(range(len(population))):
            boolean=True
            Xi=population[i]
            for j in range (len(population)):
                Xj=population[j]
                if (removeParameter=="CostEx"):
                    if (Xi.Reliability < Xj.Reliability and Xi.Latency > Xj.Latency):
                        boolean=False 
                        break                
                elif (removeParameter=="Reliability"):
                    if (Xi.CostEx > Xj.CostEx and Xi.Latency > Xj.Latency):
                        boolean=False 
                        break
                elif (removeParameter=="Latency"):
                    if (Xi.CostEx > Xj.CostEx and Xi.Reliability < Xj.Reliability):
                        boolean=False 
                        break
                else:
                    if (Xi.CostEx > Xj.CostEx and Xi.Reliability < Xj.Reliability and Xi.Latency > Xj.Latency):
                        boolean=False 
                        break
                
            if (boolean):
                subgroup.append(deepcopyPop.pop(i))
        subgroups.append(subgroup)
        population=deepcopy(deepcopyPop)
    return(subgroups)
    


def crowding_distance_sorting(sub_group, removeParameter=False):
    n=len(sub_group)
    distances=[0 for i in range(n)]
    distances[0]=float("inf")
    distances[-1]=float("inf")
    if (not removeParameter=="CostEx"):
        sub_group = sorted(sub_group, key=lambda individual: individual.CostEx)
        f_min = sub_group[0].CostEx
        f_max = sub_group[-1].CostEx
        if (f_max != f_min):
            for i in range(1,n-1):
                distances[i] += (sub_group[i+1].CostEx - sub_group[i-1].CostEx) / (f_max - f_min)
    
    if (not removeParameter=="Reliability"):
        sub_group = sorted(sub_group, key=lambda individual: individual.Reliability)
        f_min = sub_group[0].Reliability
        f_max = sub_group[-1].Reliability
        if (f_max != f_min):
            for i in range(1,n-1):
                distances[i] += (sub_group[i+1].Reliability - sub_group[i-1].Reliability) / (f_max - f_min)

    if (not removeParameter=="Latency"):
        sub_group = sorted(sub_group, key=lambda individual: individual.Latency)
        f_min = sub_group[0].Latency
        f_max = sub_group[-1].Latency
        if (f_max != f_min):
            for i in range(1,n-1):
                distances[i] += (sub_group[i+1].Latency - sub_group[i-1].Latency) / (f_max - f_min)

    for i in range(n):
         sub_group[i].crowding_distance = distances[i]
     
    sub_group = sorted(sub_group, key=lambda individual: individual.crowding_distance, reverse=True)
     
    return sub_group

def sort_sub_group(sub_groups,removeParameter=False):
    new_sub_groups=[]
    for sub_group in sub_groups:
        new_sub_groups.append(crowding_distance_sorting(sub_group,removeParameter))
    return(new_sub_groups)

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


def show_Domination_Plot_3D (population, save=False):

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

def show_Domination_Plot_2D (population,xattribute,yattribute, save=False):
    x = []
    y = []
    c = []
    pio.renderers.default = 'browser'
    for individual in population:
        if (xattribute=="CostEx"):
            x.append(individual.CostEx)
        elif (xattribute=="Reliability"):
            x.append(individual.Reliability)
        else:
            x.append(individual.Latency)
        if (yattribute=="CostEx"):
            y.append(individual.CostEx)
        elif (yattribute=="Reliability"):
            y.append(individual.Reliability)
        else:
            y.append(individual.Latency)
                    
        c.append(individual.Rank)
    plt.scatter(x,y,c=c)
    if save:
        plt.savefig(f'{save}.png')
    plt.show()
    

def show_Domination_Plot(population, removeParameter=False, save= False):
    if removeParameter=="CostEx":
        show_Domination_Plot_2D(population,"Reliability","Latency",save)
    elif removeParameter=="Reliability":
        show_Domination_Plot_2D(population,"CostEx","Latency",save)
    elif removeParameter=="Latency":
        show_Domination_Plot_2D(population,"CostEx","Reliability",save)
    else:
        show_Domination_Plot_3D(population, save)

# Select and display the best solution for one of the objectives
def display_best_solution_by_objective(solutions,objective):
    best_solution_for_objective = solutions[0]

    if objective == "CostEx":
        for solution in solutions:
            if solution.CostEx < best_solution_for_objective.CostEx:
                best_solution_for_objective = solution
            elif solution.CostEx == best_solution_for_objective.CostEx:
                if (solution.Latency < best_solution_for_objective.Latency or solution.Reliability > best_solution_for_objective.Reliability):
                    best_solution_for_objective = solution

    elif objective == "Latency":
        for solution in solutions:
            if solution.Latency < best_solution_for_objective.Latency:
                best_solution_for_objective = solution
            elif solution.Latency == best_solution_for_objective.Latency:
                if (solution.CostEx < best_solution_for_objective.CostEx or solution.Reliability > best_solution_for_objective.Reliability):
                    best_solution_for_objective = solution

    elif objective == "Reliability":
        for solution in solutions:
            if solution.Reliability > best_solution_for_objective.Reliability:
                best_solution_for_objective = solution
            elif solution.Reliability == best_solution_for_objective.Reliability:
                if (solution.CostEx < best_solution_for_objective.CostEx or solution.Latency > best_solution_for_objective.Latency):
                    best_solution_for_objective = solution
    
    return best_solution_for_objective

def NSGA_II(population_size=200,nb_generations=100, removeParameter=False, show_convergence=False):
    Tasks,VMs=generateTasksAndVMs()
    population=generate_random_population(population_size,Tasks,VMs)
    display_means(population)
    for i in range(nb_generations):
         if (i%10==0):
             print("étape "+str(i))
         shuffle(population)
         population=reproduction(population,Tasks,VMs)
         rankedPop=create_subgroups(population,removeParameter)
         rankedPop=giveRank(rankedPop)
         rankedPop=sort_sub_group(rankedPop,removeParameter)
         population=natural_selection(population_size, rankedPop)
         if (i==0 or i==nb_generations-1 or show_convergence and(i==2 or i==4 or i==6 or i==10)):
             savefileName="_generation_n-"+str(i)
             if removeParameter:
                 savefileName= "SavedPlots/2D_Plot_"+removeParameter+"_ignored"+savefileName
             else:
                 savefileName= "SavedPlots/3D_Plot"+savefileName
             show_Domination_Plot(population,removeParameter,save=savefileName)
             print(savefileName)
    print("average of final generation parameters:")
    display_means(population)
    print("exemple of some of the fittest individual:")
    population[0].show()
    print(population[0].CostEx,population[0].Reliability,population[0].Latency)
    population[population_size//2].show()
    print(population[population_size//2].CostEx,population[population_size//2].Reliability,population[population_size//2].Latency)
    population[population_size-1].show()
    print(population[population_size-1].CostEx,population[population_size-1].Reliability,population[population_size-1].Latency)
    print()

    best_costEx = display_best_solution_by_objective(population,"CostEx")
    best_latency = display_best_solution_by_objective(population,"Latency")
    best_reliability = display_best_solution_by_objective(population,"Reliability")
    print("best solution for CostEx is : ")
    best_costEx.show()
    print(best_costEx.CostEx,best_costEx.Reliability,best_costEx.Latency)
    print("best solution for Latency is : ")
    best_latency.show()
    print(best_latency.CostEx,best_latency.Reliability,best_latency.Latency)
    print("best solution for Reliability is : ")
    best_reliability.show()
    print(best_reliability.CostEx,best_reliability.Reliability,best_reliability.Latency)

def main ():
    #NSGA_II(removeParameter="CostEx",show_convergence=True)
    #NSGA_II(removeParameter="Reliability")
    #NSGA_II(removeParameter="Latency")
    NSGA_II()
    
main()