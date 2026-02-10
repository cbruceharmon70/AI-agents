# agent2.py, B. Harmon 12/31/2025
# Copilot: see also agent1.py
# See additional prompt at the end of the code

import json
from openai import OpenAI

client = OpenAI()

# ---------------------------
# TOOL DEFINITIONS
# ---------------------------

def tool_get_user_input():
    """Tool: get user input for novel name and Celsius number."""
    novel = input("Enter the name of a novel (or 'quit' to exit): ").strip()
    if novel.lower() == "quit":
        return json.dumps({"novel": "quit"})
    number = input("Enter a Celsius number: ").strip()
    return json.dumps({"novel": novel, "celsius": number})

def tool_summarize_novel(novel: str):
    """Tool: LLM-powered novel summary."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize novels briefly."},
            {"role": "user", "content": f"Summarize the novel '{novel}' in 3–4 sentences."}
        ]
    )
    return response.choices[0].message.content.strip()

def tool_convert_c_to_f(celsius: float):
    """Tool: pure Python conversion."""
    return (celsius * 9/5) + 32

# ---------------------------
# MAIN ORCHESTRATOR LOOP
# ---------------------------

def main():
    print("LLM Orchestrator running. Type 'quit' as the novel name to exit.\n")

    while True:
        # Step 1: Ask the LLM what to do next
        controller = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an orchestrator agent. Your job is to call tools to:\n"
                        "1. Get user input (tool_get_user_input)\n"
                        "2. Summarize the novel (tool_summarize_novel)\n"
                        "3. Convert Celsius to Fahrenheit (tool_convert_c_to_f)\n"
                        "You must decide which tool to call next.\n"
                        "When the user enters 'quit' as the novel name, stop the loop.\n"
                        "Always return a JSON object describing what you want done."
                    )
                },
                {"role": "user", "content": "Begin the loop."}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "tool_get_user_input",
                        "description": "Get novel name and Celsius number from the user.",
                        "parameters": {}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "tool_summarize_novel",
                        "description": "Summarize a novel using an LLM.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "novel": {"type": "string"}
                            },
                            "required": ["novel"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "tool_convert_c_to_f",
                        "description": "Convert Celsius to Fahrenheit.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "celsius": {"type": "number"}
                            },
                            "required": ["celsius"]
                        }
                    }
                }
            ]
        )

        # Step 2: The LLM will request the first tool call
        first_call = controller.choices[0].message.tool_calls[0]
        if first_call.function.name != "tool_get_user_input":
            raise RuntimeError("Unexpected first tool call.")

        # Step 3: Execute the user-input tool
        user_input_raw = tool_get_user_input()
        user_input = json.loads(user_input_raw)

        if user_input["novel"].lower() == "quit":
            print("Exiting.")
            break

        # Step 4: Summarize the novel
        summary = tool_summarize_novel(user_input["novel"])

        # Step 5: Convert temperature
        try:
            celsius_value = float(user_input["celsius"])
        except ValueError:
            print("Invalid Celsius number. Restarting loop.\n")
            continue

        fahrenheit_value = tool_convert_c_to_f(celsius_value)

        # Step 6: Output JSON result
        output = {
            "novel": user_input["novel"],
            "summary": summary,
            "celsius": celsius_value,
            "fahrenheit": fahrenheit_value
        }

        print("\nResult:")
        print(json.dumps(output, indent=2))
        print("\n---\n")

if __name__ == "__main__":
    main()

"""
Please make the main program use an llm to orchestrate achieving the same result but such that it in turn draws on the two tools plus a tool to take the user input. I want this to be an implementation of an llm with agents implemented as tools wherein at least one of the tools involves an llm
"""