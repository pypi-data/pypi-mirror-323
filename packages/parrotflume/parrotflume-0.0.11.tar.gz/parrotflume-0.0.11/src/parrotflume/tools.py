import json
import re
from datetime import datetime


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get the current (today's) date",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sympy_simplify",
            "description": "Simplify a mathematical expression using sympy.simplify",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "mathematical expression to simplify, using sympy syntax"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sympy_solve",
            "description": "Solve a mathematical expression using sympy.solve",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "mathematical expression to solve, using sympy syntax"
                    },
                    "variable": {
                        "type": "string",
                        "description": "variable to solve for, using sympy syntax"
                    }
                },
                "required": ["expression", "variable"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sympy_integrate",
            "description": "Integrate a mathematical expression using sympy.integrate",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "mathematical expression to integrate, using sympy syntax"
                    },
                    "variable": {
                        "type": "string",
                        "description": "variable of integration, using sympy syntax"
                    }
                },
                "required": ["expression", "variable"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sympy_differentiate",
            "description": "Differentiate a mathematical expression using sympy.diff",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "mathematical expression to differentiate, using sympy syntax"
                    },
                    "variable": {
                        "type": "string",
                        "description": "variable of differentiation, using sympy syntax"
                    },
                    "order": {
                        "type": "integer",
                        "description": "order of differentiation (optional, default is 1)"
                    }
                },
                "required": ["expression", "variable"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "regex_match",
            "description": "Applies a regex pattern to a text and returns the matches",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "regex pattern to apply."
                    },
                    "text": {
                        "type": "string",
                        "description": "text to search within."
                    }
                },
                "required": ["pattern", "text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_chars",
            "description": "Counts the number of characters in a string",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "string whose characters are to be counted",
                    }
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_substring_occurrences",
            "description": "Counts the number of occurrences of a substring in a string",
            "parameters": {
                "type": "object",
                "properties": {
                    "string": {
                        "type": "string",
                        "description": "string to search within"
                    },
                    "substring": {
                        "type": "string",
                        "description": "substring to count occurrences of"
                    }
                },
                "required": ["string", "substring"]
            }
        }
    },
]


def handle_get_current_date(messages, tool_call_id):
    result = datetime.now().strftime("%Y-%m-%d")
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "get_current_date",
        "content": result
    })


def handle_sympy_simplify(messages, arguments, tool_call_id):
    from sympy.parsing.sympy_parser import parse_expr
    from sympy import simplify
    try:
        expr = parse_expr(arguments["expression"])
        content = str(simplify(expr))
    except Exception as e:
        content = str(e)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "sympy_simplify",
        "content": content
    })


def handle_sympy_solve(messages, arguments, tool_call_id):
    from sympy.parsing.sympy_parser import parse_expr
    from sympy import solve, sympify, Eq
    try:
        equation = arguments["expression"]
        variable = arguments["variable"]

        if "=" in equation:
            left, right = equation.split("=", 1)
            left_expr = parse_expr(left.strip())
            right_expr = parse_expr(right.strip())
            eq = Eq(left_expr, right_expr)
        else:
            eq = parse_expr(equation)

        solution = solve(eq, sympify(variable))
        content = str(solution)
    except Exception as e:
        content = str(e)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "sympy_solve",
        "content": content
    })


def handle_sympy_integrate(messages, arguments, tool_call_id):
    from sympy.parsing.sympy_parser import parse_expr
    from sympy import sympify, integrate
    try:
        expression = arguments["expression"]
        variable = sympify(arguments["variable"])

        expr = parse_expr(expression)
        result = integrate(expr, variable)
        content = str(result)
    except Exception as e:
        content = str(e)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "sympy_integrate",
        "content": content
    })


def handle_sympy_differentiate(messages, arguments, tool_call_id):
    from sympy.parsing.sympy_parser import parse_expr
    from sympy import sympify, diff
    try:
        expression = arguments["expression"]
        variable = sympify(arguments["variable"])
        order = arguments.get("order", 1)

        expr = parse_expr(expression)
        result = diff(expr, variable, order)
        content = str(result)
    except Exception as e:
        content = str(e)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "sympy_differentiate",
        "content": content
    })


def handle_regex_match(messages, arguments, tool_call_id):
    try:
        pattern = arguments["pattern"]
        text = arguments["text"]

        result = re.findall(pattern, text)
        content = str(result)
    except Exception as e:
        content = str(e)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "regex_match",
        "content": content
    })


def handle_count_chars(messages, arguments, tool_call_id):
    try:
        text = arguments["text"]
        content = str(len(text))
    except Exception as e:
        content = str(e)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "count_chars",
        "content": content
    })


def handle_count_substring_occurrences(messages, arguments, tool_call_id):
    try:
        text = arguments["string"]
        substring = arguments["substring"]
        content = str(text.count(substring))
    except Exception as e:
        content = str(e)

    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": "count_substring_occurrences",
        "content": content
    })


def handle_tool_call(messages, tool_call, do_print=False):
    if tool_call.function.arguments:
        args = json.loads(tool_call.function.arguments)
    else:
        # Claude via openrouter sends an empty string as argument for argument-less tool call
        args = None
    if do_print:
        print(f"[{tool_call.function.name} called]")

    if tool_call.function.name == "get_current_date":
        handle_get_current_date(messages, tool_call.id)
    elif tool_call.function.name == "sympy_simplify":
        handle_sympy_simplify(messages, args, tool_call.id)
    elif tool_call.function.name == "sympy_solve":
        handle_sympy_solve(messages, args, tool_call.id)
    elif tool_call.function.name == "sympy_integrate":
        handle_sympy_integrate(messages, args, tool_call.id)
    elif tool_call.function.name == "sympy_differentiate":
        handle_sympy_differentiate(messages, args, tool_call.id)
    elif tool_call.function.name == "regex_match":
        handle_regex_match(messages, args, tool_call.id)
    elif tool_call.function.name == "count_chars":
        handle_count_chars(messages, args, tool_call.id)
    elif tool_call.function.name == "count_substring_occurrences":
        handle_count_substring_occurrences(messages, args, tool_call.id)
