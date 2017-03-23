'''
家庭成员从全国各地到纽约会面，希望同一天到达，并在同一天离开
而且他们想搭乘相同的交通工具往返飞机场
目标：
总票价
总的候机时间
总的飞行时间
'''

import time
import random
import math

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]
# Laguardia Airport
destination = 'LGA'

# 从文件中读取航班信息
flights = {}
for line in open('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')

    flights.setdefault((origin, dest), [])
    flights[(origin, dest)].append((depart, arrive, int(price)))

print(flights)


def getminutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]


def printschedule(r):
    for d in range(int(len(r) / 2)):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin, destination)][int(r[d])]
        ret = flights[(destination, origin)][int(r[d + 1])]
        print('%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin,
                                                      out[0], out[1], out[2],
                                                      ret[0], ret[1], ret[2]))


def schedulecost(sol):
    '''成本函数，返回值越大，表示该方案越差
    参数：
    sol：保存每个人乘坐飞到纽约和飞离纽约的航班顺序，长度是人数的两倍'''
    totalprice = 0
    latestarrival = 0
    earliestdep = 24 * 60

    for d in range(int(len(sol) / 2)):
        # Get the inbound and outbound flights
        origin = people[d][1]
        try:
            outbound = flights[(origin, destination)][int(sol[d])]

            returnf = flights[(destination, origin)][int(sol[d + 1])]
        except Exception as ex:
            print('Exception:', ex)
            print('d=', d)
            print('except:', sol[d], sol[d + 1])

        # Total price is the price of all outbound and return flights
        totalprice += outbound[2]
        totalprice += returnf[2]

        # Track the latest arrival and earliest departure
        if latestarrival < getminutes(outbound[1]): latestarrival = getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]): earliestdep = getminutes(returnf[0])

    # Every person must wait at the airport until the latest person arrives.
    # They also must arrive at the same time and wait for their flights.
    totalwait = 0
    for d in range(int(len(sol) / 2)):
        origin = people[d][1]
        outbound = flights[(origin, destination)][int(sol[d])]
        returnf = flights[(destination, origin)][int(sol[d + 1])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0]) - earliestdep

    # Does this solution require an extra day of car rental? That'll be $50!

    # 最晚到达时间（租车时间)比 最早出发时间（还车时间)晚，则表示租车时间超过一天，需要额外交50租金
    # 书中注释理解错误？
    if latestarrival > earliestdep: totalprice += 50
    # print(latestarrival,earliestdep)

    return totalprice + totalwait
#记录优化算法时间装饰器
def timingOptimizer(optimizer):
    def newOptimizer(*args, **kwargs):
        begintime=time.clock()
        #print(begintime)
        sol=optimizer(*args, **kwargs)
        endtime=time.clock()
        #print(endtime)
        seconds=endtime-begintime
        #时间格式化
        #http://stackoverflow.com/questions/775049/python-time-seconds-to-hms
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        print ("Seconds Elapsed: %f Time Elapsed: %d:%02d:%02d" % (endtime-begintime,h, m, s))
        return sol
    return newOptimizer
# 随机搜索
# domain表示每个人的可选航班数，往返均有10班，则为(0,9)
# costf 为成本函数
# 随机构造一种方案，随机1000次，得到1000次中cost最小的
# 次数越多，就更可能获得更优的方案
@timingOptimizer
def randomoptimize(domain, costf):
    best = 999999999
    bestr = None
    for x in range(0, 1000):
        # Create a random solution
        r = [float(random.randint(domain[i][0], domain[i][1]))
             for i in range(len(domain))]
        # print('#',x,'>>',r)
        # Get the cost
        cost = costf(r)

        # Compare it to the best one so far
        if cost < best:
            best = cost
            bestr = r
    print('Optimizer: randomoptimize')
    print('bestCost:', best)
    print('bestSolution', bestr)
    return bestr


