# Inventory Management Engine

## Overview

The Inventory Management Engine is an object-oriented Python application
designed to demonstrate core software engineering concepts including:

- Object-oriented programming
- Inheritance
- Encapsulation
- Polymorphism
- Abstract classes
- Custom exceptions
- JSON persistence
- CSV persistence
- Unit testing
- Code coverage

## Features

### Product Management

The system supports:

- Physical products
- Digital products
- Adding products
- Removing products
- Searching products
- Updating stock
- Calculating inventory value

### Error Handling

Custom exceptions are used for:

- Invalid product data
- Duplicate products
- Missing products
- Invalid quantities
- Insufficient stock
- Storage errors

### Data Persistence

The inventory can be saved and loaded using:

- JSON
- CSV

## OOP Concepts

### Encapsulation

Product attributes are stored using private variables.

Example:

```python
self.__price
self.__quantity