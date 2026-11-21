"""
crewai_example.py - a two-agent "crew" written for the CrewAI framework.

IMPORTANT: CrewAI is NOT installed in the course environment (it is large and pulls
many dependencies). This file is here to READ and to run on your own machine:

    python -m venv .venv && source .venv/bin/activate     # a separate, clean environment
    pip install crewai
    export ANTHROPIC_API_KEY=your-key-here                 # or OPENAI_API_KEY
    python crewai_example.py

If crewai is missing, the script prints a message and exits instead of crashing.
The notebook 04-multi-agent-memory-mcp.ipynb rebuilds the same idea in plain Python.

CrewAI vocabulary (check https://docs.crewai.com for the current API - it moves fast):
  Agent   - a "worker" with a role, a goal and a backstory (these become its system prompt).
  Task    - a piece of work: a description, the expected output, and which agent does it.
  Crew    - the team: a list of agents + a list of tasks + a process.
  Process - how tasks are run: sequential (one after another) or hierarchical
            (a manager agent hands out the work).
  kickoff - start the crew; `inputs` fill {placeholders} in task descriptions.
"""
import os
import sys

try:
    from crewai import LLM, Agent, Crew, Process, Task   # the four main building blocks + model wrapper
except ImportError:
    print("crewai is not installed. Read this file, or run it in its own virtual environment.")
    sys.exit(0)                                          # exit cleanly - this is expected in the course env

# Choose the model. CrewAI uses "provider/model-name" strings (LiteLLM style).
# Model names change - check your provider's models page and set CREW_MODEL in .env.
llm = LLM(model=os.getenv("CREW_MODEL", "anthropic/claude-opus-5-5"))

# Agent 1: the researcher. role/goal/backstory are turned into the agent's instructions.
researcher = Agent(
    role="Research Analyst",
    goal="Collect accurate, recent facts about {topic}",
    backstory="You are careful and always say where a fact came from.",
    llm=llm,
    verbose=True,              # print the agent's thinking steps to the terminal
    allow_delegation=False,    # this agent may not hand work to other agents
)

# Agent 2: the writer.
writer = Agent(
    role="Technical Writer",
    goal="Explain {topic} to complete beginners in plain English",
    backstory="You turn research notes into short, friendly explanations.",
    llm=llm,
    verbose=True,
)

# Task 1 is done by the researcher.
research_task = Task(
    description="List 5 key facts about {topic}. Keep each under 25 words.",
    expected_output="A numbered list of 5 facts.",
    agent=researcher,
)

# Task 2 is done by the writer and automatically receives Task 1's output as context.
writing_task = Task(
    description="Using the research, write a 150-word beginner explanation of {topic}.",
    expected_output="One paragraph of about 150 words.",
    agent=writer,
    context=[research_task],   # explicit: feed the research output into this task
)

# The crew ties it together. Sequential = research first, then writing.
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": "the Model Context Protocol"})  # fills {topic}
    print("\n=== FINAL OUTPUT ===\n", result)
