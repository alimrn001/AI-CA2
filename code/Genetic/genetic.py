import random 
import copy
import time

CrossoverProbability = 0.7
MutationProbability = 0.1
CarryProbability = 0.3
PopulationSize = 20

GoalMinReturn = 2.5
GoalMaxRisk = 0.4
GoalMinStocks = 3


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
        #self.setStocksCoeffScale()
        #self.setFitness()

    def setStocksCoeffScale(self) :
        sum = 0
        for st in self.stocks :
            sum += st.coefficient

        for st in self.stocks :
            st.coefficient /= sum

    def setFitness(self) :
        returnGoal, riskGoal, stockGoal = 0,0,0

        if(self.stocksNum > GoalMinStocks) :
            stockGoal = 0
        else :
            stockGoal = abs(self.stocksNum - GoalMinStocks)

        if(self.returnVal > GoalMinReturn) :
            returnGoal = 0
        else :
            returnGoal = abs(self.returnVal - GoalMinReturn)

        if(self.riskVal < GoalMaxRisk) :
            riskGoal = 0
        else :
            riskGoal = abs(self.riskVal - GoalMaxRisk)
           
        fitness = 1 / (stockGoal + returnGoal + riskGoal + 1)
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
            returnVal += stock.coefficient * stock.returnVal
        self.returnVal = returnVal

    def setAvgRisk(self) :
        riskVal = 0
        for stock in self.stocks :
            riskVal += stock.coefficient * stock.riskVal
        self.riskVal = riskVal


stockData = []
Aapl = Stock("AAPL", 0.2586, 0.9482)
Googl = Stock("GOOGL", 0.4285, 0.466)
Amzn = Stock("AMZN", 0.5779, 0.1)
Tsla = Stock("TSLA", 0.7, 5.12)
Msft = Stock("MSFT", 0.3, 0.56)
Nvda = Stock("NVDA", 0.62, 2.27)

stockData.append(Aapl)
stockData.append(Googl)
stockData.append(Amzn)
stockData.append(Tsla)
stockData.append(Msft)
stockData.append(Nvda)

def getInitialPopulation() :
    population = []
    
    for i in range(PopulationSize) :
        r=[]
        # r = [random.random() for j in range(0,len(stockData))]
        # s = sum(r)
        # r = [ i/s for i in r ]
        for j in range(0,len(stockData)) :
            r.append(random.random())

        for k in range(0, len(r)) : 
            stockData[k].setCoefficient(r[k])

        stockDataCp = copy.deepcopy(stockData)
        investment = Investment(stockDataCp)
    
        population.append(investment)
        
    return population

def getReturnInInvestment(investment) :
    returnVal = 0
    for stock in investment :
        returnVal += stock.coefficient * stock.returnVal
    return returnVal

def getRiskInInvestment(investment) :
    riskVal = 0
    for stock in investment :
        riskVal += stock.coefficient * stock.riskVal
    return riskVal

def getNumOfStocksInInvestment(investment) :
    numOfStocks = 0
    for stock in investment :
        if(stock.coefficient != 0) :
            numOfStocks += 1
    return numOfStocks

def calculateFitness(population) :
    for chromosome in population :
        chromosome.setFitness() 

def applyCrossover(matingPool) : #mating pool is chromosome population
    crossoverPool, parents = [], []
    
    for i in range(len(matingPool)-1) : #last item never gets inside crossover !!
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
            mutated.stocks[i].coefficient += random.random() # 0 to 1
            changed = True
            #print('in i = ', i, 'mutation result = ', mutated.stocks[i].coefficient)

    if(changed) :
        x = Investment(copy.deepcopy(mutated.stocks))
        x.setFitness()
        return x
        # mutated.setStocksCoeffScale()
        # mutated.setAvgReturn()
        # mutated.setAvgRisk()
        # mutated.setStocksNumber()
        # mutated.setFitness()
    
    return chromosome

def applyGenetic(population) : 
    
    cnt=0
    
    while(True) :
        cnt += 1

        if(cnt==300 or cnt == 2 or cnt == 20) :
            print('cnt = ', cnt)
            for investment in population :
                for st in investment.stocks :
                    print(st.coefficient, " ", end=' ')
                print('fitness : ', investment.fitness)
                #print('return : ', investment.returnVal)
                #print('stocks num : ', investment.stocksNum)
                #print('risk : ', investment.riskVal)
            print('----------------------')

        random.shuffle(population)
        calculateFitness(population)

        #print('population size : ', len(population))

        for invest in population :
            if(invest.fitness == 1) :
                return invest

        if(cnt == 10000) :
            break

        carriedChromosomes, selectedChromosomes = [], copy.deepcopy(population)
        selectedChromosomes.sort(reverse=True, key=lambda x : x.fitness)

        for i in range(0, int(PopulationSize*CarryProbability)) :
            carriedChromosomes.append(selectedChromosomes[i])
        
        crossoverPool = applyCrossover(copy.deepcopy(population))
        population.clear()

        for i in range(int(PopulationSize*(1-CarryProbability))) :
            population.append(applyMutation(crossoverPool[i]))
            #population.append(crossoverPool[i])
            

        population.extend(carriedChromosomes)




stime = time.time()

population = getInitialPopulation()
result = applyGenetic(population)

for st in result.stocks :
    print(st.coefficient, " ", end=' ')
print('fitness : ', result.fitness)
print('return : ', result.returnVal)
print('stocks num : ', result.stocksNum)
print('risk : ', result.riskVal)



# calculateFitness(population)
# crossOver = applyCrossover(population)

print("--- %s seconds ---" % (time.time() - stime))

# print('init population')
# for investment in population :
#     for st in investment.stocks :
#         print(" ", st.coefficient, end=' ')  
#     print('\n----------------------------------------------')

# print('\n\n---------------------- cross over -------------------------\n\n')

# # print(len(list(set(crossOver))))

# for investment in crossOver :
#     for st in investment.stocks :
#         print(st.coefficient, " ", end=' ')
#     print('fitness : ', investment.fitness)
#     print('return : ', investment.returnVal)
#     print('stocks num : ', investment.stocksNum)
#     print('risk : ', investment.riskVal)

