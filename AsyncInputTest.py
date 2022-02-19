# import aioconsole
# import asyncio
# 
# async def input_func():
#     while True:
#         line = await aioconsole.ainput()
#         print(line)
#     
# async def sss():
#     while True:
#         await asyncio.sleep(3)
#         print("hello")
#         
# async def main():
#     task1 = asyncio.create_task(input_func())
#     task2 = asyncio.create_task(sss())
#     await task1
#     await taks2
# 
# asyncio.run(main())

import asyncio
from concurrent.futures import ThreadPoolExecutor

async def ainput(prompt: str = ''):
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()

async def main():
    name = await ainput("What's your name? ")
    print(f"Hello, {name}!")


asyncio.run(main())