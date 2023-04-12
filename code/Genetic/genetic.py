import random 
import copy
import time
import pandas as pd


CrossoverProbability = 0.7
MutationProbability = 0.3
CarryProbability = 0.4
PopulationSize = 1000
MaxRandomVal = 200
GoalMinReturn = 10
GoalMaxRisk = 0.6
GoalMinStocks = 30


class Stock : #each element of a gene

    def __init__(self, ticker, riskVal, returnVal) :
        self.ticker = ticker
        self.riskVal = riskVal
        self.returnVal = returnVal
        self.coefficient = 0

    def setCoefficient(self, coefficient):
        self.coefficient = coefficient


class Investment : # acts as a chromosome

    def __init__(self, stocks) :
        self.stocks = stocks
        self.setStocksCoeffScale()
        self.setAvgReturn()
        self.setAvgRisk()
        self.setStocksNumber()

    def setStocksCoeffScale(self) :
        sum = 0
        for st in self.stocks :
            sum += st.coefficient

        for st in self.stocks :
            st.coefficient /= sum
            st.coefficient *= 100

    def setFitness(self) :
        # returnGoal, riskGoal, stockGoal = 0,0,0

        # if(self.stocksNum > GoalMinStocks) :
        #     stockGoal = 0
        # else :
        #     stockGoal = abs(self.stocksNum - GoalMinStocks)

        # if(self.returnVal > GoalMinReturn) :
        #     returnGoal = 0
        # else :
        #     returnGoal = abs(self.returnVal - GoalMinReturn)

        # if(self.riskVal < GoalMaxRisk) :
        #     riskGoal = 0
        # else :
        #     riskGoal = abs(self.riskVal - GoalMaxRisk)
           
        # fitness = 1 / (stockGoal + returnGoal + riskGoal + 1)

        fitness = self.returnVal / self.riskVal

        self.fitness = fitness
    
    def setStocksNumber(self) :
        stocksNo = 0
        for stock in self.stocks : 
            if(stock.coefficient != 0) :
                stocksNo += 1
        self.stocksNum = stocksNo

    def setAvgReturn(self) :
        returnVal = 0
        for stock in self.stocks :
            returnVal += stock.coefficient/100 * stock.returnVal
        self.returnVal = returnVal

    def setAvgRisk(self) :
        riskVal = 0
        for stock in self.stocks :
            riskVal += stock.coefficient/100 * stock.riskVal
        self.riskVal = riskVal

stockData = []

def getCsvData(fileName) : 
    df = pd.read_csv('sample.csv')
    for index, row in df.iterrows() :
        stock = Stock(row['ticker'], float(row['risk']), float(row['return']))
        stockData.append(stock)

def getInitialPopulation() :
    population = []
    
    for i in range(PopulationSize) :
        r=[]
        for j in range(0,len(stockData)) :
            r.append(random.randint(0, MaxRandomVal))

        for k in range(0, len(r)) : 
            stockData[k].setCoefficient(r[k])

        stockDataCp = copy.deepcopy(stockData)
        investment  = Investment(stockDataCp)

        population.append(investment)
        
    return population

def calculateFitness(population) :
    for chromosome in population :
        chromosome.setFitness() 

def applyCrossover(matingPool) : #mating pool is chromosome population
    crossoverPool, parents = [], []
    
    for i in range(len(matingPool)-1) : 
        if(random.random() > CrossoverProbability) :
            crossoverPool.append(matingPool[i])
        else :
            parents.append(matingPool[i])
        
    for chromosome1, chromosome2 in zip(parents, parents[1:]) :
        i = random.randint(1, chromosome1.stocksNum - 1)
        chromosome1Stock = copy.deepcopy(chromosome1.stocks)
        chromosome2Stock = copy.deepcopy(chromosome2.stocks)

        child1 = Investment( chromosome1Stock[:i] + chromosome2Stock[i:] )
        child2 = Investment( chromosome2Stock[:i] + chromosome1Stock[i:] )

        crossoverPool.append(child1)
        crossoverPool.append(child2)

    calculateFitness(crossoverPool)
    crossoverPool.sort(reverse=True, key=lambda x : x.fitness)
    return crossoverPool

def applyMutation(chromosome) :
    changed=False
    mutated = copy.deepcopy(chromosome)
    for i, gene in enumerate(mutated.stocks) :
        r = random.random()
        if(r < MutationProbability) :
            mutated.stocks[i].coefficient = random.randint(0, MaxRandomVal) # 0 to 200
            changed = True

    if(changed) :
        x = Investment(copy.deepcopy(mutated.stocks))
        x.setFitness()
        return x

    return chromosome

def applyGenetic(population) : 
    
    while(True) :
        random.shuffle(population)
        calculateFitness(population)

        for invest in population :
            if(invest.fitness >= GoalMinReturn/GoalMaxRisk and invest.returnVal >= GoalMinReturn and invest.riskVal <= GoalMaxRisk and invest.stocksNum >= GoalMinStocks) :    
                return invest

        carriedChromosomes, selectedChromosomes = [], copy.deepcopy(population)
        selectedChromosomes.sort(reverse=True, key=lambda x : x.fitness)

        for i in range(0, int(PopulationSize*CarryProbability)) :
            carriedChromosomes.append(selectedChromosomes[i])
        
        crossoverPool = applyCrossover(copy.deepcopy(population))
        population.clear()

        for i in range(int(PopulationSize*(1-CarryProbability))) :
            population.append(applyMutation(crossoverPool[i]))
            
        population.extend(carriedChromosomes)


stime = time.time()
getCsvData('sample.csv')

population = getInitialPopulation()
result = applyGenetic(population)

for st in result.stocks :
    print(st.coefficient, " ", end=' ')
print('fitness : ', result.fitness)

print("--- %s seconds ---" % (time.time() - stime))
