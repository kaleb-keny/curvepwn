

from random import seed
from random import randint
from datetime import datetime

import price_calcs

import numpy as np

import solver

N_COINS = 3
PRECISION_MUL = [1, 1000000000000, 1000000000000]

FEE_DENOMINATOR = 10 ** 10
PRECISION = 10 ** 18

MAX_ADMIN_FEE = 10 * 10 ** 9
MAX_FEE = 5 * 10 ** 9

MAX_A = 10 ** 6
MAX_A_CHANGE = 10
A_PRECISION = 100
amp = 2000

ADMIN_ACTIONS_DELAY = 3 * 86400
MIN_RAMP_TIME = 86400

#Expression of the invariant of the USDT pool in the contract code
def USDTpool(xp, amp, D):
    '''
    Return f(D)
    '''
    #amp is already A*n**(n-1)
    Ann = amp*N_COINS
    S = 0
    for _x in xp:
        S += _x
    if S == 0:
        return 0
    P = 1 #product of xi
    for _x in xp:
        P*= _x
    return Ann*S + (1-Ann)*D - (D**(N_COINS+1))/((N_COINS**N_COINS)*P)

current_values = [int(351794.69*10**18),int(689185.73*10**18),int(382505.53*10**18)]

#Test that we get 0 for the current values in the pool
if False:
    D = solver.get_D(current_values, amp)
    print(USDTpool(current_values, amp, D))

#Test that the spot prices are indeed 1 with the current values in the pool

if False:
    D = solver.get_D(current_values, amp)
    invariant = lambda x : USDTpool(x, amp, D)
    spot1 = price_calcs.getSpotPrice(invariant, current_values, [0,1])
    spot2 = price_calcs.getSpotPrice(invariant, current_values, [0,2])
    spot3 = price_calcs.getSpotPrice(invariant, current_values, [2,1])
    spot_prices_list = [spot1, spot2, spot3]
    print("Spot prices: ", spot_prices_list)

#funds we have a available to try to modify the amounts
funds_avail = int(100000000*10**18)

seed(1452789)
best_val = 1e100
best_i = 0
while False:
    #try to guess a solution
    coins = [randint(0, current_values[0]+funds_avail), 
             randint(0, current_values[1]+funds_avail), 
             randint(0, current_values[2]+funds_avail)]
    #value = get_I(coins,amp)
    D = solver.get_D(coins, amp)
    u = USDTpool(coins, amp, D)
    if abs(u)>0:
        print(coins)
        print(D)
        print(u)
        if abs(u)>0:
            diff = 0
            for i in range(0,3):
                diff += abs(coins[i]-current_values[i])
            if(diff<best_val):
                best_val = diff
                print('Solution found!')
                print(coins)
                print('USDTpool: ', USDTpool(coins, amp, D))
                print('Funds required: ', str(best_val/1e18) )
                print('Mod: ', str((coins[0]-current_values[0])/1e18), 'DAI' )
                print('Mod: ', str(( coins[1]-current_values[1])/1e18), 'USDC' )
                print('Mod: ', str(( coins[2]-current_values[2])/1e18), 'USDT' )

#Test all the values of balances found that result in a non zero invariant and see how the spot price and slippage are affected 

#List of the balances that create an issue
x_sols = [
    
    [2552132800774707953221343, 10954836975766391934268855, 6113261289102574864143845],

    [7383156777655277677397696, 5155991404625698646006209, 22062233463650651502213654],

    [8967941795019332620419554, 28138637197367895309556558, 17034664770329254888272019],

    [44592230509332193904618359, 92540796120217289407249535, 52517614521951134668905555],

    [6021622227921786133247673, 75552623271839259833403773, 30535944814071004252802378],

    [54910346171977265790353180, 47063522501931580992726383, 48715838319124038305979407],

    [55861715979112626728798628, 23288891084785364563789167, 27989134995153369213616087],

    [16335250935896498249124052, 42827395606463253065145007, 39735198056483082551992684]
    
    ]

#Spot price test
if False:
    #List storing all the spot prices pair for each pool that is a solution to our problem
    spot_prices_for_solutions = [] 
    for x in x_sols:
        D = solver.get_D(x, amp)
        invariant = lambda x : USDTpool(x, amp, D)
        #Get all the spot prices of the different pairs with that new invariant
        spot1 = price_calcs.getSpotPrice(invariant, x, [0,1])
        spot2 = price_calcs.getSpotPrice(invariant, x, [0,2])
        spot3 = price_calcs.getSpotPrice(invariant, x, [2,1])
        spot_prices_list = [spot1, spot2, spot3]
        spot_prices_for_solutions.append(spot_prices_list)
    print("Max spot price: ", max(sublist[-1] for sublist in spot_prices_for_solutions))
    print("Min spot price: ", min(sublist[-1] for sublist in spot_prices_for_solutions))

