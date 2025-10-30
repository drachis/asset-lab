import sys, time, concurrent.futures, pathlib, subprocess

stage = pathlib.Path(sys.argv[1])
assets = list((stage.parent/"usd").glob("*.usd"))

def fake_render(p):
    time.sleep(0.2)
    return f"OK {p.name}"

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for r in ex.map(fake_render, assets):
        print(r)
print("MOCK JOB DONE")