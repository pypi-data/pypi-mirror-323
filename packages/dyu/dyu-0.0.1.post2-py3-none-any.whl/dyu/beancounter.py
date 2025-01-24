"""Commands to make entries for beancounter."""

import datetime
import typer
import csv
import requests
import json
from datetime import datetime as dt
import logging 

logging.basicConfig(filename='bean.log', level=logging.DEBUG,
format='%(module)s %(funcName)s %(lineno)d %(levelname)s:: %(message)s') 


app = typer.Typer()

def get_rate(date):

    url=f'https://api.frankfurter.app/{date.strftime("%Y-%m-%d")}?amount=1&from=USD&to=INR'
    x=requests.get(url)
    logging.info(x)
    logging.info(x.text)
    j=json.loads(x.text)
    return j['rates']['INR']
@app.command()
def income(
    client: str,
    bill_date: datetime.datetime,
    bill_value: float,
    inr_to_india: float,
    cgst: float,
):
    """Add a new income."""
    print(f"   Income:USD:{client} {bill_value} USD @ {get_rate(bill_date)} INR")
    print(f"   Assets:INR:Cash:IDFC:Current {inr_to_india}")
    print( "   Assets:INR:ExchangeGain")
    print(f"   Assets:INR:GST:ITC:CGST     {cgst} INR")
    print(f"   Assets:INR:GST:ITC:SGST     {cgst} INR")

@app.command()
def upwork(file:str):
    """Processing Upworks Certificate of Earnings."""
    set={
            'WHT':'Expenses:USD:Upwork:WHT',
            'Service Fee':'Expenses:USD:Upwork:ServiceFee',
            'Withdrawal Fee':'Expenses:USD:Upwork:WithdrawalFee',
            'Withdrawal':'Assets:INR:Cash:AccountReceivable:Upwork',
            'Hourly':'Income:USD:Upwork:Client',
            'Fixed Price':'Income:USD:Upwork:Client',
            'Bonus':'Income:USD:Upwork:Client',
            'Refund':'Income:USD:Upwork:Client',
            'Expense':'Income:USD:Upwork:Client'
            }
    with open(file,'r') as csvfile:
        rows=csv.DictReader(csvfile)
        for r in rows:
            date=dt.strptime(r['Date'],'%b %d, %Y')
            print(date.strftime('%Y-%m-%d'),
            " * ",
            f"\"Upworks {r['Team']}\"",
            f"\"{r['Description']}\"",
            )

            conv=  f'@{get_rate(date)} INR'if set[r['Type']] in[
                    'Income:USD:Upwork:Client',
                    'Assets:INR:Cash:AccountReceivable:Upwork'
                    ] else ''
            print(f"    Assets:USD:Upwork {r['Amount']} USD {conv}")
            print(f"    {set[r['Type']]} \n")
@app.command()
def razorpay(file:str):
    with open(file,'r') as csvfile:
        rows=csv.DictReader(csvfile)
        for r in rows:
            date=dt.strptime(r['Date'],"%d/%m/%Y")
            if r['Status'] =="Success":
                print(date.strftime('%Y-%m-%d'),
                      f"* \"{r['Emp Name']} {r['Type']}\"\n",
                      "   Assets:INR:Cash:RazorPay",
                      )
                if r['Credit'] !='':
                    print(f"    Assets:INR:Cash:IDFC:Current {r['Credit']} INR")
                else:
                    print(f"    Expenses:INR:Salary {r['Debit']} INR")


