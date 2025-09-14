# Read This First

Our documentation is here to help you understand all the critical parts of Dandy and get you discovering all the cool features that are available.

Take some time to read the couple sections below as they will provide you with information that will make it easier to learn how to use Dandy.

## Pydantic = Friend!

We have a class called `BaseIntel` that directly inherits from the pydantic `BaseModel` class.
This class has extended functionality and naming to give more separation of concerns between Dandy code and your code.

!!! tip

    Pydantic is an amazing library that makes handling data in python much easier.
    Every developer should take time to learn the basics and understand how pydantic can benefit your project.

Dandy critically relies on the use of pydantic like objects to handle the flow and validation of data with your artificial intelligence systems. 
Make sure you have a good foundation on the use of pydantic before continuing.

Please visit [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/){:target="_blank"} for more information on pydantic.

## Python Things to Know

The following list of concepts are good to understand before you start using Dandy:

- __Typing__ - Dandy requires the use of [Typing](https://docs.python.org/3/library/typing.html){:target="_blank"} in a lot of its functionality.
- __Classes__ - A strong understanding of [Classes](https://docs.python.org/3/tutorial/classes.html){:target="_blank"} will go a long way to make Dandy easier to develop.

## Pyright Also Friend!

We highly recommend using [Pyright](https://microsoft.github.io/pyright/#/){:target="_blank"} during development with Dandy.
Pyright is a great tool to help ensure that you are following the best practices for python development when using Dandy.

!!! info

    The use of pyright is recommended but we understand people have preferences on coding, 
    and that's ok but we do suggest you have some type checking enabled during development.

