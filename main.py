#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


import requests
import discord
import os
from chart import Chart
from book import Book

chart = Chart()
book = Book()

client = discord.Client()

token = os.environ["DISCORD_TOKEN"]

verif = 0

rules = ["\n"+"Quelques règles du discord de la baleine :"+"\n"]
rules.append("- Pas de pubs sans une autorisation des admins"+"\n")
rules.append("- Courtoisie et savoir-vivre"+"\n")
rules.append("- Les calls **SANS ARGUMENT** seront suivis par un avertissement et ensuite un bannissement"+"\n")
rules.append("- Pensez aux gens qui vont lire et mettez-vous à leur place"+"\n")
rules.append("- Le flood et le troll sont interdits"+"\n")
rules.append("- Les commandes de prix, conv etc du bot sont uniquement autorisé dans le chan #bot"+"\n")
rules.append("- Les liens de parrainage sont interdits" +"\n"+"\n"+"\n")
rules.append("Commande du bot :"+"\n"+"\n")
rules.append("\t"+"BaleineDeWallStreet :"+"\n")
rules.append("\t"+"prix -> price (market) coin"+"\n")
rules.append("\t"+"conversion -> conv unité coin"+"\n")
rules.append("\t"+"graph -> chart coin"+"\n")
rules.append("\t"+"order book -> book coin"+"\n"+"\n")
rules.append("Lexique :"+"\n"+"\n")
rules.append("\t"+"!helpList "+"\n")
rules.append("\t"+"!help Recherche"+"\n")
rules = ''.join(rules)

class switch(object):

    value = None
    def __new__(class_, value):
        class_.value = value
        return True

def case(*args):
    return any((arg == switch.value for arg in args))


def calc(boo):

    boo=boo.replace('os.','')
    boo=boo.split()
    boo=boo.remove("calc")
    print(boo)
    return("")  #eval(boo[0])


def traitement(boo): #ICI

    d = 0
    boo = boo.lower()
    print(boo)
    print("Contrôle mot 1")
    if(len(boo.split())>1):
        while switch((boo.split()[0]).lower()):
            if case('prix'):
                d = price(boo.split())
                break
            if case('price'):
                d = price(boo.split())
                break
            if case('conv'):
                d = conv(boo.split())
                break
            if case('volume'):
                print("soon")
                break
            if case('chart'):
                d = chart.chart(boo.split()[1])
                break
            if case('book'):
                d = book.book(boo.split()[1])
                break
            break

    return d

def price(boo2):

    print("Choix du market")

    if(len(boo2)>=2):
        while switch(boo2[1]):
            if case('polo'):            #polo
                boo2.remove("polo")
                t = poloniex(boo2)
                break
            if case('trex'):            #trex
                boo2.remove("trex")
                t = bittrex(boo2)
                break
            if case('poloniex'):        #polo
                boo2.remove("poloniex")
                t = poloniex(boo2)
                break
            if case('bittrex'):         #trex
                boo2.remove("bittrex")
                t = bittrex(boo2)
                break
            if case('p'):           #polo
                boo2.remove("p")
                t = poloniex(boo2)

                break
            if case('b'):               #trex
                boo2.remove("b")
                t = bittrex(boo2)
                break
            t = lost(boo2)                    # Si market pas indiqué
            break

    return t

