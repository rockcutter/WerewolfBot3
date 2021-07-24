import discord
import random
import readenv
import rolenamelist
import util

class Status(object):
    client = None
    channel = None
    killedPlayer = None
    formerExecutedIsBlack = False
    gameStarted = False
    day = 0
    night = False

    #特定ロール
    exeRole = None
    killedRole = None
    
class VoteStatus:
    voteMode = False
    voteCount = 0
    votedPlayerList = []
    targetPlayerDict = {}

class AbilityStatus:
    abilityMode = False
    abilityCount = 0 #アビリティ持ちのカウント
    usedPlayerList = []
    usedPlayerCount = 0
    defencedPlayerList = []
    killPlayerList = []

st = Status()
vstatus = VoteStatus()
abistatus = AbilityStatus()

def Init(client):
    st.client = client
    return

def InitStatus():
    st.client = None
    st.channel = None
    st.killedPlayer = None
    st.formerExecutedIsBlack = False
    st.gameStarted = False
    st.day = 1
    st.night = False
    return

def InitVoteStatus():
    vstatus.voteMode = False
    vstatus.voteCount = 0
    vstatus.votedPlayerList = []
    vstatus.targetPlayerDict = {}
    return

def InitAbilityStatus():
    abistatus.abilityMode = False
    abistatus.abilityCount = 0 
    abistatus.usedPlayerList = []
    abistatus.usedPlayerCount = 0
    abistatus.defencedPlayerList = []
    abistatus.killPlayerList = []
    return

#ゲームスタート処理
async def StartGame(message, playerList, roleCountDict):
    st.channel = message.channel
    st.gameStarted = True

    GiveRoles(playerList, roleCountDict)
    ApplyRole(message)
    await TellRole(playerList)
    await message.channel.send("皆さんの村の中には人狼が紛れ込んでいます。\n村人側は人狼を処刑できれば勝利、人狼側は人間と人狼の数が同数になると勝利です。")
    await Daytime(playerList)
    return

def GameStarted():
    return st.gameStarted

def IsVoteMode():
    return vstatus.voteMode

def IsAbilityMode():
    return abistatus.abilityMode

def GiveRoles(playerList, roleCountDict):
    tempNameList = []
    for roleName in roleCountDict.keys():
        for i in range(roleCountDict[roleName]):
            tempNameList.append(roleName)
    random.shuffle(tempNameList)
    print(tempNameList)
    for plObj in playerList:
        plObj.roleName = tempNameList.pop(0)
    return

def ApplyRole(message):
    st.exeRole = message.guild.get_role(readenv.EXECUTEDID)
    st.killedRole = message.guild.get_role(readenv.KILLEDID)
    return

async def TellRole(playerList):
    for plClass in playerList:
        await plClass.playerObj.send("あなたの役職は" + plClass.roleName + "です")
        if(plClass.roleName == rolenamelist.WEREWOLF):
            await plClass.playerObj.send("人狼のプレイヤーは以下の通りです")
            for pl in RolePlayerSearch(playerList, rolenamelist.WEREWOLF):
                await plClass.playerObj.send(str(pl))
    return

def RolePlayerSearch(playerList, roleName):
    retList = []
    for plClass in playerList:
        if(plClass.roleName == roleName):
            retList.append(plClass.playerObj)
    return retList

def PlayerSearch(playerList, playerObj):
    for plClass in playerList:
        if(plClass.playerObj == playerObj):
            return plClass
    return

async def Daytime(playerList):
    st.day += 1;

    await st.channel.send(str(st.day) + "日目朝")
    if(st.killedPlayer != None):
        await st.channel.send(str(st.killedPlayer.playerObj) + "が無残な死体となって発見されました")
    else:
        await st.channel.send("今朝は死体は見つかりませんでした")
    if(await WinnerCheck(playerList)):
        return

    #霊媒能力
    for pl in RolePlayerSearch(playerList,rolenamelist.SHAMAN):
        if(st.day == 1):
            continue
        if(st.formerExecutedIsBlack):
            await pl.send("昨日処刑されたプレイヤーは黒です")
        else:
            await pl.send("昨日処刑されたプレイヤーは白です")


    await st.channel.send("誰が人狼なのかを話し合い、本日処刑する人を決めてください。```!vote [番号]```コマンドで投票できます。```!list```コマンドでプレイヤーの番号が確認できます")
    vstatus.voteMode = True
    return

