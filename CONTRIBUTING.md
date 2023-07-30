## CONTRIBUTING.md  

Normally one would not need to worry about Dependency Control. Akatsumekusa will manually confirm the versions and GitHub Actions will automatically generate `DependencyControl.json` on merge. However, if one has push access to the repository and wants to push directly to `master`, they must setup their Git Hooks via `git config core.hooksPath .hooks/hooks` and make sure that the requirements are satisfied with `python -m pip install -r .hooks/requirements.txt`.  

AAE Export uses M4 and sh script to generate final code, make sure to set up Git Hooks as explained above, or manually run `generate.sh` in the three folders to generate the final code before commit.  
