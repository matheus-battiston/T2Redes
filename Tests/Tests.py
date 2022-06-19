# Python 3.7
import io
import unittest
import unittest.mock

from parameterized import parameterized

import main
from main import *

def get_resposta(arquivo):
    diretorio = os.getcwd() + '/Arquivos/' + arquivo
    file1 = open(diretorio, 'r')
    Lines = file1.readlines()
    Lines = ''.join(Lines)

    return Lines


#  - test--
class TestFunction(unittest.TestCase):

    @parameterized.expand([
        ([('Topologia.txt', 'ping', 'n1', 'n2'), get_resposta('Resposta1.txt')]),
        ([('Topologia.txt', 'ping', 'n1', 'n3'), get_resposta('Resposta2.txt')]),
        ([('Topologia.txt', 'traceroute', 'n1', 'n3'), get_resposta('Resposta3.txt')]),
        ([('Topologia2.txt', 'traceroute', 'n1', 'n2'), get_resposta('Resposta4.txt')]),
        ([('Topologia3.txt', 'ping', 'n1', 'n2'), get_resposta('Resposta5.txt')]),
        ([('Topologia3.txt', 'traceroute', 'n1', 'n2'), get_resposta('Resposta6.txt')]),
        ([('Topologia4.txt', 'ping', 'n1', 'n2'), get_resposta('Resposta7.txt')]),
        ([('Topologia4.txt', 'traceroute', 'n1', 'n2'), get_resposta('Resposta8.txt')]),

    ])
    def test_prints(self, a, resposta):
        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            main(a)
            self.assertEqual(
                mock_stdout.getvalue(),
                resposta  # It's important to remember about '\n'
            )

