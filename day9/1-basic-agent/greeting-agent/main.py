from google.adk.agents import Agent 

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="A helpful assistant that greets the user",
    instructions="""You are a helpful assistant that greets the user. 
                    Ask the users name and then greet them by name""",
)

def main():
    print("Hello from greeting-agent!")


if __name__ == "__main__":
    main()
