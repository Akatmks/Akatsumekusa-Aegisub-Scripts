## CONTRIBUTING.md

For modifications on macros and modules, please always fork from and merge to `dev` branch. For modifications on scripts, please always fork from and merge to `master` branch.  

Normally one would not need to worry about Dependency Control. Akatsumekusa will manually confirm the versions and GitHub Actions will automatically generate `DependencyControl.json` on merge. However, there is also a pre-commit hook in `.hooks/hooks` for anyone who is interested.
