## Using aka.outcome

aka.outcome introduces `Result` and `Option` similar to Rust's `std::result::Result` ([Introduction](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html)) and `std::option::Option` ([Introduction](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html#the-option-enum-and-its-advantages-over-null-values)).  

This implementation is largely based on [mtdowling/outcome](https://github.com/mtdowling/outcome) ([Document](https://mtdowling.com/outcome/)) with these major changes:  

1. `Result:andThen(f)` is introduced. This method alongside `Result:orElseOther(f)` should be the most convenient way to write logics with the absence of Rust's `match`.  

2. `o(...)` is introduced to convert general Lua function return into `Result` in addition to `pcall(...)` from mtdowling/outcome. If function like `io.open` returns `false` or `nil`, it will capture the error message following the `false` or `nil` into an `Err`. If the function's first return value is `true`, it will pack all the data after `true` into an `Ok`. If the function's first return value is not a boolean, it will pack everything into an `Ok`.  

3. All `resultProvider`, `valueProvider` functions from mtdowling/outcome are now fed with the value inside either the `Ok` or `Err`.  

4. `Option:mapOr` and `Option:mapOrElse` now returns the value instead of `Some` value as in mtdowling/outcome.  
