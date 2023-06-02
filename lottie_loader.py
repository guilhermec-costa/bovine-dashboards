import requests

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_all_lotties():
    lottie = load_lottieurl('https://assets7.lottiefiles.com/packages/lf20_puciaact.json')
    accept = load_lottieurl('https://assets3.lottiefiles.com/datafiles/uoZvuyyqr04CpMr/data.json')
    cat = load_lottieurl('https://assets8.lottiefiles.com/temp/lf20_QYm9j9.json')
    return lottie, accept, cat
