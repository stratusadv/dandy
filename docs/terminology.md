# Terminology

### Appliance (Final)

A class or object that can be used by an agent or prompts to complete specific tasks

- Gadget
- Instrument
- Device

### Database (In Memory or Storage)

A structured data storage system used to keep track of jobs, tasks and tickets

### Input (Final)

Information and data provided by the client

- Instruction

### Coordinator (Final)

This would have both an input and output.

The input method would process input and convert it into a job and should return a ticket to the system.

The output method would process what ever the result of the job was into the desired output for the program.

- Handler
- Broker (This is designed for transactions that are resolved immediately like messaging)
- Manager (So close but this represents a point of responsibility versus )
- Processor

### Output (Final)

Result in the form of information and data provided back to the client after processing the input

- Yield

### Schema (Final)

Class used to create an input or output object based on the completion of a job and structure LLM requests and responses

- Complex
- Formation
- Blueprint
- Structure

### Schema Data / Instance (Final)

The data that make up the values of a schema after it's been processed to be used in the pipeline or job

- Complex Data
- Formation Data
- Blueprint Data
- Structure Data

### Prompt (Final)

The instructions for a Large Language Model created during the process

### Prompt Snippet (Final)

A smaller piece of a prompt that is used to assemble a full prompt.

- Prompt Sentence
- Prompt Snippet (Think this is the closest)
- Prompt Slice
- Prompt Division
- Prompt Piece

### Reflection (Final)

The result of analyzing a prompt request versus the response.

- After Thought

### LLM (Final)

A Large Language Model that can interpret a prompt into a text

### LLM Handler (Final)

The process that handles the interaction with an LLM model

- Prompter
- Broker
- Operator
- Driver

### Department (Final)

This is the grouping used to put together agents to accomplish a task

- Agency
- Facility (Probably Better But not Programmatically Verbose to me)

### Agent (Final)

Small program that has specific prompts and code that make it good at a specific set of jobs utilizing an LLM for processing

- Assistant
- Handler

### Ticket (Final)

This object is provided from a department when ever a job is started as to reference the job progress

- Voucher
- Record
- Receipt

### Tool (Final)

Specific functions to be used by agents and prompts to complete specific tasks

- Gadget
- Appliance
- Mechanism
- Utility

### Pipeline (Final)

The order of operation for the jobs to be completed along with specific requirements.

- Flow
- Path

### Job (Final)

The assembled set of tasks required to complete what is laid out in the input

- Activity
- Operation
- Assignment
- Project Action

### Task (Final)

A smaller more specific part of a job that needs to be done to consider a job complete

- Effort

### Cost (Final)

The breakdown of anything into a compute / token / time / money cost for evaluation of a service

### Utility (Final)

Functions that are internal to the library to help manage and control the flow of data.

### System (Final)

The central part of the whole program that will orchestrate all the operations required in this library.