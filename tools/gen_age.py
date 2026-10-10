import random
def age_batch(rng, lo=7, hi=12, n_lo=4, n_hi=7):
    n=rng.randint(n_lo,n_hi); ids=[chr(65+i) for i in range(n)]
    parts=[]
    for pid in ids:
        c=rng.choice([0,0,0,3,5,10,12,20]); parts.append({"id":pid,"collateral":c,"reserve":rng.choice([0,0,c//2,c]),"ceiling":c+rng.choice([0,5,10,1000,1000])})
    pays=[]; 
    for k in range(rng.randint(lo,hi)):
        if pays and rng.random()<0.6:
            d=rng.choice(pays)["creditor"]; c=rng.choice([x for x in ids if x!=d])
        else: d,c=rng.sample(ids,2)
        pays.append({"id":rng.choice(["p","q"])+f"{k:02d}","debtor":d,"creditor":c,"amount":rng.choice([2,3,5,6,8,10,12,15,20]),"priority":rng.choice([0,0,1,1,2,2,2]),"seq":rng.randint(0,9)})
    return {"participants":parts,"payments":pays}
