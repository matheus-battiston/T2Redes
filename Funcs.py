from textwrap import wrap


def get_ip_rede(ip):
    binario = ''
    prefixo = ip.split('/')[1]
    num = ip.split('/')[0].split('.')
    for x in num:
        z = format(int(x), '08b')
        binario += z

    primeiro_endereco = binario[:len(binario) - (32-int(prefixo))] + '0'*(32-int(prefixo))
    primeiro_endereco = wrap(primeiro_endereco, 8)

    for enum, x in enumerate(primeiro_endereco):
        primeiro_endereco[enum] = str(int(x, 2))

    primeiro_endereco = '.'.join(primeiro_endereco)
    return primeiro_endereco

