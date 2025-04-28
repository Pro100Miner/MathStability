import math



def get(a, b, ep=100):
    ep1 = 1000


    def number(eps, a, a1):
        s = 1
        for j in range(2, eps+1):
            if a[j] * a[j - 1] > 0:
                s += 1
                if s >= 3:
                    if a1[j] > 0:
                        return j - 2
                    else:
                        s = 2
            else:
                s = 1
        return 0


    u = [0.0] * ep1
    u1 = [0.0] * ep1
    v = [0.0] * ep1
    v1 = [0.0] * ep1
    f = [0.0] * ep1
    g = [0.0] * ep1
    p = [0.0] * ep1
    p1 = [0.0] * ep1
    r = [0.0] * ep1
    r1 = [0.0] * ep1

    u[1] = 1.0
    u[2] = 1 + (b ** 2) / (2 * a * (1 - a))
    p[1] = 0.0
    p[2] = 0.0

    for i in range(2, round(ep / 2)):
        u[i+1] = u[i] - (b ** 2) * u[i - 1] / (4 * (i ** 2 - a) * \
        ((i - 1) ** 2 - a))
        #print(f'u={i} {u[i+1]}')
        p[i+1] = abs(u[i+1]) - (b ** 2) * abs(u[i]) / (12 * (i - 1) ** 3)

    m = number(round(ep / 2), u, p)
    u1[1] = 1.0
    u1[2] = 1 - (b ** 2) / (4 * (1 - a) * (4 - a))
    r[1] = 0.0
    r[2] = 0.0

    for i in range(3, round(ep / 2)+1):
        u1[i] = u1[i - 1] - (b ** 2) * u1[i - 2] / (4 * (i ** 2 - a) * \
        ((i - 1) ** 2 - a))
        #print(f'u1={i} {u1[i]}')
        r[i] = abs(u1[i]) - (b ** 2) * abs(u1[i - 1]) / (12 * (i - 1) ** 3)

    n = number(round(ep / 2), u1, r)
    d = max(m, n)
    f[1] = 1.0
    f[2] = u[2]

    for i in range(2, d+1):
        f[2 * i - 1] = u[i+1] * u1[i - 1]
        f[2 * i] = u[i+1] * u1[i]
    c1 = sum(1 for i in range(1, 2 * d) if f[i] * f[i + 1] < 0)

    v[1] = 1.0
    v[2] = (b ** 2) / ((9.0 / 2.0 - 2 * a) * (0.5 - 2 * a - b))
    p1[1] = 0.0
    p1[2] = 0.0
    for i in range(2, round(ep / 2)):
        v[i+1] = v[i] - (b ** 2) * v[i - 1] / (((2 * i + 1) ** 2 / 2 - 2 * a) \
        * ((2 * i - 1) ** 2 / 2 - 2 * a))
        #print(f'v={i} {v[i+1]}')
        p1[i+1] = abs(v[i+1]) - 2 * (b ** 2) * abs(v[i]) / (3 * (2 * i - 3) ** 3)

    m1 = number(round(ep / 2), v, p1)
    v1[1] = 1.0
    v1[2] = 1 - (b ** 2) / ((9.0 / 2.0 - 2 * a) * (0.5 - 2 * a + b))
    r1[1] = 0.0
    r1[2] = 0.0
    for i in range(2, round(ep / 2)):
        v1[i+1] = v1[i] - (b ** 2) * v1[i - 1] / \
        (((2 * i + 1) ** 2 / 2 - 2 * a) * ((2 * i - 1) ** 2 / 2 - 2 * a))
        #print(f'v1={i} {v1[i+1]}')
        r1[i+1] = abs(v1[i+1]) - 2 * (b ** 2) * abs(v1[i]) / \
        (3 * (2 * i - 3) ** 3)

    n1 = number(round(ep / 2), v, p1)
    d1 = max(m1, n1)
    g[1] = 1.0

    for i in range(1, d1+1):
        g[2 * i] = v[i+1] * v1[i]
        g[2 * i + 1] = v[i+1] * v1[i + 1]

    c = sum(1 for i in range(1, 2 * d1+1) if g[i] * g[i + 1] < 0)
    c2 = c1 - c

    #print(f'c1 = {c1} c = {c}')
    if c2 == -1 or c2 == 1:
        return True, c
    elif c2 == 0:
        return False, c1

