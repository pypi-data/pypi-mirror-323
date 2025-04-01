% Facts
man(marcus).
pompeian(marcus).
roman(X) :- pompeian(X).
ruler(caesar).

% Rules
loyal_or_hate(X, caesar) :- roman(X), (loyal_to(X, caesar); hate(X, caesar)).
loyal_to(X, Y) :- person(X), Y \= caesar.
hate(X, caesar) :- roman(X), \+ loyal_to(X, caesar).

% Assassination rule
try_assassinate(X, Y) :- \+ loyal_to(X, Y), ruler(Y).

% Persons
person(marcus).
person(caesar).