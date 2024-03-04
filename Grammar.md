* Лексический анализатор ---point
* Стадия предобработки --- физические строки превращаются в логические --- пары (метка, текст оператора) point
* Стадия синтаксического разбора разбирает вторые компоненты пар
* Стадия семантического анализа
  - проверить что идентификатор не длинее 6 символов
  - в том числе, проверяет наличие меток у FORMAT
  - проверяет, что нет повторяющихся меток, что DO, IF и GOTO ссылаются на существующие метки

```
Program -> PROGRAM identifier statement_list END
statement_list -> statement | statement statement_list
statement -> assigment_statement
            | read_statement
            | print_statement
            | format_statement
            | go_to_statement
            | continue_statement
            | if_statement
            | dimension_statement
assigment_statement -> identifier '=' arithmetic_expression | identifier '(' expression_list ')' '=' arithmetic_expression
read_statement -> READ  format_identifier ',' identifier_list
print_statement -> PRINT format_identifier ',' expression_list
format_statement -> FORMAT  format_list
go_to_statement -> GOTO label
continue_statement -> CONTINUE
if_statement -> IF '(' artithmetic_expression ')' label ',' label ',' label
dimension_statement -> DIMENSION array_declaration_list
expression_list -> arithmetic_expression | arithmetic_expression ',' expression_list
arithmetic_expression -> term | arithmetic_expression '+' term | arithmetic_expression '-' term
term -> exponentiation | term '*' exponentiation | term '\' exponentiation
exponentiation -> factor | factor '**' exponentiation
factor -> number | identifier | '(' artithmetic_expression ')' | call
call -> identifier '(' expression_list ')'
format_list ->  '(' repetable_format_item ')'
repetable_format_item -> format_item | repeated_format_group | format_item ',' repetable_format_item
repeated_format_group -> POSITIVE '(' format_item_list ')' | POSITIVE format_item 
format_item_list -> format_item | format_item ',' format_item_list
format_item -> 'I' INTEGER
                | 'F' INTEGER '.' INTEGER
                | 'E' INTEGER '.' INTEGER
                | INTEGER 'X'
                | INTEGER 'H' text
text -> character | character text      
character -> ALL_SYMBOLS    
identifier_list -> identifier | identifier ',' identifier_list
array_declaration_list -> array_declaration | array_declaration ',' array_declaration_list
array_declaration -> identifier '(' INTEGER ')'
number -> INTEGER | REAL

identifier -> STRING
format_identifier -> label
label -> POSITIVE

#Задаем регуляркой
letter -> A | B | C... | Z

digit -> 0 | 1 | 2... | 9

real_number -> digits '.' dogits optional_exponent
                | digits '.' optional_exponent
                | '.' digits optional_exponent
optional_exponent -> ε | 'E' signed_integer
signed_integer -> optional_sign digits
optional_sign -> '+' | '-' | ε
```