<p align="center">
  <img class="dandy-logo" src="/static/img/dandy_logo_512.png" />
</p>

# AI Development Made Easierish...

Dandy is an intelligence framework for developing programmatic solutions using artificial intelligence. 
It's opinionated, simple and designed to be incredibly pythonic putting the project and developers first.

!!! warning

    Make sure to go through all the sections in our getting started guide to ensure you are fully understanding the concepts and best practices.
    This is critical before you start using Dandy as it's a very opinionated framework and intelligence development is a unique process.

## Yet Another AI Framework?

Intelligence programming is a very different experience than conventional programming as it's very probabilistic.
Based on our experience most of the existing frameworks / libraries are designed to focus more on deterministic outcomes which is not realistic or in our opinion, or beneficial to developers. 

We created Dandy to focus on the flow and validation of data with your artificial intelligence systems to allow you to embrace the probabilistic nature of intelligence.
Our approach is to focus on batteries included with strong tooling to help build great interactions and lowers the barrier to entry for developers.

## Pillars of Dandy

- __Simple__ - Intelligence programming is complex by nature, and we want Dandy to get out of your way as much as possible.
- __Pythonic__ - We want everything Dandy can do to be as pythonic as possible leaving the developer to focus on their own code.
- __Opinionated__ - Our goal is to provide as many of the answers as possible along with working solutions that allow developers to focus on maintaining their agency while being informed.
- __Developer First__ - All features added to Dandy must make the developer's life easier and reduce complexity.
- __Batteries Included__ - Dandy comes with batteries included with strong tooling to help build great interactions and lowers the barrier to entry for developers.
- __Scalable__ - Every design choice in Dandy is about the future and making sure developers can scale their projects as needed.

## Pydantic = Friend!

We have a class called `BaseIntel` that directly inherits from the pydantic `BaseModel` class.
This class has extended functionality and naming to give more separation of concerns between Dandy code and your code.

This project critically relies on the use of pydantic to handle the flow and validation of data with your artificial intelligence systems. 
Make sure you have a good foundation on the use of pydantic before continuing.

Please visit [https://docs.pydantic.dev/latest/](https://docs.pydantic.dev/latest/){:target="_blank"} for more information on pydantic.

## Pyright Also Friend!

We highly recommend using [Pyright](https://microsoft.github.io/pyright/#/){:target="_blank"} during development with Dandy.
Pyright is a great tool to help ensure that you are following the best practices for python development when using Dandy.


