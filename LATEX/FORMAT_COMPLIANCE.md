# Thesis Formatting Compliance Notes

This LaTeX workspace is formatted to resemble a restrained German economics master thesis. The reference thesis supplied by the user is used only for production conventions, not for prose, argument structure, literature content, or interpretation.

## Non-Negotiable Structure

The compiled document order is:

1. Title page
2. Abstract
3. Contents
4. List of Figures
5. List of Tables
6. List of Abbreviations
7. List of Symbols
8. Chapter 1: Introduction
9. Chapter 2: Literature Review
10. Chapter 3: Methodology
11. Chapter 4: Data
12. Chapter 5: Results
13. Chapter 6: Robustness & Diagnostics
14. Chapter 7: Discussion
15. Chapter 8: Conclusion
16. Appendix A: Additional Material
17. References
18. Selbststaendigkeitserklaerung

Acknowledgements are optional and are not included unless the author supplies final text.

## Visual Standard

- Use a restrained serif thesis style: 12 pt body text, Times-like font, 1.5 line spacing, justified paragraphs, and centered bottom page numbers.
- Use Roman page numbers for front matter and Arabic page numbers for the main text, appendix, references, and declaration.
- Keep the title page unnumbered and compact. Candidate metadata belongs lower on the page; supervisor and second reviewer belong in the administrative block.
- Use flat chapter headings such as `1. Introduction`, not oversized default LaTeX `Chapter 1` display headings.
- Keep section and subsection hierarchy bold, simple, and black. Do not add color, decorative rules, or oversized display typography.
- Keep contents, lists, and page numbers generated automatically with dotted leaders.

## Figures, Tables, And Appendix

- Use `\thesisfigure` for figures so every figure is linked to `results/final/figures/...` with a visible source note.
- Use `\artifacttable` for repository-backed table artifacts. Do not hand-copy CSV contents into LaTeX unless a final thesis-facing table is intentionally typeset.
- Captions should be concise. The source path carries reproducibility context; the caption should not become a paragraph.
- Appendix A must remain organized as:
  - A.1 Additional Figures
  - A.2 Additional Tables
  - A.3 Technical Derivations
- Core empirical claims and primary interpretation belong in the main chapters, not the appendix.

## Citation And Bibliography

- Use one author-year system consistently: `biblatex` with `authoryear-comp` and `biber`.
- Use `\textcite{...}` for narrative citations and `\parencite{...}` for parenthetical citations.
- Keep references alphabetized by the bibliography engine.
- Do not mix numeric citations, footnote-only citations, and author-year citations.

## Administrative Safety

- Keep personal metadata centralized in `preamble/metadata.tex`.
- Before submission, replace bracketed metadata values for candidate name, submission date, thesis period, supervisor, and second reviewer.
- Keep the Selbststaendigkeitserklaerung page present and visually separate after references.
- Do not copy wording from the reference thesis. Only formatting logic and administrative architecture are reusable.
