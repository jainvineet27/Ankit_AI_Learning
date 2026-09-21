import asyncio
import json 
from tools_2 import get_stock_details 
from connect_to_db_2 import get_schema , get_table

tool_mapping = {"get_stock_details":get_stock_details , "get_table" :get_table , "get_schema" :get_schema }

async def execute_item(item) -> dict:
    f_name=  item.name
    call_id = item.call_id
    args = json.loads(item.arguments)
    
    tool = tool_mapping.get(f_name)
    if tool is None:

        return {
            "type": "function_call_output",
            "call_id": call_id,
            "output": json.dumps({"error": f"Tool '{f_name}' not found."})
        }

    f_output = await tool(**args)

    return {
        "type": "function_call_output", 
        "call_id": call_id,
        "output": str(f_output)
    }

async def concurrent_runs(functions_call) -> list: 

    response = await asyncio.gather(*(execute_item(item) for item in functions_call))
    return response