import discord
from discord.ext import commands

import psycopg3
from random import choice

# db connect
with open("db_access.txt", "r") as f:
    db = f.read()

try:
    conn = psycopg3.connect(db)
    cur = conn.cursor()
except:
    print("Não foi possível se conectar com o db")

def atribui_status():
    """
    Atribui os status do soldado aleatoriamente.
    Retorna um dicionário com os status e seus valores.
    """
    pontos = [5, 2, 2, 1]
    atributos = ["forca", "armadura", "vida", "vel_ataque"]
    status = {}

    while len(pontos) > 0:
        atributo = choice(atributos)
        ponto = choice(pontos)
        atributos.remove(atributo)
        pontos.remove(ponto)
        status[atributo] = ponto

    return status

bot = commands.Bot(command_prefix= '>')

@bot.event
async def on_ready():
    print('Logado como')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def entrar(ctx):
    try:
        cur.execute(f"SELECT to_regclass('public.id_{ctx.author.id}')")
        result = cur.fetchall()
        print("resultado: ",result)
        if result[0][0] != None:
            await ctx.send(f"{ctx.author.name} você já está participando, >help para saber mais.")
        else:
            cur.execute(f"""CREATE TABLE IF NOT EXISTS id_{ctx.author.id} (id SMALLSERIAL PRIMARY KEY, nome TEXT, forca INTEGER, armadura INTEGER, vida INTEGER, vel_ataque INTEGER, rank INTEGER, moedas INTEGER )""")
            cur.execute(f"INSERT INTO id_{ctx.author.id} VALUES (DEFAULT,'gold', 0, 0, 0, 0, 0, 200)")
            conn.commit()
            await ctx.send(f"Bem vindo ao Lik rpg {ctx.author.name}.")
            await ctx.send("Você começa com 200 moedas, use >soldado [nome_do_soldado], para pegar um soldado com status aleatórios por 100 moedas.")
    except EnvironmentError:
        await ctx.send("Algo deu errado tente novamente mais tarde e/ou avisa os moderadores.")
        print(EnvironmentError)

@bot.command()
async def soldado(ctx, nome):
    try:
        name = ('gold', )
        cur.execute(f"SELECT moedas FROM id_{ctx.author.id} WHERE nome = %s", ('gold', ))
        aux = cur.fetchone()
        moedas = aux[0]
        print(moedas)
        if moedas >= 100:
            moedas -= 100
            cur.execute(f"UPDATE id_{ctx.author.id} SET moedas = {moedas} WHERE nome = %s", name)
            status = atribui_status()
            cur.execute(f"INSERT INTO id_{ctx.author.id} VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)", (nome, status["forca"], status["armadura"], status["vida"], status["vel_ataque"], 1, 0))
            conn.commit()
            await ctx.send(f"@{ctx.author.name} você adiquiriu um soldado com os seguintes status:\nForça: {status['forca']}\nArmadura: {status['armadura']}\nVida: {status['vida']}\nVel. Ataque: {status['vel_ataque']}")
        else:
            await ctx.send(f"@{ctx.author.name} você precisa de 100 moedas para comprar um soldado, você possui {moedas}.")
    except EnvironmentError:
        await ctx.send(f"@{ctx.author.name} você dar um nome ao seu soldado.")
        print("Erro no bd",EnvironmentError)

    


with open("token.txt","r") as f:
    token = f.read()

bot.run(token)