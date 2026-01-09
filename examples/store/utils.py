import hashlib
import urllib.parse

def generate_signature(dataArray, passPhrase = ''):
    payload = ""
    for key in dataArray:
        # Get all the data from Payfast and prepare parameter string
        payload += key + "=" + urllib.parse.quote_plus(str(dataArray[key]).replace("+", " ")) + "&"
    # After looping through, cut the last & or append your passphrase
    payload = payload[:-1]
    if passPhrase != '':
        payload += f"&passphrase={passPhrase}"
    return hashlib.md5(payload.encode()).hexdigest()