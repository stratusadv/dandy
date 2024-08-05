# Terminology

### Appliance

A class or object that can be used by an agent or prompts to complete specific tasks

- Gadget
- Instrument
- Device

### Database (In Memory or Storage)

A structured data storage system used to keep track of jobs, tasks and tickets

### Input

Information and data provided by the client

- Instruction

### Processor

This would have both an input and output.

The input method would process input and convert it into a job and should return a ticket to the system.

The output method would process what ever the result of the job was into the desired output for the program

- Handler
- Broker (This is designed for transactions that are resolved immediately like messaging)
- Coordinator (More accurate)
- Manager (Probably Correct)

### Output

Result in the form of information and data provided back to the client after processing the input

- Yield

### Structure

Class used to create an input or output object based on the completion of a job

- Complex
- Formation
- Blueprint

### Structure Data

The values that make up the values of a structure to be used on input or output

- Complex Data
- Formation Data
- Blueprint Data

### Prompt

The instructions for a Large Language Model created during the process

### Prompt Segment

A smaller piece of a prompt that is used to assemble a full prompt.

- Prompt Sentence
- Prompt Snippet (Think this is the closest)
- Prompt Slice
- Prompt Division
- Prompt Piece

### Reflection

The result of analyzing a prompt request versus the response.

- After Thought

### LLM

A Large Language Model that can interpret a prompt into a text

### LLM Handler

The process that handles the interaction with an LLM model

- Prompter
- Broker
- Operator
- Driver

### Department (High Level Module)

This is the grouping used to put together agents to accomplish a task

- Agency
- Facility (Probably Better)

### Agent

Small program that has specific prompts and code that make it good at a specific set of jobs utilizing an LLM for processing

- Assistant
- Handler

### Ticket

This object is provided from a department when ever a job is started as to reference the job progress

- Voucher
- Record
- Receipt

### Tool

Specific functions to be used by agents and prompts to complete specific tasks

- Gadget
- Appliance
- Mechanism
- Utility

### Flow

The order of operation for the jobs to be completed along with specific requirements.

- Pipeline
- Path

### Job

The assembled set of tasks required to complete what is laid out in the input

- Activity
- Operation
- Assignment
- Project Action

### Job Cost

This would be a rough calculation of the token and compute time used to complete a job

- Job Value
- Job Worth
- Job Price

### Task

A smaller more specific part of a job that needs to be done to consider a job complete

- Effort

### Task Cost

The quick break down of the compute and token usages required for the task

- Task Value
- Task Worth
- Task Price

### Utility

Functions that are internal to the library to help manage and control the flow of data.

### System

The central part of the whole program that will orchestrate all the operations required in this library.