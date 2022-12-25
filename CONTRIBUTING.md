## CONTRIBUTING.md

For modifications in `macros` and `modules`, please always fork from and merge to `dev` branch. For modifications in `scripts`, please always fork from and merge to `master` branch.  

Normally one would not need to worry about Dependency Control. Akatsumekusa will manually confirm the versions and GitHub Actions will automatically generate `DependencyControl.json` on merge. However, if one has push access to the repository and wants to push directly to `dev`, they must setup their Git Hooks via `git config core.hooksPath .hooks/hooks` and make sure that the requirements are satisfied with `python -m pip install -r .hooks/requirements.txt`.  
