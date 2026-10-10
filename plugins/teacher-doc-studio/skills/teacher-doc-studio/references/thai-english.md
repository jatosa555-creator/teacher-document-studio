# Thai and English typography and meaning

- Thai combines base letters, upper/lower vowels, and tone marks. Keep Unicode text intact; check marks for clipping in headings, tables, and footers. Do not insert spaces between letters or use fixed exact line heights that clip marks.
- Thai word wrapping is renderer-dependent. Prefer left alignment for ordinary reports, and assess ragged line endings visually. Use justified alignment only after checking that spaces and line breaks remain natural. Avoid distributed alignment.
- Preserve spelling, formal titles, institution names, dates, and Thai numerals if requested. Never silently convert Buddhist Era years to Common Era or vice versa.
- Mixed Thai/English runs may need a Thai-capable complex-script font. Set Word `ascii`, `hAnsi`, `eastAsia`, and `cs` font attributes consistently. Setting only `font.name` does not reliably cover every renderer.
- Do not insert manual line breaks throughout body paragraphs to imitate a screenshot. Keep paragraphs editable and let Word paginate.
- Use real Heading styles and real list numbering. A line beginning with `3.1` is not automatically a heading; infer its role from context and confirm against the source.
- A translation is a content change. Format-only requests retain the original language. When translating a quote, indicate translation or edited translation and preserve the original sentiment.
- For English proper names whose source is Thai, use the user's verified spelling. If none is supplied, retain Thai or clearly mark transliteration for verification rather than inventing a confident official spelling.
- Font files are not included in this package. Do not redistribute installed fonts without checking their licence. If a font is missing, choose an available Thai-capable alternative and verify the change visually.

Useful checks: “ผู้เรียนได้เรียนรู้ผ่านการลงมือปฏิบัติ”; “น้ำ พื้นที่ วิทยาศาสตร์”; “STEM เพื่อความเสมอภาค (Educational Equity)”; “ความพึงพอใจเฉลี่ย 8.90/10”; “24–26 July 2026”. Check that diacritics, decimal points, slashes, and en dashes remain readable.
