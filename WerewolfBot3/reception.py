import discord
import util
import Player
import ongoing

client = None

def Init(argclient):
    client = argclient
    return

async def JoinGame(message, playerList):
    for plClass in playerList:
        if(message.author == plClass.playerObj): return

    bufObj = Player.Player()
    bufObj.playerObj = message.author
    playerList.append(bufObj)
    await message.channel.send("`" + str(message.author) + "`の参加を受け付けました")
    return

async def CheckOption(message, playerList, roleCountDict):
    if(len(playerList) == 0):
        await message.channel.send("参加人数が0人です")
        return

    #役職数判定
    sum = 0
    for i in roleCountDict.values():
        sum += i
    if(len(playerList) > sum):
        await message.channel.send("参加人数 > 役職数です")
        return

    await ongoing.StartGame(message, playerList, roleCountDict)
    return

async def SetRole(message, roleCountDict):
    await message.channel.send("参加人数 < 役職数の場合、役欠けが発生します")
    for roleName in roleCountDict.keys():
        await message.channel.send("`" + roleName + "`の人数を設定してください")

        ibuf = -1
        while(ibuf < 0): ibuf = await util.WaitforInteger()
        roleCountDict[roleName] = ibuf
    await message.channel.send("役職の登録が完了しました")
    return
