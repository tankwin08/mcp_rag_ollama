import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama
import json

server_params = StdioServerParameters(
    command="python",
    args=["server.py"], 
    env=None,
)

user_query = 'Minus 8 and 12'

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("##### Available tools:", tools)

            result = await session.call_tool("add", arguments={"a": 7, "b": 3})
            print("##### Result of addition:", result)

            prompts = await session.list_prompts()
            print("##### Available prompts:", prompts)
            
            prompt_names = [prompt.name for prompt in prompts.prompts] 

            if "operation-decider" in prompt_names:
                prompt = await session.get_prompt(name=prompt_names[0], arguments={"user_query": user_query})
                response = ollama.chat(model="deepseek-r1:latest", messages=[{"role": "user", "content": prompt.messages[0].content.__getattribute__("text")}], options={"temperature": 0.7})
                print("##### Response", response.message.content)

                # Extract the JSON part from the response content
                raw_content = response.message.content
                json_start_index = raw_content.find('{')
                if json_start_index != -1:
                    json_string = raw_content[json_start_index:]
                    try:
                        extracted_data = json.loads(json_string)
                        print("##### Extracted data", extracted_data)
                        a, b, operation = extracted_data["a"], extracted_data["b"], extracted_data["operation"].strip().lower()

                        if operation in ["add", "subtract"]:
                            result = await session.call_tool(operation, arguments={"a": a, "b": b})
                            print(f"##### Result of {operation}({a}, {b}): {result}")
                        else:
                            print("##### LLM provided an invalid operation.")
                    except json.JSONDecodeError as e:
                        print(f"##### Failed to decode JSON: {e}")
                        print(f"##### JSON string attempted: {json_string}")
                else:
                    print("##### Could not find JSON object in LLM response.")
            else:
                print("Issue in finding tools")       

if __name__ == "__main__":
    asyncio.run(run())