# Formal proof validator

Formal logic proof verifier.

## TODO

* Spaces to be possible in formulas.
* The tokenizer should return the tokens as strings only (not formula types).
  The next steps should recognize which strings are connectives and relations.
  This allows connectives and relations to be more than 1 character long.
* Documentation on how to use it, with examples.
* Docstring for functions, even to implementation functions.
* 100 % code coverage with tests.
* Update tests to make every rule's failing case to test
  every way they can fail.
  This means that every line in `Formula.eq_with_variable_map` and
  `Formula.is_variable_in` is hit for every failing case.
* Use `elif`s in rules, not just simple `if`s with `return`.
* Better error messages, with more information.
* Do not use exceptions, but return with the error.

## Licensing

This software is distributed under the GNU General Public License (GPL) version 3. You can find the full text of the license in the [LICENSE](LICENSE.txt) file.
