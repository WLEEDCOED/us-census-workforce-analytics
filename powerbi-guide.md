# دليل إعادة بناء الداشبورد في Power BI

هذا الدليل يخليك تعيد بناء نفس الداشبورد الموجود في الملف `dashboard.png`
(بنفس المجلد — هو المرجع البصري للشكل النهائي) داخل **Power BI Desktop**
على جهازك، خلال **~15 دقيقة** بخطوات مرقّبة وبسيطة.

البيانات حقيقية 100%: سجلات تعداد أمريكا 1994 (UCI Adult dataset).

> **المتطلب المسبق:** ثبّت Python على جهازك مع مكتبتي `pandas` و `matplotlib`
> (`pip install pandas matplotlib`)، وفعّله في Power BI من
> **File ← Options and settings ← Options ← Python scripting**.

---

## الطريق الأسرع: فيجوال بايثون (صفحتين جاهزتين)

### الصفحة 1 — نظرة عامة (Overview)
1. **Get Data** ← حمّل `data/adult_census.csv`.
2. أنشئ صفحة جديدة وسمّها **Overview**، ومن **Insert** أضف **Python visual**.
3. اسحب إلى خانة **Values** هذه الأعمدة الخمسة بالضبط:
   `income` ← `age` ← `hours-per-week` ← `education` ← `occupation`.
4. الصق كامل محتوى الملف `powerbi-page1-overview.py` ← اضغط Run.

### الصفحة 2 — التفاصيل (Details)
1. أنشئ صفحة ثانية وسمّها **Details**، وأضف **Python visual** جديد.
2. اسحب إلى خانة **Values** هذه الأعمدة الخمسة بالضبط:
   `income` ← `sex` ← `hours-per-week` ← `age` ← `capital-gain`.
3. الصق كامل محتوى الملف `powerbi-page2-details.py` ← اضغط Run.

### إضافة Slicers (فلاتر تفاعلية)
أضف Slicers عادية وستُرشّح فيجوال بايثون تلقائياً:
- **Slicer** ← `sex` | **Slicer** ← `education` | **Slicer** ← `occupation`.

> **ملاحظة صادقة:** الـ Slicers **تُرشّح** فيجوال بايثون فعلاً — الصفوف المفلترة هي اللي توصل
> لمتغير `dataset` داخل السكربت. لكن فيجوال بايثون **لا يستقبل** التظليل التفاعلي (highlight)
> من الضغط على رسوم بيانية ثانية.

---
## الطريق الثاني: بناء يدوي بمقاييس DAX (اختياري)

## ١) تحميل البيانات (Get Data)

1. افتح **Power BI Desktop** ← تبويب **Home** ← **Get Data** ← **Text/CSV**.
2. اختر الملف **`data/adult_census.csv`** — هو الملف الوحيد اللي تحتاجه
   (48,842 صف × 15 عمود، منظّف وجاهز، ما يحتاج دمج ملفات).
3. تأكد أن **File Origin = ‎65001: UTF-8** و **Delimiter = Comma** ثم اضغط **Load**.

> ما تحتاج تحمّل ملفي `adult.data` و `adult.test` الخام — ملف الـ CSV عندنا
> مدمج ومنظّف مسبقاً بسكربت `download_data.py`.

---

## ٢) نموذج البيانات (Data Model)

- عندك **جدول واحد فقط** اسمه `adult_census`.
- **لا تحتاج أي Relationships** — كل الأعمدة في نفس الجدول، فلا يوجد ربط.
- أهم الأعمدة اللي بنستخدمها (انسخ الأسماء زي ما هي):
  `age` ،`workclass` ،`education` ،`education-num` ،`occupation` ،`sex` ،
  `hours-per-week` ،`capital-gain` ،`income`

---

## ٣) مقاييس DAX (انسخ والصق)

روح على جدول `adult_census` ← كليك يمين ← **New Measure**، والصق كل مقياس:

```dax
Total Records =
COUNTROWS ( 'adult_census' )
```

```dax
Over50K Count =
CALCULATE (
    COUNTROWS ( 'adult_census' ),
    'adult_census'[income] = ">50K"
)
```

```dax
Pct Over 50K =
DIVIDE ( [Over50K Count], [Total Records] )
```

```dax
Median Hours =
MEDIAN ( 'adult_census'[hours-per-week] )
```

```dax
Median Age =
MEDIAN ( 'adult_census'[age] )
```

```dax
Mean Hours Over50K =
CALCULATE (
    AVERAGE ( 'adult_census'[hours-per-week] ),
    'adult_census'[income] = ">50K"
)
```

```dax
Mean Hours Others =
CALCULATE (
    AVERAGE ( 'adult_census'[hours-per-week] ),
    'adult_census'[income] = "<=50K"
)
```

```dax
Over50K Rate =
DIVIDE (
    CALCULATE (
        COUNTROWS ( 'adult_census' ),
        'adult_census'[income] = ">50K"
    ),
    COUNTROWS ( 'adult_census' )
)
```

> ⚠️ مهم: أسماء الأعمدة اللي فيها شرطة (`-`) لازم تُكتب هكذا:
> `'adult_census'[hours-per-week]` — اسم الجدول بين علامتي تنصيص مفردة،
> واسم العمود بين قوسين مربعين.
> بعد لصق `Pct Over 50K` و `Over50K Rate`: حددهما ← **Measure tools** ←
> **Format = Percentage**.

