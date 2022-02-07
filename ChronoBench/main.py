import hashlib
from random import choice, randint, randbytes
from time import perf_counter, sleep
import multiprocessing as mp
import concurrent.futures
from shutil import disk_usage
import psutil
import platform
from datetime import datetime

def get_size(inp, suffix='B'):
    inc = 1024
    for i in ['', 'K', 'M', 'G', 'T', 'P']:
        if inp < inc:
            return f'{inp:.2f}{i}{suffix}'
        inp /= inc

print('-'*30, 'System Information', '-'*30)
uname = platform.uname()
print(f'System: {uname.system}')
print(f'Node: {uname.node}')
print(f'Release: {uname.release}')
print(f'Version: {uname.version}')
print(f'Architecture: {uname.machine}')
print(f'Platform: {platform.platform()}')

print('-'*35, 'CPU Info', '-'*35)
print(f'Processor: {uname.processor}')
print('Physical cores:', psutil.cpu_count(logical=False))
print('Threads:', psutil.cpu_count(logical=True))
cpufreq = psutil.cpu_freq()
print(f'Base Clock: {int(cpufreq.current)}Mhz')

print('-'*30, 'Memory Information', '-'*30)

svmem = psutil.virtual_memory()
print(f'Total: {get_size(svmem.total)}')
print(f'Available: {get_size(svmem.available)}')
print(f'Used: {get_size(svmem.used)}')

swap = psutil.swap_memory()
if swap.total:
    print(f'Swap total: {get_size(swap.total)}')
    print(f'Swap free: {get_size(swap.free)}')
    print(f'Swap used: {get_size(swap.used)}')
else:
    print('No active swap memory found')
    
print('-'*30, 'Drive Information', '-'*31)
print(f'Allocated: {get_size(disk_usage("/")[0])}')
print(f'Free: {get_size(disk_usage("/")[2])}')
print(f'Used: {get_size(disk_usage("/")[1])}')

difficulty = 73
hashrate = 0

if not difficulty:
    difficulty = int(input('difficulty: '))

def rollNum(length=64):
    res = ''
    hexDump = [i for i in '01234567890abcdef']
    for i in range(length):
        res += choice(hexDump)
        
    return res
    
def check(att, target, verbose=False):
    
    if verbose:
        print('target:', target)
    
    if int(att, 16) < target:
        return True
    else:
        return False

def ssdTest():
    writes = 0
    reads = 0
    for i in range(2000):
        with open('ssdBench.txt', 'wb') as writeBench:
            header = randbytes(1000000)
            writeBench.write(b'')
            start = perf_counter()
            writeBench.write(header)
            end = perf_counter()
            
            writes += 1000000/(end-start)
            writeBench.close()
        if i % 200 == 0:
            print(f'ssd test progress [{("="*int(i/200))+(" "*(10-int(i/200)))}]')

        with open('ssdBench.txt', 'rb', 1000000) as readBench:
            start = perf_counter()
            readBench.read(1000000)
            #readBench.getvalue()
            end = perf_counter()
            
            reads += 1000000/(end-start)
            readBench.close()
    
    print(f'ssd test progress [{("="*10)}]')
    return (writes, reads)

print('-'*35, 'SSD TEST', '-'*35)
ssd = ssdTest()

def main(minerNum):
    verbose = False
    att = rollNum()
    nonce = 0
    
    target = '1'
    for i in range(difficulty-1):
        target += '0'
        
    target = int(target)

    #print('generating header')
    header = hashlib.sha256(rollNum(1000000).encode('utf-8')).hexdigest()
    #print('started node number', minerNum)

    start = perf_counter()

    while not check(att, target):
        nonce += 1
        if verbose:
            print('testing attempt:', att)
        att = hashlib.sha256(str(int(header, 16)+nonce)[2:].encode('utf-8')).hexdigest()
    
    end = perf_counter()

    return (nonce/(end-start))/1000

hashrate = 0
history = []
mcHigh = -1
mcLow = -1

print('-'*31, 'MULTI CORE TEST', '-'*32)

for i in range(10):
    print(f'multi core test progress [{("="*i)+(" "*(10-i))}]')
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        nodes = [executor.submit(main, i) for i in range(0, psutil.cpu_count(logical=True))]
    
    for i in nodes:
        res = i.result()
        hashrate += res
        history.append(res)
    #print('done with', hashrate, 'KHashes/second')
    
print(f'multi core test progress [{"="*10}]')

for i in history:
    if i < mcLow or mcLow == -1:
        mcLow = i
    if i > mcHigh:
        mcHigh = i

mcScore = hashrate/10

def main():
    verbose = False
    att = rollNum()
    nonce = 0
    
    target = '1'
    for i in range(difficulty-1):
        target += '0'
        
    target = int(target)

    header = hashlib.sha256(rollNum(1000000).encode('utf-8')).hexdigest()
    #print('starting node')

    start = perf_counter()

    while not check(att, target):
        
        nonce += 1
        if verbose:
            print('testing attempt:', att)
        att = hashlib.sha256(str(int(header, 16)+nonce)[2:].encode('utf-8')).hexdigest()
    
    end = perf_counter()
    
    return (nonce/(end-start))/1000

hashrate = 0

print('-'*30, 'SINGLE CORE TEST', '-'*30)

for i in range(10):
    print(f'single core test progress [{("="*i)+(" "*(10-i))}]')
    hashrate += main()
    
print(f'single core test progress [{"="*10}]')
    
scScore = hashrate/10

print('\n', '-'*35, 'RESULT', '-'*35, '\n')
print('Single Core Score:', round(scScore, 2))
print('Multi Core Score:', round(mcScore, 2), '\nMulti Core High:', round(mcHigh*4, 2), '\nMulti Core Low', round(mcLow*4, 2))
print(f'Ssd Read: {get_size(ssd[1]/2000)}/second')
print(f'Ssd Write: {get_size(ssd[0]/2000)}/second\n')