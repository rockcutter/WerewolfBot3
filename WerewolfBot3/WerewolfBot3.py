import discord
import random
import readenv
import Player

import util
import reception
import ongoing
import rolenamelist
client = discord.Client()

#変数リスト
playerList = []
roleCountDict = {rolenamelist.VILLAGER: 0,
                rolenamelist.WEREWOLF: 0,
               rolenamelist.KNIGHT: 0,
              rolenamelist.FORTUNETELLER: 0,
             rolenamelist.SHAMAN: 0}

@client.event
async def on_message(message):
    if(message.content == ""): return
    if(message.content[0] != "!"): return
    buf = message.content.split()
    command = buf.pop(0)
    arg = []
    for bufStr in buf:
        arg.append(bufStr)

    #進行中のコマンド受付
    if(command == "!vote" and ongoing.IsVoteMode()): await ongoing.Vote(message, playerList)
    if(command == "!action" and ongoing.IsAbilityMode): await ongoing.Ability(playerList, message)

    #受付時のコマンド受付
    if(not ongoing.GameStarted()):
        if(message.content == "!join"): await reception.JoinGame(message, playerList)
        if(message.content == "!set"): await reception.SetRole(message, roleCountDict)
        if(message.content == "!start"):await reception.CheckOption(message,playerList,roleCountDict)

    #常時受け付けのコマンド
    if(message.content == "!list"): await ShowList(message.channel, playerList)


    #DEBUG
    if(command == "!debug"):
        await ongoing.Ability(playerList, message)
        pass
    return

async def ShowList(channel, aplayerList):
    if(len(aplayerList) == 0):
        return
    outString = ""
    i = 0
    for pl in aplayerList:
        outString += "[" + str(i) + "]" + str(pl.playerObj)
    await channel.send(outString)
    return

def main():
    util.Init(client)
    reception.Init(client)

    client.run(readenv.TOKEN)
    return 0

if (__name__ == "__main__"):
    main()