def conv(boo2):

    print("CONV")

    print(boo2)
    boo2.remove("conv")

    print(boo2)

    valBtc = btcrecup(0)
    valBtcE = btcrecup(1)
    print(valBtcE)
    print(valBtc)
    try:  #si le nombre + la devise
        float(boo2[0])
        final=polorecup(boo2[1],0)

        if(boo2[1].upper()=="BTC"):
            final=float(valBtc)*float(boo2[0])
            final2=float(valBtcE)*float(boo2[0])
            return ("```"+str(boo2[0])+" "+str(boo2[1]).upper()+" valent "+ str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€```")

        if(final==0):
            final=bittrecup(boo2[1],0)
        if(final!=0):
            final2=(float(valBtcE)*(float(final)/float(valBtc)))*float(boo2[0])
            final=float(final)*float(boo2[0])
            final = "```"+str(boo2[0])+" "+str(boo2[1]).upper()+" valent "+ str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€  ("+str("%.4f" %(final/valBtc))+"฿)```"

    except : #si la devise + le nombre
        try:
            float(boo2[1])
        except:
            boo2[1]=0

        if(boo2[0].upper()=="BTC"):
            final=float(valBtc)*float(boo2[1])
            final2=float(valBtcE)*float(boo2[1])
            print(1)
            return ("```"+str(boo2[1])+" "+str(boo2[0]).upper()+" valent "+ str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€```")

        final=polorecup(boo2[0],0)
        if(final==0):
            final=bittrecup(boo2[0],0)

        if(final!=0):
            final2=(float(valBtcE)*(float(final)/float(valBtc)))*float(boo2[1])
            final=float(final)*float(boo2[1])
            final ="```"+str(boo2[1])+" "+str(boo2[0]).upper()+" valent "+  str("%.2f" %final)+"$ ou "+str("%.2f" %final2)+"€  ("+str("%.4f" %(final/valBtc))+"฿)```"

    return final



def bittrex(boo3):

    print("Trex Selector")

    i = 0
    final = ["","","","","",""]
    boo3.remove("price")

    nbreCase = len(boo3)

    offset = 0

    while nbreCase > i :

        final[offset]=bittrecup(boo3[i],1)

        if(final[offset]!=0):
            offset+=1

        i = 1 + i

    return final

def poloniex(boo3):

    print("Polo Selector")

    i = 0
    final = ["","","","","","","","","","","","","","","",""]

    boo3.remove("price")


    nbreCase = len(boo3)

    offset=0

    while nbreCase > i :

        final[offset]=polorecup(boo3[i],1)

        if(final[offset]!=0):
            offset+=1

        i = 1 + i
    return final

def finexrecup(boo4,all):
 
    url="https://api.bitfinex.com/v1/pubticker/"
    valBtc = btcrecup(0)
    market=boo4+"btc"
    print(market)
    content=requests.get(url+market)
    data=content.json()
 
    if("bid" in data):
 
 
        if(all):
            print("all")
            #percent1=((data["last_price"])-(data["result"][0]["PrevDay"]))
            #percent2=(percent1/float(data["result"][0]["PrevDay"]))*100
       
            return("```"+boo4.upper()+"   "+str(data["last_price"])+"฿    $"+str("%.5f" %(float(data["last_price"])*float(valBtc)))+"  (Bitfinex)"+"```")
        else:
            return(data["last_price"]*valBtc)
    else:
        return 0
 
 
def lost(boo3):
 
    i = 0
    final = ["","","","","","","","","","","","","","","",""]
    boo3.remove("price")
 
    nbreCase = len(boo3)
 
    while nbreCase > i :
 
        final[i]=polorecup(boo3[i],1)
 
        if(final[i]==0):
            final[i]=bittrecup(boo3[i],1)
        if(final[i]==0):
            final[i]=finexrecup(boo3[i],1)
 
        i = 1 + i
    return final

def polorecup(boo4,all):

    market="BTC_"+boo4.upper()

    valBtc = btcrecup(0)
    valBtcE = btcrecup(1)

    if(market=="BTC_BTC"):
        value = "```1 BTC vaut "+str(valBtc)+"$"+" ou "+str(valBtcE)+"€```"
        return(value)

    url="https://poloniex.com/public?command=returnTicker"
    print("Poloniex Récup")

    content=requests.get(url)
    data=content.json()



    print(market)

    if(market in data):
        if(all):
            return("```"+boo4.upper()+"   "+data[market]["last"]+"฿ ("+str("%.2f" %(float(data[market]["percentChange"])*100))+"%) $"+(str("%.5f" %(float(data[market]["last"])*(float(valBtc)))))+" (Poloniex)"+"```")
        else:
            return(float(data[market]["last"])*valBtc)
    else:
        return 0


def bittrecup(boo4,all):

    print("Bittrex Recup")

    url="https://bittrex.com/api/v1.1/public/getmarketsummary?market="
    valBtc = btcrecup(0)
    market="btc-"+boo4
    print(market)
    content=requests.get(url+market)
    data=content.json()

    print(data["success"])

    if(data["success"]):

        if(all):
            print("all")
            percent1=((data["result"][0]["Last"])-(data["result"][0]["PrevDay"]))
            percent2=(percent1/float(data["result"][0]["PrevDay"]))*100



            return("```"+boo4.upper()+"   "+str(data["result"][0]["Last"])+"฿ ("+str("%.2f" %percent2)+"%) $"+str("%.5f" %(data["result"][0]["Last"]*float(valBtc)))+"  (Bittrex)"+"```")
        else:
            return(data["result"][0]["Last"]*valBtc)
    else:
        return 0

def btcrecup(euro):

    print("Bitcoin Recup")

    if(euro):
        url="https://www.bitstamp.net/api/v2/ticker/btceur/"
    else:
        url="https://www.bitstamp.net/api/v2/ticker/btcusd/"

    content=requests.get(url)
    data=content.json()
    if( "last" in data):
        return (float(data["last"]))

    else:
        return(0)


def renvoie(boo5):

    print("Fonction de renvoie")
    client = discord.Client()
    boucle = len(boo5)

    i=0

    print(boo5[:])
    while boucle > i :

        i += 1






@client.event
async def on_message(message):
    if message.content.startswith(('price', 'Price', 'prix', 'Prix', 'conv', 'Conv', 'chart', 'Chart', 'book', 'Book')):
        if str(message.channel) != "bot":
            roles = [i.name for i in message.author.roles]
            if 'Baleine novice' in roles:
                await client.send_message(message.author, "Es-tu sûr de respecter les règles d'utilisation du bot ? ;)")

    if message.content.startswith(('price','Price','prix','Prix')):
        await client.send_typing(message.channel)
        retour=traitement(message.content)
        print("retour ok")

        boucle = len(retour)

        i=0

        print(retour[0])
        print(retour[1])


        while boucle > i :

            if(retour[i]!=""):
                await client.send_message(message.channel, retour[i])

            i += 1

    if message.content.startswith(('conv','Conv')):
        await client.send_typing(message.channel)
        retour=traitement(message.content)
        print(retour)

        if(retour!=0):
            await client.send_message(message.channel, retour)

    if message.content.startswith(('calc','Calc')):

        retour=calc(message.content)

        await client.send_message(message.channel,"```"+ ((message.content).split())[1]+ " = " + str("%.2f" %retour)+"```")

    if message.content.startswith(('chart','Chart')):
        # https: // poloniex.com / public?command = returnChartData & currencyPair = BTC_XMR & start = 1405699200 & end = 9999999999 & period = 14400
        await client.send_typing(message.channel)
        retour = traitement(message.content)
        if (retour!=""):
            await client.send_file(message.channel,retour )
            os.remove(retour)
        # await client.send_message(message.channel, chart('etc'))

    if message.content.startswith(('book', 'Book')):
        await client.send_typing(message.channel)
        retour = traitement(message.content)
        if (retour!=""):
            await client.send_file(message.channel,retour )
            os.remove(retour)

    if message.content.startswith(('/rules', '!rules', 'rule', '!règles', 'rules', 'Rules')):

        print(message.content)

        await client.send_message(message.author, rules)




@client.event
async def on_ready():

    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    verif=1


client.run(token)
