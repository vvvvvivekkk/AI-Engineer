# Module 10 - Agentic AI

## What an agent is
An **AI agent** is an LLM that works in a loop: it decides which **tool** to call (a function such as a calculator, a search or a database query), reads the result, and repeats until it can answer. This loop is often called **ReAct**: reason, act, observe.

## Tool calling
In **tool calling** (also called function calling), you describe each tool with a name, a description and a JSON schema for its inputs. The model replies with a structured request to call a tool, your code runs it, and you send the result back.

## Guardrails
Agents need limits: a maximum number of steps, read-only database access, timeouts, and human approval before risky actions such as sending emails or spending money.

## MCP
The **Model Context Protocol** (MCP) is an open standard for exposing tools and data to AI applications. You write an MCP server once and any MCP-capable client can use its tools.
