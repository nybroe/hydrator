import json
import time
import contract as c
from price import get_drip_price
from datetime import datetime
import time

drip_contract_addr = "0xFFE811714ab35360b67eE195acE7C10D93f89D8C"
wallet_public_addr = "0x361472B5784e83fBF779b015f75ea0722741f304"
min_hydrate_amount = 0.5
loop_sleep_seconds = 60*10
start_polling_threshold_in_seconds = 60*10

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

def buildTimer(t):
    mins, secs = divmod(int(t), 60)
    hours, mins = divmod(int(mins), 60)
    days, hours = divmod(int(hours), 24)
    timer = '{:02d} days, {:02d} hours, {:02d} mins, {:02d} seconds'.format(days, hours, mins, secs)
    return timer

def countdown(t):
    while t:
        print(f"Start polling in: {buildTimer(t)}", end="\r")
        time.sleep(1)
        t -= 1

    
# create infinate loop that checks contract every set sleep time
while True:
    deposit = deposit_amount(wallet_public_addr)
    #hydrate_amount = deposit * .01
    avail = available(wallet_public_addr)
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")

    dripPerDay = deposit * 0.01
    dripPerSecond = dripPerDay / 24 / 60 / 60
    secondsUntilHydration = (min_hydrate_amount - avail) / dripPerSecond
    
    sleep = loop_sleep_seconds

    if secondsUntilHydration > start_polling_threshold_in_seconds:
        sleep = secondsUntilHydration - start_polling_threshold_in_seconds
    
    if avail > min_hydrate_amount:
        hydrate()
        new_deposit = deposit_amount(wallet_public_addr)
        drip_price = get_drip_price()
        total_value = new_deposit * drip_price

        print("********** HYDARTED *******")
        print(f"{timestampStr} Added to deposit: {avail:.3f}")
        print(f"{timestampStr} New total deposit: {new_deposit:,.2f}")
        print(f"{timestampStr} New total value: {total_value:,.2f}")
        print("***************************")
    else:
        print("********** STATS *******")
        print(f"{timestampStr} Deposit: {deposit:.3f}")
        print(f"{timestampStr} Minimum hydrate amount: {min_hydrate_amount:.3f}")
        print(f"{timestampStr} Available to hydrate: {avail:.3f}")
        print(f"{timestampStr} Drip per second: {dripPerSecond:.8f}")
        print(f"{timestampStr} Until next hydration: {buildTimer(secondsUntilHydration)}")
        print(f"{timestampStr} Start hydration polling {(start_polling_threshold_in_seconds / 60):.0f} min before next hydration")
        print("************************")

    countdown(int(sleep))
    
