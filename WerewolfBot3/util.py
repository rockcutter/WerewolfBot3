import discord
class Client:
    client = None

cl = Client()

def Init(argclient):
    cl.client = argclient
    return

async def WaitforInteger():
    while(True):
        message = await cl.client.wait_for("message")
        if(IsInt(message.content)):
            return int(message.content)
    return

def IsInt(argStr):
    try:
        int(argStr)
    except ValueError:
        return False
    else:
        return True