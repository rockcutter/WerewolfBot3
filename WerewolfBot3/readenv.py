from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
EXECUTEDID = int(os.getenv("EXECUTED_ID"))
KILLEDID = int(os.getenv("KILLED_ID"))

