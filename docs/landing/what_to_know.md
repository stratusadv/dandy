# What to Know

Our guides are here to help you understand all the critical parts of Dandy and get you discovering all the cool features that are available to you.

!!! tip

    Alot of the information in this guide will reference our [Example Project](https://github.com/stratusadv/dandy/tree/main/example){:target="_blank"} project.
    We recommend that you go through the contents while reading the different sections to reinforce your understanding of Dandy.

## Pydantic = Friend!

We have a class called `BaseIntel` that directly inherits from the pydantic `BaseModel` class.
This class has extended functionality and naming to give more separation of concerns between Dandy code and your code.

This project critically relies on the use of pydantic to handle the flow and validation of data with your artificial intelligence systems. 
Make sure you have a good foundation on the use of pydantic before continuing.

Please visit [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/){:target="_blank"} for more information on pydantic.

## Python Things to Know

The following list of concepts are good to understand before you start using Dandy:

- __Typing__ - Dandy requires the use of [Typing](https://docs.python.org/3/library/typing.html){:target="_blank"} in a lot of its functionality.
- __Classes__ - A strong understanding of [Classes](https://docs.python.org/3/tutorial/classes.html){:target="_blank"} will go a long way to make Dandy easier to develop.

## Pyright Also Friend!

We highly recommend using [Pyright](https://microsoft.github.io/pyright/#/){:target="_blank"} during development with Dandy.
Pyright is a great tool to help ensure that you are following the best practices for python development when using Dandy.

