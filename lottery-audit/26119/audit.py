"""DLT 26119 exact 10-ticket payoff audit. Requires numpy. Python 3.10+."""
import itertools, math, json, collections
from pathlib import Path
import numpy as np
A="""03 04 10 14 26|09 12
03 09 10 21 22|01 05
02 05 19 28 34|06 07
11 16 17 18 32|06 11
06 07 17 20 25|05 07
12 22 24 27 33|04 12
08 14 28 30 31|04 08
01 23 27 29 31|02 11
13 21 25 26 34|03 10
15 18 20 33 35|02 10"""
B="""03 10 14 21 26|07 09
03 10 14 26 33|07 09
03 10 21 26 33|07 09
03 14 21 26 33|07 09
10 14 21 26 33|07 09
03 10 14 21 26|09 12
11 16 17 18 32|06 11
06 07 17 20 25|05 07
12 22 24 27 33|04 12
08 14 28 30 31|04 08"""
def parse(s):
 return [(tuple(map(int,x.split())),tuple(map(int,y.split()))) for x,y in (z.split('|') for z in s.splitlines())]
def dantuo(front_d,front_t,back_d,back_t):
 return [(tuple(sorted((front_d,)+a)),tuple(sorted((back_d,b)))) for a in itertools.combinations(front_t,4) for b in back_t]
C=dantuo(26,(3,10,14,21,33),9,(7,12))
tier=np.zeros((6,3),dtype=np.uint8)
for f,b,t in [(5,2,1),(5,1,2),(5,0,3),(4,2,3),(4,1,4),(4,0,5),(3,2,5),(3,1,6),(2,2,6),(3,0,7),(2,1,7),(1,2,7),(0,2,7)]: tier[f,b]=t
low=np.array([0,0,0,5000,300,150,15,5])
high=np.array([0,0,0,6666,380,200,18,7])
N=math.comb(35,5)*math.comb(12,2)
assert N==21425712
front=np.array(list(itertools.combinations(range(1,36),5)),dtype=np.uint8)
back=np.array(list(itertools.combinations(range(1,13),2)),dtype=np.uint8)
def audit(tickets):
 assert len(tickets)==len(set(tickets))==10
 for f,b in tickets:
  assert len(f)==len(set(f))==5 and all(1<=x<=35 for x in f)
  assert len(b)==len(set(b))==2 and all(1<=x<=12 for x in b)
 fmatch=[np.isin(front,t[0]).sum(axis=1).astype(np.uint8) for t in tickets]
 bmatch=[np.isin(back,t[1]).sum(axis=1).astype(np.uint8) for t in tickets]
 c=collections.Counter(); sumlo=sumhi=0
 for j in range(66):
  lo=np.zeros(len(front),dtype=np.int64);hi=lo.copy()
  win=np.zeros(len(front),dtype=np.uint8);fixed=win.copy();g56=win.copy()
  for i in range(10):
   g=tier[fmatch[i],bmatch[i][j]]
   lo+=low[g];hi+=high[g]
   win+=(g!=0);fixed+=(g>=3);g56+=(g==5)|(g==6)
  c['any']+=np.count_nonzero(win);c['fixed_2plus']+=np.count_nonzero(fixed>=2)
  c['fixed_3plus']+=np.count_nonzero(fixed>=3)
  c['any_56']+=np.count_nonzero(g56)
  c['low_ge_20']+=np.count_nonzero(lo>=20);c['high_ge_20']+=np.count_nonzero(hi>=20)
  c['high_ge_89']+=np.count_nonzero(hi>=89)
  sumlo+=int(lo.sum());sumhi+=int(hi.sum())
 return {'numerators':{k:int(v) for k,v in c.items()},'probabilities':{k:float(v/N) for k,v in c.items()},'expected_fixed_low':sumlo/N,'expected_fixed_high':sumhi/N}
result={name:audit(t) for name,t in [('V5',parse(A)),('V6',parse(B)),('dantuo',C)]}
photo=dantuo(14,(3,10,15,26,33),9,(4,7))
outcome=(set((3,24,25,26,35)),set((7,9)))
prizes=[int(high[tier[len(outcome[0]&set(f)),len(outcome[1]&set(b))]]) for f,b in photo]
assert sum(prizes)==89 and sorted(prizes)==[0,0,7,7,7,7,7,18,18,18]
assert len({round(x['expected_fixed_low'],10) for x in result.values()})==1
assert len({round(x['expected_fixed_high'],10) for x in result.values()})==1
report={'total_outcomes':N,'photo_26110_payout':sum(prizes),'portfolios':result}
output_path=Path(__file__).with_name('dlt_26119_audit_results.json')
output_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