### عمود محسوب للفئة العمرية (New Column)

كليك يمين على الجدول ← **New Column** ← الصق:

```dax
Age Band =
SWITCH (
    TRUE (),
    'adult_census'[age] <= 24, "17-24",
    'adult_census'[age] <= 34, "25-34",
    'adult_census'[age] <= 44, "35-44",
    'adult_census'[age] <= 54, "45-54",
    'adult_census'[age] <= 64, "55-64",
    "65+"
)
```

### ترتيب التعليم من الأقل للأعلى

حدّد عمود **`education`** ← تبويب **Column tools** ← **Sort by column** ←
اختر **`education-num`** (عشان الرسم يطلع مرتباً حسب المستوى الدراسي،
مثل الداشبورد الأصلي).

---

## ٤) الرسوم (صفحة واحدة — نفس ترتيب `dashboard.png`)

### صف المؤشرات العلوي — ٤ بطاقات Card

| البطاقة | الـ Value | العنوان |
|---|---|---|
| Card 1 | `Total Records` | Census records |
| Card 2 | `Pct Over 50K` | Earning > $50K / yr |
| Card 3 | `Median Hours` | Median hours / week |
| Card 4 | `Median Age` | Median age |

### رسم ١: النسبة حسب التعليم — Bar chart (أعمدة أفقية)

- **Y-axis** ← `education`
- **X-axis** ← `Over50K Rate`
- فعّل **Data labels**.
- الترتيب تلقائي حسب `education-num` (خطوة الترتيب فوق).

### رسم ٢: النسبة حسب المهنة — Bar chart (أعمدة أفقية)

- **Y-axis** ← `occupation`
- **X-axis** ← `Over50K Rate`
- **Filters on this visual** ← `occupation` **is not** `?`
  (القيمة `?` تعني بيانات ناقصة — نستبعدها من هذا الرسم فقط).
- رتّب تنازلياً: نقاط الرسم `...` ← **Sort descending**.

### رسم ٣: النسبة حسب الجنس (فجوة الأجور) — Clustered column chart

- **X-axis** ← `sex`
- **Y-axis** ← `Over50K Rate`
- **Tooltips** ← أضف `Total Records` (عشان يظهر العدد عند التحويم:
  الذكور n=32,650 والإناث n=16,192).

### رسم ٤: توزيع ساعات العمل حسب الدخل — Clustered column chart

1. حدّد عمود **`hours-per-week`** ← **New Group** ← **Binning** ←
   **Bin size = 2** ← OK (ينشئ عمود `hours-per-week (bins)`).
2. **X-axis** ← `hours-per-week (bins)`
3. **Y-axis** ← `Total Records`
4. **Legend** ← `income` (يطلع عمودين متداخلين: `<=50K` و `>50K`).

### رسم ٥: النسبة حسب الفئة العمرية — Clustered column chart

- **X-axis** ← `Age Band` (العمود المحسوب)
- **Y-axis** ← `Over50K Rate`
- رتّب الفئات يدوياً من الأصغر للأكبر: 17-24 ← 25-34 ← … ← 65+.

### رسم ٦: توزيع Capital Gain حسب الدخل — Clustered column chart

- **Filters on this visual** ← `capital-gain` **is greater than** `0`
  (معظم السجلات قيمتها صفر — نهتم بمن لديه أرباح فقط).
- **X-axis** ← `capital-gain` ← من **Format** ← **X-axis** ← فعّل **Log scale**
  (مقياس لوغاريتمي مثل الداشبورد الأصلي).
- **Y-axis** ← `Total Records`
- **Legend** ← `income`

### Slicers اختيارية (فلترة تفاعلية)

أضف **Slicer** لعمود `sex` وآخر لعمود `education` أعلى الصفحة —
تفلتر كل الرسوم معاً بضغطة واحدة.

---

## ٥) تنظيف Power Query (للمرجع فقط)

ملف `data/adult_census.csv` **منظّف مسبقاً** (المسافات الزائدة محذوفة،
وقيم `income` موحّدة)، فلا تحتاج أي خطوة تنظيف لو حمّلته مباشرة.

لو يوماً حمّلت الملفات الخام من موقع UCI مباشرة، ستحتاج في **Power Query**:

1. حدّد كل الأعمدة النصية ← **Transform** ← **Format** ← **Trim**
   (حذف المسافات من البداية والنهاية).
2. في أعمدة `workclass` و `occupation` و `native-country`:
   **Replace Values** ← استبدل `?` بـ `null` (قيم ناقصة).
3. في الملف الخام `adult.test` عمود الدخل فيه نقطة زائدة (`>50K.`):
   **Replace Values** ← احذف النقطة.

---

## ✅ التحقق الأخير

قارن نتيجتك مع **`dashboard.png`** وتأكد أن الأرقام تطابق:

- **48,842** سجل
- **23.9%** فوق $50K
- الوسيط: **40** ساعة/أسبوع، العمر **37**
- التعليم: Prof-school **74.0%** ← الأعلى
- الجنس: ذكور **30.4%** مقابل إناث **10.9%**
- العمر: الفئة **45-54** الأعلى **39.4%**

إذا طابقت، داشبوردك جاهز 🎉
