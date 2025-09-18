use smolagents to define LLM MCP tooling. 

the following tools should be supported: 
- looking up the user's to-do list database using a search query (e.g. date, string matching, etc.)
- internet searches through the Brave API 
- adding a new to-do list entry into the database 
- removing a to-do list entry from the database 
- editing an existing to-do list entry in the database 

generic.py contains the example structure for a tool.

backend/src/schemas.py contains schemas for creating tasks. 