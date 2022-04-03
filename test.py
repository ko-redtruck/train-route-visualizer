def name():
    
    #Freiburg&#x0028;
    raw_characters = list("Freiburg&#x0028;Breisgau&#x0029; Hbf")
    real_characters = []
    i=0
    while i < len(raw_characters):
        c = raw_characters[i]
        if i < len(raw_characters)-2 and "".join(raw_characters[i:i+3]) == "&#x":
            c = chr(int("".join(raw_characters[i+3:i+7]),base=16))
            i+=7
        real_characters.append(c)
        i+=1
    return "".join(real_characters)