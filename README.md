# SSW LaTeX Exercise CI

[![status](https://github.com/SSW-JKU/latex-exercise-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/SSW-JKU/latex-exercise-ci/actions/workflows/ci.yml)

This action, used at the [SSW](https://ssw.jku.at/) at the [JKU](https://www.jku.at/), is configured to automatically build exercise files upon commit and (to prevent unnecessary rebuilds) cache the results.
We group exercise files into two categories: _lesson_ and _exercise_ (homework) materials.
Hence, the action expects these materials to adhere to this folder structure:

`<semester>/<exercise_nr>/Unterricht/` or `<semester>/<exercise_nr>/Aufgabe/`

where `Unterricht` denotes _lesson_ materials and `Aufgabe` denotes _exercise_ materials.

Examples:

```
21WS/UE01/Aufgabe
22WS/UE10/Unterricht
```

_Note: For exercises where no homework is given, the `Aufgabe` folder may be omitted_

During each build, the action iterates over the **exercises** of the configured **semester** and performs three separate **builds** per exercise:

- building the _lesson_ materials
- building the _exercise_ materials
- building the _solution_ (i.e., the _exercise_ materials that also include the expected results)

These typically result in three PDF files that are subsequently added to the corresponding folder in the repository, which causes a subsequent commit by the build bot.
The builds are performed in a prepared CI environment that installs (parts of) [TeX Live](https://tug.org/texlive/) to support our requirements.
As preparing this environment is costly (in terms of CI build time), the action tries to cache as much as possible from this process (e.g., the TeX Live packages) and also tries to prevent excessive rebuilds of the materials.
Therefore, the build process generates a hash of its included files per _exercise_ and also pushes it to the repo (local `.checksum` files in the `<exercise_nr>` directories). If in a subsequent invocation of the build process (another commit) the given files of the exercises _have not_ changed, the checksum should match and the exercise is skipped during the build process. Hence, the `.checksum` files should never be manually changed, unless you want to force a rebuild (e.g., by deleting the `.checksum` file).

**Note:**: A correct checksum without proper PDFs *does not* trigger a rebuild. Since checksum files are only generated once the PDFs are successfully built, this should not occur without manual intervention.

## Configuration

The action is customizable via the following inputs:

- `python_version` (type: `string`, default: `"3.13"`)

  Specifies the Python version used to perform the build task.

- `texlive_version` (type: `string`, default: `"2024"`)

  Specifies the TeX Live version that is used for creating the PDFs.

- `texlive_packages` (type: `list of strings`, default: `"scheme-basic"`)

  Denotes the TeX Live packages that are required for the build process.
  When adding new dependencies, keep in mind that the CI runs on Ubuntu - the TeX Live package names may therefore differ from your local installation.

- `config_file_name` (type: `string (path-to-file)`, default: `".lecture-build-ci.json"`)

  Specifies the configuration file path, a JSON file that defines:

  ```jsonc
  {
    /*
     * current semester folder (cf. <semester>) - only files within this
     * root directory are considered for the build.
     */
    "activeSemester": "<str>",
    /*
     * TeX entry points for the build.
     */
    "entryPoints": {
      "exercise": "<str>", // exercise entry point (also for solution build).
      "lesson": "<str>" // lesson entry point
    },
    /*
     * list of exercises (cf. <exercise_nr>) that are considered for the build
     * (useful if not all exercises are ready to be built yet)
     */
    "exercises": [
      "<str>", // exercise 1 folder name
      "<str>", // exercise 2 folder name
      // ...
    ]
  }
  ```

- `commit_user_name` (type: `string`, default: `"LaTeX Exercise CI Build[bot]"`)

  Configures the name of the user (or bot) that pushes the commit with the updated/generated PDFs.

- `commit_user_email` (type: `string`, default: `"latex-exercise-ci-bot@users.noreply.github.com"`)

  Configures the email address of the user (or bot) that pushes the commit with the updated/generated PDFs.

### Configuring builds for a new semester

When initiating a new semester, usually the only remaining step is to adapt the `"activeSemester"` variable in the file specified in `config_file_name`. If the number of exercises has changed compared to the previous year, the list of `"exercises"` must also be reconfigured.

## Possible reasons for TeX build errors

- Do not use ² (squared) in your .tex files, as the build system seems to not like that (due to encoding problems)

## Build results and error handling

The build process typically continues over all exercises even if an individual build fails. This may be due to TeX build errors, or if the configured `"entryPoints"` file is missing. Note that if the _lesson_ or _exercise_ directory is missing as a whole, the build process treats it as a deliberate omission (e.g., if there is no homework/no actual lesson materials required) and does not report a failure.

If a build fails, changes to the directory (e.g., generated PDFs) are rolled back and the `.checksum` naturally remains unchanged.

Even if some builds succeed, the build bot will still push changes; however, the task as a whole will be reported as a failure.
