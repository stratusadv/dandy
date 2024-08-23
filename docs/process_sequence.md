# Process Sequence

### Description
We have a user add a work order to the system and we want to pull all the work orders on that machine and use a large language model to see if any of the other work orders are similar and return the id's and information related to the similare work orders with a description the relationship.

### Operation Sequence

```mermaid
sequenceDiagram
    actor user as User

    box Internal Service
        participant app as Web Application
    end

    box Dandy
        participant workflow as Workflow
        participant agent as Agent
        participant tool as Tool
    end

    box External Services
        participant llm as LLM Service
        participant db as Database
    end

    user ->>+ app: Request: Create Work Order
    user ->> user: Action: Works on Other Parts of the Work order
    app ->> app: Process: Work Order
    app ->>+ workflow: Send: Current Work Order
    deactivate app
    workflow ->> workflow: Process: Create Job
    workflow ->> workflow: Process: Start Step 1
    workflow ->>+ tool: Request: Other Work Orders
    tool ->>+ db: Query: Other Work Orders
    db -->>- tool: Result: Other Work Orders
    tool -->>- workflow: Return: Other Work Orders Schema Data
    workflow ->> workflow: Process: Start Step 2
    workflow ->>+ agent: Send: Current & Other Work Orders as Prompt
    agent ->>+ llm: Request: Compare Current & Other Work Orders
    llm -->>- agent: Result: Related Other Work Orders
    agent ->> agent: Process: LLM Result into Schema Data
    agent -->>- workflow: Return: Filtered Work Orders Schema Data
    workflow ->> workflow: Process: Filtered Work Orders Result
    workflow -->>- app: Return: Work Orders
    activate app
    app -->> user: Response: Related Work Orders
    deactivate app

```