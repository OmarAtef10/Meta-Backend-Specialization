# It's not in the course but its from a google test so i thought that I'd Just add it

def solution(i):
    primeNums = getPrimes()

    return primeNums[i:i + 5]


def getPrimes():
    primes = ''
    prev = 2
    while len(primes) < 10005:

        primes += str(prev)
        prev += 1
        while not primeGen(prev):
            prev += 1
    return primes


def primeGen(n):
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


print(solution(0))
