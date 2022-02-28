import json
import time
import contract as c
from price import get_drip_price
from datetime import datetime
import time

drip_contract_addr = "0xFFE811714ab35360b67eE195acE7C10D93f89D8C"
wallet_public_addr = "0x361472B5784e83fBF779b015f75ea0722741f304"
min_hydrate_amount = 0.050
loop_sleep_seconds = 60*60 # One hour

# load private key
wallet_private_key = open('key.txt', "r").readline()

# load abi
f = open('faucet_abi.json')
faucet_abi = json.load(f)

# create contract
faucet_contract = c.connect_to_contract(drip_contract_addr, faucet_abi)

def deposit_amount(addr):
    user_totals = faucet_contract.functions.userInfoTotals(addr).call()
    return user_totals[1]/1000000000000000000

def available(addr):
    return faucet_contract.functions.claimsAvailable(addr).call() / 1000000000000000000

def hydrate():
    txn = faucet_contract.functions.roll().buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1

    
# create infinate loop that checks contract every set sleep time
while True:
    deposit = deposit_amount(wallet_public_addr)
    hydrate_amount = deposit * .01
    avail = available(wallet_public_addr)
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")
    
    if avail > min_hydrate_amount and avail >= hydrate_amount:
        hydrate()
        new_deposit = deposit_amount(wallet_public_addr)
        drip_price = get_drip_price()
        total_value = new_deposit * drip_price
        
        print(f"{timestampStr} Hydrated! {avail:.3f} added to deposit. Total deposit now {new_deposit:,.2f}")
        print(f"{timestampStr} Total value of your deposit is now ${total_value:,.2f}")
    else:
        if avail < min_hydrate_amount:
            print(f"{timestampStr} Only {avail:.3f} Drip is available for the minimum required amount: {min_hydrate_amount:.3f}. Sleeps..")
        else:
            print(f"{timestampStr} Hydrate not ready {avail:.3f} Drip available. Need {(hydrate_amount - avail):.3f} more")

    countdown(loop_sleep_seconds)
    