async def Vote(message, playerList):
    splitedList = message.content.split()
    if(len(splitedList) < 2): return
    if(not util.IsInt(splitedList[1])): return
    if(message.author in vstatus.votedPlayerList):return
    splitedList[1] = int(splitedList[1])
    if(len(playerList) <= splitedList[1]): return

    vstatus.votedPlayerList.append(message.author)
    vstatus.voteCount += 1
    if(playerList[splitedList[1]] in vstatus.targetPlayerDict):
        vstatus.targetPlayerDict[playerList[splitedList[1]]] += 1
    else:
        vstatus.targetPlayerDict[playerList[splitedList[1]]] = 1
    await message.channel.send(str(playerList[splitedList[1]].playerObj) + "に投票しました")

    #投票終了処理
    if(vstatus.voteCount >= len(playerList)):
        maxCount = 0
        executedPlayer = None
        for pl in vstatus.targetPlayerDict.keys():
            if (vstatus.targetPlayerDict[pl] > maxCount):
                maxCount = vstatus.targetPlayerDict[pl]
                executedPlayer = pl
                continue
            if(vstatus.targetPlayerDict[pl] == maxCount):
                await st.channel.send("同票のプレイヤーがいるため、処刑は行われませんでした")
                st.exeRole = None
                InitVoteStatus()
                await Night(playerList)
                return
        await Execute(executedPlayer, playerList)
        await st.channel.send("全員の投票が終わり、票が集計されました。\n`" + str(executedPlayer.playerObj) + "`が処刑されました")
        InitVoteStatus()
        #夜処理へ
        await Night(playerList)
    return
    
async def Execute(playerClass, playerList):
    playerList.remove(playerClass)
    if(playerClass.roleName == rolenamelist.WEREWOLF):
        st.formerExecutedIsBlack = True
    else:
        st.formerExecutedIsBlack = False
    await playerClass.playerObj.add_roles(st.exeRole)
    return
    
async def Night(playerList):
    if(await WinnerCheck(playerList)):
        return 
    await st.channel.send(str(st.day) + "日目夜\n恐ろしい夜の時間がやってきました。\n能力持ちのプレイヤーはDMにてアクションを行ってください\nコマンドは```!action [対象のプレイヤー番号]```")

    abistatus.abilityMode = True
    return

def CountAbility(playerList):
    abistatus.abilityCount = 0
    for plClass in playerList:
        if(plClass.roleName != rolenamelist.VILLAGER and plClass.roleName != rolenamelist.SHAMAN):
            abistatus.abilityCount += 1
    return

async def Ability(playerList, message):
    CountAbility(playerList)
    bufList = message.content.split()
    if(len(bufList) < 2): return
    if(not util.IsInt(bufList[1])): return
    command = bufList[0]
    arg = int(bufList[1])

    plClass = PlayerSearch(playerList, message.author)
    if(plClass in abistatus.usedPlayerList or
       len(playerList) <= arg or
       arg < 0):
        return

    plClass = PlayerSearch(playerList, message.author)
    if(plClass.roleName == rolenamelist.FORTUNETELLER and
       playerList[arg].playerObj != plClass.playerObj
       ):
        if(playerList[arg].roleName == rolenamelist.WEREWOLF):
            await message.author.send("黒です")
            abistatus.usedPlayerCount += 1
        else:
            await message.author.send("白です")
            abistatus.usedPlayerCount += 1
        abistatus.usedPlayerList.append(plClass)
    
    if(plClass.roleName == rolenamelist.KNIGHT and
       playerList[arg].playerObj != plClass.playerObj):
        abistatus.defencedPlayerList.append(playerList[arg])
        await message.author.send("守護対象を決定しました")
        abistatus.usedPlayerList.append(plClass)
        abistatus.usedPlayerCount += 1

    if(plClass.roleName == rolenamelist.WEREWOLF and
       playerList[arg].roleName != rolenamelist.WEREWOLF):
        await message.author.send("対象を襲撃候補リストに入れました")
        abistatus.killPlayerList.append(playerList[arg])
        abistatus.usedPlayerList.append(plClass)
        abistatus.usedPlayerCount += 1

    #能力終了フェイズ
    if(abistatus.usedPlayerCount >= abistatus.abilityCount):
        random.shuffle(abistatus.killPlayerList)
        st.killedPlayer = abistatus.killPlayerList.pop()
        if(st.killedPlayer in abistatus.defencedPlayerList):
            st.killedPlayer = None
        else:
            playerList.remove(st.killedPlayer)
        InitAbilityStatus()
        await Daytime(playerList)
    return

async def WinnerCheck(playerList):
    werewolfCount = len(RolePlayerSearch(playerList, rolenamelist.WEREWOLF))
    if(werewolfCount >= len(playerList) - werewolfCount):
        await st.channel.send("村人陣営の数が人狼陣営以下になりました\n人狼陣営の勝利です")
        InitStatus()
        playerList.clear()
        return True
    if(werewolfCount == 0):
        await st.channel.send("人狼の数が0になりました\n村人陣営の勝利です")
        InitStatus()
        playerList.clear()
        return True

