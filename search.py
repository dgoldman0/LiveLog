from enum import Enum
from typing import Optional, List, Union, Tuple
from pyparsing import Word, alphas, nums, Combine, oneOf, Keyword, Optional as PPOptional, Group, infixNotation, opAssoc, ParseResults

class Operator(Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

class QueryNode:
    def __init__(self, operator: Optional[Operator] = None, term: Optional[str] = None):
        self.operator = operator
        self.term = term
        self.children: List[Union['QueryNode', str]] = []

    def __repr__(self):
        if self.term:
            return f"QueryNode(term={self.term})"
        return f"QueryNode(operator={self.operator}, children={self.children})"

# Define search query language grammar
identifier = Word(alphas + "_", alphas + nums + "_")
integer = Word(nums)
date = Combine(integer + '-' + integer + '-' + integer)

# Define keywords and their identifiers
tag = Combine(Keyword("tag:") + identifier)
author = Combine(Keyword("author:") + integer)
date_range = Combine(Keyword("date:") + date + PPOptional(Keyword("to") + date))

# Define search term with combined keywords
search_term = Group(tag | author | date_range | Word(alphas))

# Define boolean operators
boolean_operator = oneOf("AND OR NOT")

# Define the expression using infix notation
search_expression = infixNotation(
    search_term,
    [
        (oneOf("NOT"), 1, opAssoc.RIGHT),
        (oneOf("AND OR"), 2, opAssoc.LEFT),
    ],
)

def parse_query_expression(expression: str) -> QueryNode:
    def _parse(tokens: ParseResults) -> QueryNode:
        if isinstance(tokens, list):
            if len(tokens) == 1:
                return _parse(tokens[0])
            elif len(tokens) == 2:
                return QueryNode(operator=Operator.NOT, children=[_parse(tokens[1])])
            elif len(tokens) == 3:
                left = _parse(tokens[0])
                operator = Operator(tokens[1])
                right = _parse(tokens[2])
                node = QueryNode(operator=operator)
                node.children.extend([left, right])
                return node
        else:
            if "date:" in tokens:
                if "to" in tokens:
                    term = f"{tokens[1]} to {tokens[3]}"
                else:
                    term = tokens[1]
                return QueryNode(term=f"date:{term}")
            return QueryNode(term=str(tokens[0]))

    parsed_tokens = search_expression.parseString(expression, parseAll=False)
    return _parse(parsed_tokens[0])

def construct_sql_query(query_node: QueryNode) -> Tuple[str, List[str]]:
    sql_query = ""
    params = []
    if query_node.term:
        if query_node.term.startswith("date:"):
            date_parts = query_node.term[5:].split(" to ")
            if len(date_parts) == 2:
                sql_query = "(date BETWEEN ? AND ?)"
                params.extend(date_parts)
            else:
                sql_query = "(date = ?)"
                params.append(date_parts[0])
        elif query_node.term.startswith("tag:"):
            sql_query = "(tag = ?)"
            params.append(query_node.term[4:])
        elif query_node.term.startswith("author:"):
            sql_query = "(author = ?)"
            params.append(query_node.term[7:])
        else:
            sql_query = "(keyword = ?)"
            params.append(query_node.term)
    elif query_node.operator:
        if query_node.operator == Operator.NOT:
            child_query, child_params = construct_sql_query(query_node.children[0])
            sql_query = f"NOT ({child_query})"
            params.extend(child_params)
        else:
            left_query, left_params = construct_sql_query(query_node.children[0])
            right_query, right_params = construct_sql_query(query_node.children[1])
            sql_query = f"({left_query} {query_node.operator.value} {right_query})"
            params.extend(left_params)
            params.extend(right_params)
    
    return sql_query, params

# Example usage
expression = "tag:science AND author:123 OR date:2021-01-01 to 2021-12-31"
parsed_query = parse_query_expression(expression)
sql_query, params = construct_sql_query(parsed_query)

print(f"SQL Query: {sql_query}")
print(f"Params: {params}")
