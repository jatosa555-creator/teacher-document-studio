# Quality gates before delivery

## Content and structure

Compare source and output text, tables, pictures, hyperlinks, fields, footnotes, and comments. Distinguish formatting changes from authorised edits. Check all section numbers, names, dates, figures, and quote attributions. For translated content, compare meaning and numerical consistency rather than byte equality.

The supplied formatter's audit verifies body text/field text, math, structural order, annotation anchors, numbering references, original package parts and relationship entries. Parts outside the document model are retained from the source package. Header/footer, notes, comments, numbering and binary payloads remain unchanged except a requested new footer in an empty single-section document. It is a structural check, not proof of correct pagination or of every application feature. Shared style changes may still alter the appearance of protected content.

## Every rendered page

1. **Typography:** Thai vowel/tone marks are complete; no missing-glyph squares; mixed text is legible; body font sizes are consistent.
2. **Hierarchy:** title, headings, body, and attribution have distinct roles; no heading is stranded at the bottom; numbering is coherent.
3. **Spacing:** margins are balanced; no accidental blank page; no repeated empty paragraphs; no unexplained large gap. A deliberate last page can be short.
4. **Tables:** no content outside margins, clipped rows, over-narrow columns, or split quote/metric labels. Header repeats on subsequent pages.
5. **Pagination:** page numbers are dynamic and visible; footers do not overlap the body; a section break has not created an unwanted blank page.
6. **Readability:** paragraphs are not walls of text; lists are not over-indented; quotes and captions stay with the related content.

Fix the cause: style spacing, column width, table row settings, keep-with-next, or a deliberate break. Avoid reducing every font simply to meet an arbitrary page count.

## Verification statement

Use one of these truthful statuses:

- “Rendered and inspected all N pages; structural preservation checks passed.”
- “Created the Word file and checked its structure. Visual pagination could not be verified because no renderer was available.”

Never invent a render status. Store QA PDFs/images separately from the final files so the teacher receives a clear result.
