# معايير القبول / Quality Gates

**قاعدة:** امتداد `.docx` لا يعني ملف Word صالحًا. كل إصدار له تعريف واضح لـ editability وfidelity.

| Gate | Automatic check today | Manual acceptance condition | State |
| --- | --- | --- | --- |
| Q1 Source text mapping | suspicious Unicode count == 0 to allow editable | لا أخطاء حروف/همزات عند المقارنة بصورة PDF | جزئي؛ حروف خاطئة صامتة قد تمر |
| Q2 RTL | paragraph has `w:bidi`; segments have `w:rtl` | العربية والأقواس والأرقام في مواضعها الأصلية | جزئي |
| Q3 Page count | optional LibreOffice re-render page count | عدد صفحات Word مطابق لمجموعة الصفحات المطلوبة | موجود |
| Q4 Editable structure | count text paragraphs, tables, images | جميع النصوص المطلوبة قابلة للتعديل (في مسار editable) | جزئي؛ الجدول ناقص |
| Q5 Typography | report PDF font metrics | أحجام الخط والهوامش وتباعد الأسطر مطابقة ضمن سماحية متفق عليها | يدوي/مؤجل |
| Q6 Layout | preliminary image blocks; list complex pages | الأعمدة/المربعات والصور لا تتداخل ولا تتحرك خطأً | يدوي/مؤجل |
| Q7 Figures & tables | count embedded images and native tables | الصور واضحة والتعليقات مرتبطة بها؛ الجداول Word حقيقية حيث طُلب | جزئي/مؤجل |
| Q8 Release | report plus reviewer sign-off | فحص 100% من الصفحات، ودوّن محرك Word والخطوط المستعملة | غير تلقائي |

## Proposed scorecard, not yet implemented

- **Transcription:** Character Error Rate (CER) against human-verified truth. Target e.g. `≤0.1%` only *when* ground truth exists; not a claim of achieved quality.
- **Layout:** per-block bbox tolerance e.g. ≤3 mm and correct reading order; requires a detector and matching.
- **Visual:** region-level SSIM/render overlap; should not substitute editable-structure validation.
- **Editing:** at least 95% of content-character count in editable runs; explicitly exclude visual pages.
- **Tables:** expected table count and cell text equality.

## Policy

`mode=editable` returns nonzero failure if source text contains suspicious Unicode, unless `--allow-suspect-text` is passed with full awareness. `mode=hybrid` substitutes a full image of a suspect page. Both are **honest** about the tradeoff. For production, review every page and do not release corrupted text based solely on one automatic score.
