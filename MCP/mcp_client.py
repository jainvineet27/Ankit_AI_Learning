from fastmcp import Client
from openai import AsyncOpenAI

from dotenv import load_dotenv
import asyncio
import json

load_dotenv()
openai_client = AsyncOpenAI()
user_query = input(" Ask something :")

async def main():

    async with Client("https://swimsuit-dominion-parcel.ngrok-free.dev/mcp") as mcp_client:
        mcp_tools = await mcp_client.list_tools()
        print("MCP tools:")

        for tool in mcp_tools:
            print(tool.name)
            print(tool.description)
            print(tool.input_schema)

        my_tools = []

        for tool in mcp_tools:

            my_tools.append(
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
            )

        # --------------------------------
        # 4. Send question to OpenAI
        # --------------------------------
        response = await openai_client.responses.create(
            model="gpt-5.6-luna",
            input=user_query,
            tools=my_tools
        )
        # --------------------------------
        # 5. Tool calling loop
        # --------------------------------
        while True:
            llm_output=  response.output
            tool_outputs = []
            for item in llm_output:

                if item.type == "function_call":

                    tool_name = item.name
                    arguments = json.loads(item.arguments)
                    print("\nCalling MCP tool:")
                    print(tool_name)
                    print(arguments)

                    # --------------------------------
                    # 6. Call MCP server
                    # --------------------------------

                    result = await mcp_client.call_tool(
                        tool_name,
                        arguments
                    )
                    print("\nMCP result:")
                    print(result)

                    # --------------------------------
                    # 7. Give result back to OpenAI
                   # --------------------------------
                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": str(result)
                        }
                    )
            # --------------------------------
            # No tool call?
            # We are finished.
            # --------------------------------
            if not tool_outputs:
                break
            # --------------------------------
            # 8. Send tool result back
            # --------------------------------

            response = await openai_client.responses.create(
                model="gpt-5.6-luna",
                input=tool_outputs,
                previous_response_id=response.id,
                tools=my_tools
            )
            llm_output = response.output
        # --------------------------------
        # 9. Final answer
        # --------------------------------
        print("\nFinal answer:")
        print(response.output_text)

asyncio.run(main())