# Dandy Exceptions

## DandyException

This is the base to all exceptions in Dandy.

## DandyCriticalException

All the exceptions that are marked as `Critical` with in Dandy need to be addressed in the development process.
We deliberately wanted a major separation of concerns to make sure there is no confusion when shipping code to production. 

## DandyRecoverableException

When writing your project with Dandy you can attempt to handle all exceptions marked with `Recoverable` in the development process.
This gives a clear line for developers to attempt to handle the exception and recover processes safely knowing we deemed the exception recoverable.

