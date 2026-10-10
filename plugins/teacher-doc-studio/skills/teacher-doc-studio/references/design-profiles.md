# Design profiles

These are design defaults, not institutional rules. A supplied template takes priority. Text and headings are black; metadata can be dark grey. Colour is optional when explicitly requested.

| Role | Thai modern | English report | Bilingual blocks |
|---|---|---|---|
| Body | Tahoma 11.5 pt | Calibri 11.5 pt | Tahoma 11.5 pt |
| Title | Tahoma bold 20 pt | Calibri bold 22 pt | Tahoma bold 20 pt |
| Heading 1 | 15 pt bold | 16 pt bold | 15 pt bold |
| Heading 2 | 13 pt bold | 13 pt bold | 13 pt bold |
| Heading 3 | 11.5 pt bold | 11.5 pt bold | 11.5 pt bold |
| Body line spacing | 1.18 | 1.15 | 1.18 |
| Paragraph after | 7 pt | 7 pt | 7 pt |
| Table body | 10.5–11 pt | 10.5–11 pt | 10.5–11 pt |

Tahoma is the conservative Thai fallback in the supplied Windows examples. Font availability varies on other devices. Inspect glyphs and line breaks after rendering; never declare fonts embedded unless they are actually embedded.

The `thai-formal` profile uses TH Sarabun New: body 16 pt, title 28 pt, headings 22/20/18 pt, table/caption/footer 14 pt, and subtitle 16 pt. Its reusable JSON is `assets/profiles/thai-formal.json`. The script checks the Windows font registry and reports whether the chosen font was confirmed; it does not silently substitute a font or claim font availability on unsupported platforms.

The tested Thai formal starting point uses single line spacing with 4 pt paragraph spacing because larger multiples produced excessive gaps with this font's metrics in Word. Check tone marks after rendering. For a dense English report, `assets/profiles/english-compact.json` offers Calibri 11 pt with smaller role sizes and spacing; use it only when it remains readable and suits the source layout.

This is a starting point for an institutional style, not certification against every Thai government or university requirement. Explicit school/agency rules override it through a reviewed JSON config. Tune line spacing to the actual renderer. Sarabun and Tahoma have different visual sizes; do not reuse the same point size blindly.

## Report composition

Title and a short subtitle occupy roughly the upper quarter or less of the first page. Add date/place as one line when possible. Main headings have 14 pt before and 6 pt after; secondary headings have 10 pt before and 5 pt after. A short activity report normally begins immediately below this block.

For a three-part report, use Background, Activities, and Reflection. Reflection may contain key learning, participant voice, and intended application. Group facilitator learning and participant learning when the source calls for it. Section numbers must reflect the actual hierarchy.

For bilingual reports, prefer complete Thai and English blocks with the same section order. Side-by-side columns work for short labels, not long paragraphs. Do not repeat an entire translation unless requested. Mixed-language proper names within a sentence should share its baseline and visual size.

## Tables and quotations

Keep the usable width within the page margins. Use a pale grey header, bold labels, about 2 mm cell padding, and top-aligned content. Avoid a table merely to place ordinary paragraphs. Use a short quotation paragraph with left/right indentation and an attribution line. Italicise English quotations only if readable; Thai body should remain upright.

The formatter preserves existing footer content. For a new single-section template, add a short report label left and a dynamic page number right. Do not put a full long report title into every header.
