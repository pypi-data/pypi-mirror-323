import random

import yelllovkitten
import inspect


#def debuging():

def errors(error: int,error_warn: int):
    error = errors_2(error)
    if error_warn == 1:
        yelllovkitten.text.info(error)
    elif error_warn == 2:
        yelllovkitten.text.warn(error)
    else:
        yelllovkitten.text.error(error)

def errors_2(error):
    if error == 0:
        out_text = 'No errors found!'
    #elif error == -1:
        #out_text = 'internal error: the function could not be started.'
    elif error == 1:
        out_text = 'It isn\'t recommended to use function arguments without specifying a valid data type.'
    elif error == 2:
        out_text = 'An error has been found, but at the moment debug cannot tell the cause of the error, it may be in the next update.'
    else:
        out_text = f'debug found the error, but can\'t figure out what the error is, the error code:{error}'


    return out_text


def debug4():
    out_text = 0
    alph = 'abcdefghijklmnopqrstuvwxyz'
    num = random.randint(1,4)
    if num == 1:
        if random.randint(0, 1):
            out_text = False
        else:
            out_text = True
    elif num == 2:
        most = ''
        for i in range(random.randint(1, 20)):
            most = alph[random.randint(0, len(alph) - 1)] + most
        out_text = most
    elif num == 3:
        most = 0
        for i in range(random.randint(1, 8)):
            most = str(random.randint(0, 9)) + str(most)
        out_text = int(most)
    elif num == 4:
        out_text = random.random() * 9
    return out_text

def debug3(func):
    list_ = []
    alph = 'abcdefghijklmnopqrstuvwxyz'
    arguments = func.__annotations__
    debuging = debug2(func, arguments)
    a = 0
    for i in debuging:
        if a == len(debuging):
            a = 0
        if debuging[a] is bool:

            if random.randint(0,1):
                debuging[a] = False
            else:
                debuging[a] = True
        elif debuging[a] is str:
            most = ''
            for i in range(random.randint(1,20)):
                most = alph[random.randint(0, len(alph) - 1)] + most
            debuging[a] = most
        elif debuging[a] is int:
            most = 0
            for i in range(random.randint(1,8)):
                most = str(random.randint(0,9)) + str(most)
            debuging[a] = int(most)
        elif debuging[a] is float:
            debuging[a] = random.random()*9
        if debuging[a] != None:
            list_ = list_ + [debuging[a]]
        else:
            break
        a += 1
    return list_

def debug2(func,arguments):
    exitt = []
    if len(arguments) != 0:
        dict_ = {}
        a = 0
        for i in arguments:
            a += 1
            if a == len(arguments.values()):
                break
            dict_.update({str(i):str(arguments[i])})
        exitt = debug2(func,dict_)
    every = len(inspect.getfullargspec(func).args)
    see = len(func.__annotations__)
    argument = None
    if len(arguments) == 0:
        return
    for i in arguments:
        argument = arguments[i]
    if exitt == None:
        exitt = []
    method = eval(str(argument).split()[1].strip()[1:][:-2])
    exitt.append(method)
    return exitt