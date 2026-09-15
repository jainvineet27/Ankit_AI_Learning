''' this is important module where we have mentioend lit oflla the functionalities'''
from bharatstock import BharatStock
from dotenv import load_dotenv

load_dotenv()

def get_stock_details(stock_code:str) -> str:
    """
    this function is going to return the current otkc infromation based on the provided details 
    stock_code : A NSE Stock code corresponding to a comany name  
    
    returns lastest price which shos about  currnet price where the market clsed last day as per share market
    """
    client = BharatStock()
    response = client.stocks.get(stock_code)

    return response.latest_price , response.company_name





    