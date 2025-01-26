""" testen voor de package waterstand """
import unittest
from unittest.mock import patch, MagicMock, ANY
from urllib.error import HTTPError, URLError

import waterstand


def create_mock_response(filenaam):
  """ maak een response van de testdata """
  with open(filenaam, 'r', encoding='utf-8') as fid:
    testdata = fid.read()

  mock_response = MagicMock()
  mock_response.getcode.return_value = 200
  mock_response.read.return_value = testdata.encode('utf-8')
  mock_response.__enter__.return_value = mock_response
  return mock_response


class TestUrlopen(unittest.TestCase):
  """ Class voor het testen van de package waterstand """

  @patch('urllib.request.urlopen')
  def test_haalwaterstand(self, mock_urlopen):
    """ test van de normale flow """
    mock_urlopen.return_value = create_mock_response('tests/testdata.json')

    response = waterstand.haalwaterstand('Katerveer', 'KATV')
    verwacht = {'resultaat': 'OK', 'tijd': '23-11 16:50', 'nu': 84.0, 'morgen': 89.0}

    self.assertEqual(response, verwacht)

  @patch('urllib.request.urlopen')
  def test_haalwaterstand_timeformat(self, mock_urlopen):
    """ test 2 van de normale flow """
    mock_urlopen.return_value = create_mock_response('tests/testdata2.json')

    response = waterstand.haalwaterstand('Katerveer', 'KATV')
    verwacht = {'resultaat': 'OK', 'tijd': '23-11 16:50', 'nu': 84.0, 'morgen': 89.0}

    self.assertEqual(response, verwacht)

  @patch('urllib.request.urlopen', side_effect=HTTPError('', 0, '', None, None))
  def test_haalwaterstand_httperror(self, mock_urlopen):
    """ test van een HTTP-fout bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_urlopen.called

  @patch('urllib.request.urlopen', side_effect=TimeoutError)
  def test_haalwaterstand_timeouterror(self, mock_urlopen):
    """ test van een time-out bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_urlopen.called

  @patch('urllib.request.urlopen', side_effect=URLError('Dummy'))
  def test_haalwaterstand_urlerror(self, mock_urlopen):
    """ Test van een URL-fout bij het ophalen """
    response = waterstand.haalwaterstand('Katerveer', 'KATV')

    expected = {'resultaat': 'NOK', 'error': ANY}
    self.assertEqual(response, expected)
    assert mock_urlopen.called
