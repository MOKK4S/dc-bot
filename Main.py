import discord
from discord.client import Client
from discord.ext import commands
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from discord.message import Message
import mysql.connector
import json

f = open('data.json',)

data = json.load(f)

db = mysql.connector.connect(
  host = "localhost",
  user ="root",
  database = 'discord',

)

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '!mail ')

TOKEN = data['token']

@client.event
async def on_ready():
    print("Bot is ready: {0.user}".format(client))

@client.command()
async def ping(ctx):
    await ctx.send(f'Response time = {round(client.latency * 1000)}ms')



@client.command()#Mail sending command
async def send(ctx, receiver_address, Title, Description, ilosc=1 ):
    embed=discord.Embed(title=f'Title:{Title}', description=Description, color=0xd747ff)
    embed.add_field(name="Address that we sent your messages", value=receiver_address, inline=True)
    embed.add_field(name="Number of copies sent", value=ilosc, inline=True)
    emb = await ctx.send(embed=embed)
    await emb.add_reaction("✅")#emoji
    await emb.add_reaction("❌")#emoji
    r, u = await client.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id and str(r.emoji) in ['✅', '❌'])
    if str(r.emoji) == '✅':
        for i in range(1, ilosc + 1 ):
            mycursor = db.cursor()#baza danych
            
            mycursor.execute(f"SELECT Email, Haslo FROM passy ORDER BY RAND() LIMIT 1") #random generating mails
            mydata = mycursor.fetchall()
            number = [x for x in mydata] 
            numberstr = number[-1]

            sender_address = numberstr[-2]
            sender_pass = numberstr[-1]
            if receiver_address !="lista":     #Check if list is added if not used DB
                mail_content = Description
                message = MIMEMultipart()
                message['From'] = sender_address
                message['To'] = receiver_address
                message['Subject'] = Title
                message.attach(MIMEText(mail_content, 'plain'))
                session = smtplib.SMTP('smtp.gmail.com', 587)
                session.starttls()
                session.login(sender_address, sender_pass) 
                text = message.as_string()
                session.sendmail(sender_address, receiver_address, text)
                i+=1
            else:#list 
                mycursor.execute(f"SELECT Email from `lmaile`")
                mylista = mycursor.fetchall()

                for mail in mylista:
                    mail_content = Description
                    message = MIMEMultipart()
                    message['From'] = sender_address
                    message['To'] =  mail[-1]
                    message['Subject'] = Title
                    print(mail)

                    
                    message.attach(MIMEText(mail_content, 'plain'))
                    session = smtplib.SMTP('smtp.gmail.com', 587)
                    session.starttls()
                    session.login(sender_address, sender_pass) 
                    text = message.as_string()
                    session.sendmail(sender_address, mail, text)
                    i+=1

        session.quit()

    elif str(r.emoji) == '❌':
        await ctx.send("Work has been suspended🤖")


@client.command()
async def add(ctx, PwMail):
    EmailA, EmailP = PwMail.split(":")
    if EmailA.find("@") == -1: #Checking is mail valid
        embed=discord.Embed(color=0xff0000)
        embed.add_field(name="Incorrect mail", value="Try again!", inline=False) #if not 
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(color=0x00ff00)
        embed.add_field(name="Sent to db", value="undefined", inline=False)
        embed.add_field(name="Email: ", value=EmailA, inline=True)
        embed.add_field(name="Password: ", value=EmailP, inline=False)
        emb = await ctx.send(embed=embed)
        await emb.add_reaction("✅")
        await emb.add_reaction("❌")
        r, u = await client.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id and str(r.emoji) in ['✅', '❌']) #adding reaction to waiting for approval
        if str(r.emoji) == '✅':
            mycursor = db.cursor()
            mycursor.execute("INSERT INTO passy (Email, Haslo) VALUES (%s,%s)",(EmailA, EmailP) )
            db.commit() # Query approval
        elif str(r.emoji) == '❌':
            await ctx.send("Work has been suspended🤖")
            
@client.command()
async def delete(ctx, Email):
    embed=discord.Embed(color=0xff0000)
    embed.add_field(name="Mail has been removed", value="undefined", inline=False)
    embed.add_field(name="Email: ", value=Email, inline=True)
    emb = await ctx.send(embed=embed)
    await emb.add_reaction("✅")
    await emb.add_reaction("❌")
    r, u = await client.wait_for('reaction_add', check=lambda r, u: u.id == ctx.author.id and str(r.emoji) in ['✅', '❌'])
    if str(r.emoji) == '✅':
        mycursor = db.cursor()
        Emaildb = '"'+ Email +'"'#added "" because of Mysql Query
        mycursor.execute(f'DELETE FROM `passy` WHERE Email = {Emaildb}')
        db.commit()
    elif str(r.emoji) == '❌':
        await ctx.send("Work has been suspended🤖")
        
@client.command()
async def show(ctx):
    mycursor = db.cursor()
    mycursor.execute("SELECT Email, Haslo FROM passy ")

    list = ""
    for x,y in mycursor:
        list += x +" : "+ y + "\n"


    embed=discord.Embed(color=0x00bfff)
    embed.add_field(name="Mail combolist:", value=list, inline=False)
    emb = await ctx.send(embed=embed)
      


@client.command()
async def bug(ctx, desc=None, rep=None):
    user = ctx.author
    await ctx.author.send('```Tell us about bug```')
    responseDesc = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=300)
    description = responseDesc.content
    await ctx.author.send('````Bug Dectription: ```')
    responseRep = await client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=300)
    replicate = responseRep.content
    embed = discord.Embed(title='Bug Report', color=0x00ff00)
    embed.add_field(name='Description', value=description, inline=False)
    embed.add_field(name='Replicate', value=replicate, inline=True)
    embed.add_field(name='Reported By', value=user, inline=True)
    adminBug = client.get_channel(788484028717596673)
    await adminBug.send(embed=embed)
    # Add 3 reaction (different emojis) here

@client.command()
async def spam(ctx, person, count=1):
    for i in range(count):
        i+=1
        await ctx.send(person)



client.run(TOKEN)