#Slippage test with 
if False:
    #List storing all the slippage between the pairs for each pool that is a solution to our problem
    slippage_solutions = [] 
    for x in x_sols:
        D = solver.get_D(x, amp)
        invariant = lambda x : USDTpool(x, amp, D)
        #Get all the spot prices of the different pairs with that new invariant
        spot1 = price_calcs.getSlippage(invariant, x, 10000000*1e18, [0,1])
        spot2 = price_calcs.getSlippage(invariant, x, 10000000*1e18, [0,2])
        spot3 = price_calcs.getSlippage(invariant, x, 10000000*1e18, [2,1])
        slippage_list = [spot1, spot2, spot3]
        slippage_solutions.append(slippage_list)
    print("Max slippage: ", max(sublist[-1] for sublist in slippage_solutions), "%")

#Verify how profitable a potential attack might be by comparing the new spot price with the slippage for a large order
if False:
    attack_balance = [1499652125335257,3153232734120070,427674227529]#cdai, cusdc,usdt
    D = solver.get_D(attack_balance, amp)
    invariant = lambda x : USDTpool(x, amp, D)
    spot0 = price_calcs.getSpotPrice(invariant, attack_balance, [0,1])
    spot1 = price_calcs.getSpotPrice(invariant, attack_balance, [0,2])
    spot2 = price_calcs.getSpotPrice(invariant, attack_balance, [2,1])
    spot_prices_list = [spot0, spot1, spot2]
    max_spot_deviation = max([abs(x - 1) for x in spot_prices_list])
    index = np.argmax(np.array([abs(x - 1) for x in spot_prices_list]))
    if index == 0:
        slippage = price_calcs.getSlippage(invariant, attack_balance, 1000000*1e18, [0,1])
    elif index == 1: 
        slippage = price_calcs.getSlippage(invariant, attack_balance, 1000000*1e18, [0,2])
    elif index == 2: 
        slippage = price_calcs.getSlippage(invariant, attack_balance, 1000000*1e18, [2,1])
    print("Max spot price deviation: ", 100*max_spot_deviation)
    print("Corresponding slippage: ", slippage)


#Try to find an amount to swap that would break the peg 

#Read by the attack contract from Compound
rates = [210610623344836502016616268, 215836695449259000000000000, 1000000000000000000000000000000]
#Read from Etherscan for the USDT pool
fee = 4000000

iteration = 0

while True: 
    #Current amounts of cDAI, cUSDC and USDT in the pool and conversion into DAI and USDC amounts
    cdai = 1497583531010282
    cusdc = 3258032451817647
    usdt = 40550284699
    dai = cdai * rates[0] // PRECISION
    usdc = cusdc * rates[1] // PRECISION
    usdt = usdt

    #In the USDT pool, the respective positions of the tokens are DAI, USDC, USDT
    current_values = [cdai, cusdc, usdt]
    current_values_underlying = [dai, usdc, usdt * rates[2] // PRECISION]
    ###################################################################################
    #######                             TO FIX                                  ####### 
    ###################################################################################
    # D calculation doesn't work with the numbers given by reading the contract 
    # on Etherscan, but works with the numbers below:
    # current_values_underlying = [int(351794.69*10**18),int(689185.73*10**18),int(382505.53*10**18)]
    ###################################################################################

    #Get D for the current pool composition NEEDS TO BE CONVERTED IN UNDERLYING FIRST
    D = solver.get_D(current_values_underlying, amp)
    #Check that we get 0
    invariant = lambda x : USDTpool(x, amp, D)

    if (invariant(current_values_underlying) != 0):
        print(current_values_underlying)
        print("D calculation failed!", invariant(current_values_underlying))
        break

    #DAI test
    print("Iteration ", iteration)
    iteration+=1
    #Choose a random amount of cDAI to swap between 1% and 10% of the pool holdings 
    amount_dai_in_ctoken = randint(cdai//100, cdai//10)
    #Convert that in the corresponding amount of DAI using the rates function, same as in the _xp() fucntion
    amount_dai_in_underlying = amount_dai_in_ctoken*rates[0] // PRECISION
    #Check the amount of cUSDC calculated out for that amount in

    amount_usdc_out_ctokens = solver._exchange(0, 1, current_values, amount_dai_in_ctoken, rates, fee, amp)
    
    ###################################################################################
    #######                             TO FIX                                  ####### 
    ###################################################################################
    # Even if the D calculation works, the iterations fail at the 5th step because of 
    # ZeroDivisionError: integer division or modulo by zero. Why? Need to investigate.
    ###################################################################################

    #Convert to the corresponding amount of USDC
    amount_usdc_out_underlying = amount_usdc_out_ctokens*rates[1] // PRECISION
    #If we find something that gives us an effective price of more than 1.05, print it 
    if amount_usdc_out_underlying > 1.05*amount_dai_in_underlying:
        print("Solution found, swap DAI for USDC")
        print("Amount to swap: ", amount_dai_in_underlying)
        print("Profit: ", (amount_usdc_out_underlying - amount_dai_in_underlying)//PRECISION, " USD")
        print("...")

    #To adapt for USDC and USDT
