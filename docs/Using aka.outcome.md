## Using aka.outcome

aka.outcome introduces `Result` and `Option` similar to Rust's `std::option::Option` ([The Rust Programming Language](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html#the-option-enum-and-its-advantages-over-null-values) | [Reference](https://doc.rust-lang.org/stable/std/option/)) and `std::result::Result` ([The Rust Programming Language](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) | [Reference](https://doc.rust-lang.org/std/result/)).  

If you are familiar with some other languages, these are equivalents of `Result` and `Option` in those languages:  
– C++: [`std::optional`](https://en.cppreference.com/w/cpp/utility/optional) and [`std::expected`](https://en.cppreference.com/w/cpp/utility/expected)  
– C#: [Nullable](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/nullable-value-types)  
– Swift: [Optional](https://developer.apple.com/documentation/swift/result) and [Result](https://developer.apple.com/documentation/swift/result)  
– Kotlin: [Nullable](https://kotlinlang.org/docs/null-safety.html)  

aka.outcome is forked from [mtdowling/outcome](https://github.com/mtdowling/outcome). You can read mtdowling/outcome's [document](https://mtdowling.com/outcome/) but note these major changes in aka.outcome:  

1. `Result:andThen(f)` and `Option:andThen(f)` is introduced. This method alongside `Result:orElseOther(f)` and `Option:orElseOther(f)` should be the most convenient way to write logics with the absence of Rust's `match`.  

2. `o(...)` is introduced to convert general Lua function return into `Result` in addition to `pcall(...)` from mtdowling/outcome. If function like `io.open` returns `false` or `nil`, it will capture the error message following the `false` or `nil` into an `Err`. If the function's first return value is `true`, it will pack all the data after `true` into an `Ok`. If the function's first return value is not a boolean, it will pack everything into an `Ok`.  

3. `mutli_pcall(...)` is also introduced and it will pack all the returns from the function into a table.  

4. All `resultProvider`, `valueProvider` functions from mtdowling/outcome are now fed with the value inside either the `Ok` or `Err`.  

An examples of using aka.outcome is [aka.config2](../modules/aka/config2/config2.lua).  
