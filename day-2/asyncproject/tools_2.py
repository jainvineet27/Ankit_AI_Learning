from bharatstock import BharatStock
import asyncio 
from dotenv import load_dotenv

load_dotenv()

async def get_stock_details(stock_code:str):
    client = BharatStock()
    response  = client.stocks.get(stock_code)

    return  {  "latest_price" : response.industry , "company_name":response.company_name  }

