import random

# generate random password of length 15
def random_password():
    lower = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    upper = 'abcdefghijklmnopqrstuvwxyz'
    num = '1234567890'
    symbols = '!@#$%^&*'
    
    all = lower + upper + num + symbols

    temp = random.sample(all, 15, )
    pw = ''.join(temp)

    return pw
