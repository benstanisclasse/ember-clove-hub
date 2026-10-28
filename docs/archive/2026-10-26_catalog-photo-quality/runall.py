import subprocess, sys, concurrent.futures as cf
T = r"C:\Users\Administrator\AppData\Local\Temp\ec_q"
args = [l.strip() for l in open(T + r"\tool\args.txt") if l.strip()]
chunks = [args[i:i+25] for i in range(0, len(args), 25)]
def run(c):
    r = subprocess.run([sys.executable, "-I", T + r"\tool\q.py", T + r"\all"] + c, capture_output=True, text=True, cwd=T)
    return r.stdout, r.stderr
out = open(T + r"\tool\scores.tsv", "w")
with cf.ThreadPoolExecutor(8) as ex:
    for so, se in ex.map(run, chunks):
        out.write(so)
        if se.strip(): print("ERR", se[-500:])
out.close()
print(sum(1 for _ in open(T + r"\tool\scores.tsv")))
