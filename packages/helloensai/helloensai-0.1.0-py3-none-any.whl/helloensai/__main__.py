import os
world = os.getenv("WORLD")
if world is None:
    print("hello ENSAI, change WORLD environnement variable to change this message")
else:
    print(f"hello {world}, 👏👏")

