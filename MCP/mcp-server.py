from fastmcp import FastMCP
from dotenv import load_dotenv
from typing import Dict
from bharatstock import BharatStock

load_dotenv()

mcp = FastMCP("mcp_server")


@mcp.tool
def get_stock_details(stock_code:str) -> Dict[str | None, str|None ]:
    """
    this function is going to return the current otkc infromation based on the provided details 
    stock_code : A NSE Stock code corresponding to a comany name  
    
    returns lastest price which shos about  currnet price where the market clsed last day as per share market
    """
    client = BharatStock()
    
    response = client.stocks.get(stock_code)

    return  {  "latest_price" : response.industry , "company_name":response.company_name}
    

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )