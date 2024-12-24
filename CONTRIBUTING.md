## CONTRIBUTING.md  

Akatsumekusa welcomes all bug reports and feature requests. Make an [issue](https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/issues) or [pull request](https://github.com/Akatmks/Akatsumekusa-Aegisub-Scripts/pulls) here or contact me through social platforms.  

Normally one would not need to worry about Dependency Control. GitHub Actions will automatically generate `DependencyControl.json` on merge. However, if somebody has push access to the repository and wants to push directly to `master`, they must setup their Git Hooks via `git config core.hooksPath .hooks/hooks` and make sure that the requirements are satisfied with `python -m pip install -r .hooks/requirements.txt`.  

AAE Export uses M4 and sh script to generate final code, make sure to set up Git Hooks as explained above, or manually run `generate.sh` in the three folders to generate the final code before commit.  
