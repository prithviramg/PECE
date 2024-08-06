import kite_trade
import pandas as pd
from prettytable import PrettyTable
import time
import winsound
import streamlit

def verifyUserProfile(kiteApp):
    assert kiteApp.userProfile()['user_id'] == "XF6031", "User profile is not matching"
    table = PrettyTable()
    table.field_names = ["Attribute", "value"]
    table.align = "l"
    for key, value in kiteApp.userProfile().items():
        if key in ["user_id", "user_name", "password_timestamp", "twofa_timestamp"]:
            table.add_row([key, value])
    print(table)

encToken = "p7EXN3dpyWUUk3anat5q/PeG9cMw1pRP7IrIC3sJDUwM4t0Sw6zHbgRQCwBQCu5DuXRLm9crXy/+C6FoAmifFh/jCUERhOEa0pSuq0Oqzerbn0gWupFdHA==" #str(input("Enter your ENCTOCKEN: "))
kite = kite_trade.KiteApp(encToken)
verifyUserProfile(kite)

