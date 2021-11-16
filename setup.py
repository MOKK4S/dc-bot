import os
cut = "========================================================="

print(cut)
print("Welcome in bot setup\nPlease add your token\n")
print("Here u can find your token:\nhttps://discord.com/developers/applications")
print(cut, "\n")
token = input("Type HERE your token:")
with open("data.json", "w") as f:
    f.write('''{
        "token":"%s"
}
            '''% token)
filesize = os.path.getsize("data.json")    

if filesize == 0:
    print("ERROR file can't be made")
else:
    print("Everything works!")