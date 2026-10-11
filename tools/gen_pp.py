import random
def pp_batch(rng, amt_hi=3000, n_lo=2, n_hi=5, k_lo=2, k_hi=7):
    n=rng.randint(n_lo,n_hi); ids=[chr(65+i) for i in range(n)]
    parts=[]
    for pid in ids:
        c=rng.choice([0,3,5,8,10,12,17,25,40]); r=rng.choice([0,c//2,c,max(0,c-5),max(0,c-3)])
        parts.append({"id":pid,"collateral":c,"reserve":min(r,c),"ceiling":c+rng.choice([0,5,12,30,100,10**6,10**6])})
    pays=[]
    for k in range(rng.randint(k_lo,k_hi)):
        d,c=rng.sample(ids,2)
        pays.append({"id":f"p{k:02d}","debtor":d,"creditor":c,"amount":rng.choice([rng.randint(1,30),rng.randint(50,amt_hi),rng.randint(50,amt_hi)]),"priority":rng.choice([2,2,2,2,1,0]),"seq":rng.randint(0,5)})
    return {"participants":parts,"payments":pays}
