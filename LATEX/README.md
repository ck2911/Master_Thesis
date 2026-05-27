# LaTeX Thesis Workspace

This directory is the dedicated thesis authoring and compilation environment for `THESIS_Model`.

The empirical pipeline remains the single source of truth. LaTeX consumes the canonical processed data, figures, tables, diagnostics, robustness outputs, and mechanism outputs from the repository root by relative path. No figures or tables are duplicated inside `LATEX`.

## Structure

```text
LATEX/
  main.tex                 thesis entry point
  preamble/                packages, formatting, commands, metadata
  frontmatter/             title page, abstract, lists, optional acknowledgements, declaration
  chapters/                modular thesis chapters
  appendix/                appendix modules
  bibliography/            biblatex database and citation notes
  build/                   generated PDF, aux files, and logs
  scripts/                 artifact checks and compile helper
```

## Compile

From `LATEX/`:

```bash
make pdf
```

or:

```bash
scripts/compile.sh
```

The build uses `pdflatex` with `biblatex` and `biber`, configured through `latexmkrc`.

Generated files are isolated as follows:

- editor/build PDF and SyncTeX source: `build/main.pdf`, `build/main.synctex.gz`
- stable root PDF entry point: `main.pdf` symlinked to `build/main.pdf`
- auxiliary files, biber outputs, latexmk state, and logs: `build/`

Clean build files with:

```bash
make clean
```

Remove the generated PDF as well:

```bash
make cleanall
```

## Bibliography Workflow

References live in `bibliography/references.bib`. The thesis uses:

```latex
\usepackage[backend=biber,style=authoryear-comp]{biblatex}
```

Add citations with `\textcite{Key}` or `\parencite{Key}`. Run `make pdf`; `latexmk` calls `biber` automatically when needed.

The initialized bibliography contains core placeholders for monetary transmission, high-frequency identification, external instruments, and financialization. See `bibliography/citation_notes.md` before submission.

The compiled front matter follows the department thesis order: title page, abstract, contents, list of figures, list of tables, list of abbreviations, list of symbols, main text, appendix, references, and Selbststaendigkeitserklaerung. Acknowledgements remain optional and are not included by default.

## Figure and Table Integration

Canonical outputs are imported from:

- figures: `../results/final/figures/`
- main CSV tables: `../results/final/tables/`
- diagnostics: `../results/final/diagnostics/`
- robustness: `../results/final/robustness/`
- regime outputs: `../results/final/regime/`
- stability outputs: `../results/final/stability/`
- uncertainty outputs: `../results/final/uncertainty/`
- mechanism outputs: `../results/final/mechanism/`
- processed data: `../data/processed/eu_de/`

Use the thesis macros in `preamble/commands.tex`:

```latex
\thesisfigure{baseline/monthly_irf_ln_dax_real_de.png}{Caption text.}{fig:baseline-dax}

\artifacttable
  {Table caption}
  {tab:label}
  {../results/final/tables/normalized_irf_outputs.csv}
  {How the artifact is used in the thesis.}
```

The `\thesisfigure` macro imports the canonical image directly. The `\artifacttable` macro registers a CSV artifact in the thesis without copying or hand-editing its contents.

## Helper Scripts

Check that canonical outputs use deterministic filenames:

```bash
make check
```

Emit LaTeX snippets for available figures or tables:

```bash
make figures
make tables
```

These scripts inspect the repository outputs and print snippets. They do not copy binaries or rewrite pipeline products.

## Chapter Organization

- Chapter 1: Introduction
- Chapter 2: Literature Review
- Chapter 3: Theoretical Framework and Methodology
- Chapter 4: Data
- Chapter 5: Results
- Chapter 6: Robustness & Diagnostics
- Chapter 7: Discussion
- Chapter 8: Conclusion
- Appendix A: Additional Material, with additional figures, additional tables, and technical derivations

## Reproducibility Conventions

- Rebuild empirical outputs from the repository root with `python scripts/run_full_pipeline.py`.
- Keep LaTeX passive: it renders canonical artifacts; it does not own empirical outputs.
- Use relative paths only.
- Do not put generated notebook HTML, copied figures, copied CSVs, or exploratory exports in `LATEX`.
- Keep metadata centralized in `preamble/metadata.tex`.
- Keep formatting centralized in `preamble/formatting.tex`.
- Keep notation and artifact path macros centralized in `preamble/commands.tex`.
