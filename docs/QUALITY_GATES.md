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
| Q8 Release | `release-check` يتحقق من وجود سجلات المراجعة والبصمات ويمنع الاعتماد دونها | فحص 100% من الصفحات والتوافق الحقيقي مع Microsoft Word واعتماد المستخدم | بوابة برمجية موجودة؛ مصداقية المراجعة يثبتها الإنسان |

## Proposed scorecard, not yet implemented

- **Transcription:** Character Error Rate (CER) against human-verified truth. Target e.g. `≤0.1%` only *when* ground truth exists; not a claim of achieved quality.
- **Layout:** per-block bbox tolerance e.g. ≤3 mm and correct reading order; requires a detector and matching.
- **Visual:** region-level SSIM/render overlap; should not substitute editable-structure validation.
- **Editing:** at least 95% of content-character count in editable runs; explicitly exclude visual pages.
- **Tables:** expected table count and cell text equality.

## Policy

`mode=editable` returns nonzero failure if source text contains suspicious Unicode, unless `--allow-suspect-text` is passed with full awareness. `mode=hybrid` substitutes a full image of a suspect page. Both are **honest** about the tradeoff. For production, review every page and do not release corrupted text based solely on one automatic score.

## بوابة إصدار فعلية — تحديث 2026-10-16

الأمر `bio2word release-check FILE.docx runs/private_evidence.json --render` يُرجع **exit 3** إذا فشل أي شرط، ويُبلغ باسم الفشل بدل إعلان النجاح. من أمثلة معرّفات الفشل:

- `ARTIFACT_HASH_MISMATCH`: الملف تغيّر بعد المراجعة.
- `DAMAGED_UNICODE` و`TEXT_UNVERIFIED`: النص غير موثوق أو لا يحمل مصدر مراجعة الصورة.
- `SPLIT_PARAGRAPH_INTO_LINES`: إعادة بناء الأسطر بشكل يمنع تحرير الفقرات الطبيعية.
- `RUN_DIRECTION_UNCHECKED` / `OOXML_MIXED_SCRIPT_RUN`: اختلاط RTL وLTR في البيانات أو المخرجات الفعلية.
- `FONT_NOT_CALIBRATED`: لا توجد قياسات أصلية ومقابلة للناتج.
- `LAYOUT_NOT_MEASURED` / `LAYOUT_DRIFT`: إحداثيات الأصل والناتج غير متوفرة أو متباعدة أكثر من السماحية.
- `BACKGROUND_NOT_VERIFIED` / `FIGURES_NOT_IN_DOCX`: خلفية/رسوم غير موثقة أو غائبة.
- `DOCX_* / OOXML_* `: خلل بنيوي داخل Word.
- `RENDER_REQUIRED` / `PAGE_COUNT_MISMATCH`: ملف نهائي لم يعرض أو يطابق عدد الصفحات.
- `WORD_DESKTOP_NOT_VERIFIED`: لا توجد تجربة فتح/تعديل/حفظ موثقة للنسخة نفسها في Word.

الفرق بين **فحص آلي لوجود الأدلة** و**تحقق مستقل من صحة الأدلة** أساسي. البرنامج ليس قارئًا بشريًا ولا يستطيع تأكيد أن الشخص راجع المصدر فعلًا. الـCLI يحظر الملف غير الموثق، ولا يضمن صحة أي وثيقة يدّعي أصحابها خلاف الحقيقة. مثال الأدلة `docs/RELEASE_EVIDENCE_TEMPLATE.json` يتعمد أن يكون غير معتمد.

**المسارات الحالية (visual/editable/hybrid/reviewed) تنتج مرشحين تجريبيين فقط.** النجاح البرمجي أو التصيير في LibreOffice غير كافٍ للتسليم النهائي. عناصر المعايرة الآلية، ومطابقة الصور تفصيليًا، واختبار Word Desktop تلقائيًا ليست منفذة بعد؛ ولذلك لا يجوز الادعاء بأنها أصبحت مكتملة.