# 爬山法，有可能只能得到局部最小解
@timingOptimizer
def hillclimb(domain, costf):
    # Create a random solution
    sol = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]
    print('Seed Sol:', sol)
    # Main loop
    while 1:
        # Create list of neighboring solutions
        neighbors = []

        for j in range(len(domain)):
            # One away in each direction
            #书中代码无误，
            #但是网站提供源码把下面的+1和-1写反了
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j + 1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j + 1:])
        #print(neighbors)
        # See what the best solution amongst the neighbors is
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]
        # If there's no improvement, then we've reached the top
        if best == current:
            break
    print('Optimizer: hillclimb')
    print('bestCost:', best)
    print('bestSolution', sol)
    return sol

#模拟退火算法
#温度T的初始值设置问题。
#温度T的初始值设置是影响模拟退火算法全局搜索性能的重要因素之一、初始温度高，则搜索到全局最优解的可能性大，但因此要花费大量的计算时间；反之，则可节约计算时间，但全局搜索性能可能受到影响。实际应用过程中，初始温度一般需要依据实验结果进行若干次调整。
#退火速度问题。
#模拟退火算法的全局搜索性能也与退火速度密切相关。一般来说，同一温度下的“充分”搜索(退火)是相当必要的，但这需要计算时间。实际应用中，要针对具体问题的性质和特征设置合理的退火平衡条件。
@timingOptimizer
def annealingoptimize(domain, costf, T=10000.0, cool=0.95, step=1):
    '''
    #模拟退火算法
    温度T的初始值设置问题:
        温度T的初始值设置是影响模拟退火算法全局搜索性能的重要因素之一、初始温度高，则搜索到全局最优解的可能性大，但因此要花费大量的计算时间；
        反之，则可节约计算时间，但全局搜索性能可能受到影响。实际应用过程中，初始温度一般需要依据实验结果进行若干次调整。
    退火速度问题:
        模拟退火算法的全局搜索性能也与退火速度密切相关。
        一般来说，同一温度下的“充分”搜索(退火)是相当必要的，但这需要计算时间。
        实际应用中，要针对具体问题的性质和特征设置合理的退火平衡条件。
    :param domain:
    :param costf:
    :param T:
    :param cool: 0 ~ 1
    :param step:
    :return:
    '''
    # 随机初始化值
    vec = [float(random.randint(domain[i][0], domain[i][1]))
           for i in range(len(domain))]
    steps=[-1,1]
    while T > 0.1:
        # 随机选择一个索引值
        i = random.randint(0, len(domain) - 1)
        # 选择一个改变索引值的方向
        #原书取随机数会获取到0，而且几率为1/3的退火？？
        # 等于浪费了几乎1/3的计算，改为只取-1 或者 1
        #dir = random.randint(-step, step)
        dir=steps[random.randint(0,1)]
        # 创建一个代表解题的新列表，改变其中一个值
        # 此处使用的深复制
        vecb = vec[:]
        # 修改新解题列表中的随机索引处的解
        vecb[i] += dir
        # 避免修改后的解超过解的上限和下限
        if vecb[i] < domain[i][0]:
            vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]:
            vecb[i] = domain[i][1]

        # 计算当前成本和新的成本
        ea = costf(vec)
        eb = costf(vecb)

        # 是更好的解吗？或者趋向最优解的可能临界解吗？
        if (eb < ea or random.random() < pow(math.e, -(eb - ea) / T)):
            vec = vecb

        # 降低温度
        T = T * cool
    print('Optimizer: annealingoptimize')
    print('bestCost:', eb)
    print('bestSolution', vec)
    return vec



# s保存每个人乘坐飞到纽约和飞离纽约的航班顺序，长度是人数的两倍
# s=[1,4,3,2,7,3,6,3,2,4,5,3]
# printschedule(s)
# print(schedulecost(s))

# domain保存每个人乘坐飞到纽约和飞离纽约的航班顺序，长度是人数的两倍
domain = [(0, 9)] * (len(people) * 2)

s = randomoptimize(domain, schedulecost)
schedulecost(s)
printschedule(s)

s = hillclimb(domain, schedulecost)
printschedule(s)

s = annealingoptimize(domain,schedulecost,T=10000.0,cool=0.99)
printschedule(s)
