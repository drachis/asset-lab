import sys, os, pathlib
import socket
import time
import opencue
from opencue.exception import EntityNotFoundException
import asyncio
from outline import Outline
from outline.modules.shell import Shell

if len(sys.argv) != 2:
    print("Usage: python -m farm.opencue_submit <path-to-stage>")
    sys.exit(1)

stage_path = pathlib.Path(sys.argv[1])

if not stage_path.exists():
    print(f"Error: path '{stage_path}' does not exist.")
    sys.exit(1)
elif stage_path.is_file() and stage_path.stat().st_size == 0:
    print(f"Error: file '{stage_path}' is empty.")
    sys.exit(1)
elif stage_path.is_dir() and not any(stage_path.iterdir()):
    print(f"Error: directory '{stage_path}' is empty.")
    sys.exit(1)

stage = stage_path.resolve()
timestamp = time.strftime("%Y%m%d_%H%M%S")
hostname = socket.gethostname().split('.')[0]  # Get short hostname
job_name = f"AssetLab_{hostname}_{timestamp}_{stage.stem}"

ol = Outline(job_name)
layer = Shell(
    "convert",
    command=f"hython worker/convert_to_usd.py {stage.parent} out/usd"
)
ol.add_layer(layer)

import outline.cuerun

async def main():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, outline.cuerun.launch, ol)
    jobs = result if isinstance(result, list) else [result]
    job_ids = [job.id() for job in jobs]
    print(f"SUBMITTED {job_name} (IDs: {', '.join(job_ids)})")
    await asyncio.gather(*(monitor_job(jid) for jid in job_ids))
async def monitor_job(job_id):
    loop = asyncio.get_running_loop()
    while True:
        try:
            job = await loop.run_in_executor(None, opencue.api.findJob, job_id)
        except EntityNotFoundException:
            print(f"Error: Job {job_id} not found. Stopping monitor.")
            return
        state = job.state().name
        print(f"Job {job_id} state = {state}")
        if state in ('COMPLETE', 'FAILED', 'KILLED'):
            print(f"Final state: {state}")
            return
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())

