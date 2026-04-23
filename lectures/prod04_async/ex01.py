import asyncio
import time

def sync_sleep(n):
  print("sync hello")
  time.sleep(n)
  print("sync bye")

async def async_sleep(n):
  print("async hello")
  await asyncio.sleep(n)
  print("async bye")


if __name__ == "sync":
  start = time.time()
  sync_sleep(1)
  sync_sleep(2)
  end = time.time()
  print(round(end - start, 3))

async def main():
  start = time.time()
  task_1 = asyncio.create_task(async_sleep(1))
  task_2 = asyncio.create_task(async_sleep(2))
  await task_1
  await task_2
  end = time.time()
  print(round(end - start, 3))

if __name__ == "__main__":
  asyncio.run(main())
