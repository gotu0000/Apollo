monthNames = {0:'January'\
            ,1:'February'\
            ,2:'March'\
            ,3:'April'\
            ,4:'May'\
            ,5:'June'\
            ,6:'July'\
            ,7:'August'\
            ,8:'September'\
            ,9:'October'\
            ,10:'November'\
            ,11:'December'\
            }


month = {'Jan':1
        ,'Feb':2
        ,'March':3
        ,'April':4
        ,'May':5
        ,'June':6
        ,'July':7
        ,'Aug':8
        ,'Sept':9
        ,'Oct':10
        ,'Nov':11
        ,'Dec':12
        }

def get_month_from_count(hourCount):
    janHour = (31*24)-1
    febHour = janHour+(28*24)
    marchHour = febHour+(31*24)
    aprilHour = marchHour+(30*24)
    mayHour = aprilHour+(31*24)
    juneHour = mayHour+(30*24)
    julyHour = juneHour+(31*24)
    augustHour = julyHour+(31*24)
    septHour = augustHour+(30*24)
    octHour = septHour+(31*24)
    novHour = octHour+(30*24)
    decHour = novHour+(31*24)
    if(hourCount <= janHour):
        return 0
    elif(hourCount > janHour)and(hourCount <= febHour):
        return 1
    elif(hourCount > febHour)and(hourCount <= marchHour):
        return 2
    elif(hourCount > marchHour)and(hourCount <= aprilHour):
        return 3
    elif(hourCount > aprilHour)and(hourCount <= mayHour):
        return 4
    elif(hourCount > mayHour)and(hourCount <= juneHour):
        return 5
    elif(hourCount > juneHour)and(hourCount <= julyHour):
        return 6
    elif(hourCount > julyHour)and(hourCount <= augustHour):
        return 7
    elif(hourCount > augustHour)and(hourCount <= septHour):
        return 8
    elif(hourCount > septHour)and(hourCount <= octHour):
        return 9
    elif(hourCount > octHour)and(hourCount <= novHour):
        return 10
    elif(hourCount > novHour)and(hourCount <= decHour):
        return 11
    else:
        return 12