import random 
import copy

CrossoverProbability = 0.7
MutationProbability = 0.05
CarryProbability = 1 - CrossoverProbability
PopulationSize = 10

GoalMinReturn = 1000
GoalMaxRisk = 60
GoalMinStocks = 30


class Stock :
    def __init__(self, ticker, riskVal, returnVal) :
        self.ticker = ticker
        self.riskVal = riskVal
        self.returnVal = returnVal
        self.coefficient = 0

    def setCoefficient(self, coefficient):
        self.coefficient = coefficient


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
        r = [random.random() for j in range(0,len(stockData))]
        s = sum(r)
        r = [ i/s for i in r ]
        
        for k in range(0, len(r)) : 
            stockData[k].setCoefficient(r[k])

        stockDataCp = copy.deepcopy(stockData)
        population.append(stockDataCp)
        
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

def getFitness(investment) :
    returnGoal, riskGoal, stockGoal = 0,0,0
    investmentStocks = getNumOfStocksInInvestment(investment)
    investmentReturn = getReturnInInvestment(investment)
    investmentRisk = getRiskInInvestment(investment)

    if(investmentStocks > GoalMinStocks) :
        stockGoal = 0
    else :
        stockGoal = abs(investmentStocks - GoalMinStocks)

    if(investmentReturn > GoalMinReturn) :
        returnGoal = 0
    else :
        returnGoal = abs(investmentReturn - GoalMinReturn)

    if(investmentRisk < GoalMaxRisk) :
        riskGoal = 0
    else :
        riskGoal = abs(investmentRisk - GoalMaxRisk)
           
    fitness = 1 / (stockGoal + returnGoal + riskGoal + 1)
    
    return fitness



population = getInitialPopulation()

for investment in population :
    print(getFitness(investment))