# FAB-1 · предмет 5 — кукбук (томи 1–6, індекс, лоток): суперечності й дублі, застаріле, чого бракує для ПК, що веде в нікуди

> живе доки: FAB-1 відкритий (бриф `kernel/Lens_FAB-1_brief.md`); взяте — у свої доми, решта — геть разом із текою.
> хто писав: сесія FAB-1, фаза 2, 11.11.2026, один прохід **лише на читання**; цей файл — єдине, що змінено в ядрі (плюс назва файла в рядку `FAB-1` карти `kernel/Lens_INDEX.md`).
> для кого: сесія звірки, що перевіряє кожну знахідку грепом і несе Konst «беремо / ні». Тут **пропозиції й чернетки**, жодного рецепта не правлено.
> репо публічне: вмісту приватних репо тут нема — лише те, що вже стоїть у самих рецептах, і `Репо:шлях`.

## 0. Коротко

1. **Кукбук цілий там, де це найважливіше:** усі 141 номер мапи індексу мають заголовок у своєму томі, жоден не веде в порожнечу (прилад §7: ✗ 0). Слабке місце — не адресація, а **вік**: рецепт дописують зверху новим блоком, а старий текст під ним лишається. Через це в §2 — 17 місць, де рядки одного кукбука розходяться між собою.
2. **Найдорожчі суперечності — три.** Відступ нижньої панелі: «на контейнер — анти» проти еталона, що ставить його саме на контейнер (С1). Шіт: старий рецепт гортає всю раму, новий — лише середину, а код свайпа читає прокрутку рами, якої вже нема (С2). Активний фільтр: чотири різні відповіді в чотирьох рецептах (С7). Агент, що читає точково, отримує ту редакцію, на яку влучив.
3. **Рецепт, що суперечить сам собі:** A65 перелічує кнопку фільтра серед полів, а через два рядки сам називає це «помилкою рецепта» (С5). Помилка стоїть у тілі в чотирьох місцях.
4. **Для ПК кукбук — це чотири рецепти й дев'ять приписок.** Зі 140 рецептів про ПК, мишу чи клавіатуру помітно говорять 19; цілком ПК-рецептів — 4 (A117–A120). Решта ПК-знання дописана абзацами всередину мобільних рецептів, і індекс про неї не знає (П1). Немає рецептів оболонки сайту для ПК, станів наведення, клавіатури й фокуса, модального вікна (П3–П6).
5. **В нікуди ведуть не номери, а джерела.** «Точний код — греп у файлі такому-то» — 26 названих файлів-джерел, жодного в репо (Н1). Вісімнадцять посилань «wsd 2.4» ведуть у правило, з якого потрібний зміст виїхав; чотири з них — коло (Н3). Борги індексу §6 чекають сесій, що минули в серпні й вересні (Н2).
6. **Три твердження про платформу застаріли** (джерело — дані сумісності MDN, 11.11.2026): `prefers-reduced-transparency` у Safari не працює, тож гілка «зменшити прозорість» в еталоні панелі на iPhone мертва (В1); стилізований `select` уже є в Safari 27 (В2); прокрутка-таймлайн є з Safari 26 (В3).
7. **Половину цього може тримати машина.** Чернетка `cookbook_check.py` (§7, 63 рядки, запущена): шапки томів, вага, мапа індексу, переїзди номерів wsd, джерела поза репо. Сьогодні: ✗ 0 · ⚠ 11; на підкинутій помилці — ✗ і код виходу 1.

## 1. Що прочитано і чим звірено

**Прочитано цілком (11.11.2026):** індекс, томи 1–6, лоток — 8 файлів, **399 083 знаки** (`len`): том 1 — 58 420 · том 2 — 47 914 · том 3 — 77 099 · том 4 — 86 483 · том 5 — 69 955 · том 6 — 18 544 · індекс — 28 290 · лоток — 12 378.
**Точково (грепом, заради посилань із рецептів):** `kernel/wsd/Lens_verdict_protocol.md` (2.4, 4.5) · заголовки решти `kernel/wsd/` · `kernel/Lens_excel_protocol.md` (6.5, 6.6) · заголовки `kernel/Lens_stagebench_manifest.md`, `kernel/Lens_glass_FINDINGS.md`, `tools/cloudflare/CLOUDFLARE.md`, `tools/tester/TESTER.md` · шапка `tools/claude-code/ui_lint.mjs` · `kernel/Lens_governance_CHERGA.md` (рядки про кукбук) · `CLAUDE.md` ядра.
**Не читав:** `kernel/Lens_MOTION-1_brief.md`, `tools/claude-code/VOICE.md` і `SHOTS.md` (у цій частині сесії), модуль `kernel/modules/`, репо продуктів (їх у сесії нема) — чи лежать там файли-джерела з Н1, **не перевірено**.

**Прилади:** (1) `cookbook_check.py` — §7, код у звіті, запущений з кореня ядра; (2) звірка цитат цього звіту — скрипт сесії на 28 рядків, у репо його нема (бере кожне посилання «файл:рядок» із цитатою й шукає цитату в тому рядку файла); (3) `git ls-files` — чи є названий файл у репо; (4) дані сумісності браузерів MDN — `https://raw.githubusercontent.com/mdn/browser-compat-data/main/…json`, версія пакета 8.1.8, скачано 11.11.2026 у тимчасову теку й прочитано скриптом (далі — «BCD»).

**Певність:** *висока* — бачив обидва рядки або вивід приладу; *середня* — висновок про поведінку коду, який я не запускав; *низька* — здогад.
**Позначки знахідок:** С — суперечність · Д — дубль · В — вік (застаріле) · П — ПК · Н — в нікуди. Номери рецептів (A…, B…, T…) — як у кукбуку.

## 2. Суперечності між рецептами

**С1 · Нижня панель: відступ на контейнері — анти чи еталон.**
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:27` — «Anti-pattern: padding на контейнер у PWA.»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:229` — «padding:6px 6px max(9px,var(--sab));» (еталон A56, правило самого контейнера `.bottom-nav`)
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:307` — «тут overlay-варіант з sab у padding»
Певність висока. A56 про різницю знає, A15 — ні: хто відкриє лише A15, зробить навпаки від еталона. **Дія:** в A15 один рядок-межа — «бар у потоці — так; бар поверх вмісту (A55, A56) — відступ на контейнері».

**С2 · Шіт: гортається рама чи середина — і що читає свайп.**
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:35` — «`max-height:85dvh`, `overflow-y:auto`»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:431` — «.sh-box{max-height:85dvh;overflow:hidden;display:flex;flex-direction:column}»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:100` — «sy=e.touches[0].clientY; ss=box.scrollTop;»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:435` — «читає `scrollTop` саме цього скролера»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:477` — «прокрутка шіта **+** прокрутка картки під пальцем»
Певність висока щодо тексту, середня щодо наслідку (не запускав): у шіті за A108 рама не гортається, тож `box.scrollTop` з A19 завжди 0 — свайп униз у прокрученому списку закриє шіт, якщо список не внесли руками в перелік винятків. Свайп-гард описано тричі трьома способами (A19, A108, A109). **Дія:** A17 і A19 переписати під A108 — одна будова, один код свайпа.

**С3 · Ліва кольорова смужка: ✅ і 🔴 без вказівника одне на одного.**
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:35` — «**Reuse:** будь-який Lens зі списком типізованих рядків.»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:494` — «Рейл — лише коли **семантично навантажений**: кодує реальну вісь або стан,»
Певність середня: прямої суперечності нема (смужка A34 кодує тип), але A34 не згадує A84, а A84 — A34; пізніший ПК-рецепт смужку прибрав (`kernel/cookbook/Lens_iOS_cookbook_3_material.md:878` — «лишається від прибраної смужки зліва»). **Дія:** по рядку «пара — A84 / A34» в обох.

**С4 · Втоплене поле на темній: «не чіпати» проти темного токена.**
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:252` — «Темна: НЕ чіпати.»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:327` — «--well-sh:inset 0 1.5px 2px rgba(0,0,0,.30),inset 0 -1px 0 rgba(255,255,255,.098);»
Певність висока. A51 унизу каже, що реалізація тепер через токени A65, але рішення «темна = база» лишилось у тілі. **Дія:** рішення A51 замінити вказівником на A65.

**С5 · A65 суперечить власній поправці.**
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:306` — «(search-row, filter-кнопка, GUID-бокс) = **DEBOSS / well**»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:331` — «Споживачі: `.guid-box`, `.ph-srch`, `.flt-btn`»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:333` — «`.flt-btn` у переліку вище — **помилка самого рецепта**»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:335` — «Фікс = перевести їх на `--well-*`.»
Певність висока. Поправка від 08.10.2026 дописана абзацом, а помилкове твердження стоїть у рядках 306, 331, 335 і 374. **Дія:** виправити тіло, поправку згорнути в рядок історії.

**С6 · Світла тінь: «широка» і «широка — бруд» в одному рецепті.**
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:380` — «лише одна широка (розмиття ≥ 14 px без ключової) — брудна пляма, що лягає на сусіда»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:385` — «світла тінь широка за правилом вище; числа для картки»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:402` — «тінь `0 8px 22px rgba(20,40,35,.09)`»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:407` — «вузька drop (≤4px) на світлій =»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:316` — «широка drop-тінь + градієнт (→A66)»
Певність висока. Правило A66 переписано («ключова + мала розсіяна»), а приклад-прецедент, примітка, рядок «Анти» і таблиця A65 лишились зі старої редакції. **Дія:** одна редакція; прецедент `0 8px 22px` — або перевести на пару тіней, або позначити датою «до зміни правила».

**С7 · Активний фільтр: чотири відповіді.**
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:711` — «**Пасив = обведення. Актив = западина (`well`)**»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:333` — «кнопка фільтра — дія, не ввід → **lift**»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:416` — «.X.on{background:#dcefed;color:#0e2f2c;border-color:#33ccbd;»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:591` — «**Обраний фільтр — без заливки акцентом**»
`kernel/cookbook/Lens_cookbook_INDEX.md:82` — «**Активний фільтр підсвітити — акцентом чи матеріалом**»
Певність висока. За датами найновіша — редакція в полі пошуку (16.10.2026), найстарша — «западина» (21.08.2026); індекс веде лише на найстаршу. **Дія:** рішення Konst, яка чинна (§9, Р3); далі — рядок-межа в A89-б і другий рядок індексу.

**С8 · Натиск: чистий `:active` — у драбині й у «Анти» водночас.**
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:119` — «тактильний прес `:active{transform:scale(.96–.97)}`»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:156` — «на швидкий тап (down+up за <100ms) око не встигає побачити стиск»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:193` — «чистий `:active{scale}` для швидкого тапу (непомітно)»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:188` — «**Micro tap:** `:active{ transform:scale(.97) }` — лише на ключових CTA.»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:194` — «там OK, бо nav-кнопки постійні в DOM, не ре-рендеряться»
Певність висока. Виправдання з рядка 194 відповідає на іншу ваду (перемальовування), а не на «швидкий тап не видно». **Дія:** рядок драбини `.10s` і A30 п.3 привести до A67 — або назвати, де `:active` свідомо лишається.

**С9 · Кромка прокрутки: «завжди» проти «лише за станом».**
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:186` — «**Scroll-fade краї chips:**»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:470` — «кромка завжди, навіть коли все влазить (клас лише за станом)»
Певність висока. **Дія:** A30 п.1 → вказівник на A109.

**С10 · Service worker: «зареєстровано» в чек-листі проти «не потрібен».**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:619` — «SW registered»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:415` — «**Чому не service worker.**»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:680` — «**SW лише для `push` і `notificationclick`** — без `fetch` і `caches`»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:521` — «**Service Worker + offline queue** — install: cache static;»
Певність висока. Чек-лист викладки (Частина C) і продуктова специфікація B1 старші за обидва рішення. **Дія:** рядок чек-листа — «SW лише для пушу (A111), якщо пуш є»; B1 — позначка «специфікація, не реалізовано; про SW — A79».

**С11 · Детект режиму «з Додому» — і вказівник на уточнення, якого там нема.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:432` — «не `--sab` і не сам `navigator.standalone`»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:433` — «`display-mode: standalone` істинний і у вікні посилання»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:654` — «`navigator.standalone` (див. уточнення в A11).»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:657` — «самоперевірка версії (A79: HEAD без кешу, інший ETag → перезавантаження;»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:410` — «тягне власне тіло, регекс дістає з відповіді»
Певність висока. Уточнення вставлене посеред речення A79 (рядок 433 розриває рядки 432 і 434), а A110 шукає його в A11 (рядки 111–118 — без уточнення). Самоперевірку версії A110 описує іншим механізмом, ніж сам A79. **Дія:** уточнення — в A11; речення A79 зібрати; у A79 назвати обидва механізми або виправити A110.

**С12 · Три чи чотири механізми втрати даних.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:524` — «що розділяє сховища і три механізми втрати»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:547` — «чотири механізми втрати, жоден не є дефектом коду»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:586` — «Жоден із трьох механізмів не питає дозволу»
Певність висока; таблиця має чотири рядки. **Дія:** «чотири» в заголовку, рядку 586 і в мапі індексу (`kernel/cookbook/Lens_cookbook_INDEX.md:243`). Клас 0.

**С13 · Іконки: два набори.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:39` — «maskable з padding 10%»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:371` — «Габарит гліфа: `any` ≈ 0.66 сторони, `maskable` ≈ 0.50»
Певність середня (числа міряють різне, але дають різний результат: відступ 10 % — це гліф 0,80). A3 каже «7 файлів», таблиця A75 має 6. **Дія:** A3 → вказівник на A75 як чинний набір.

**С14 · «Наступний шіт після натиску»: три числа.**
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:328` — «120 = синхрон із закриттям.»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:427` — «коли дограла анімація натискання (~150–250 мс)»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:89` — «**відклади close** на ~250ms»
Певність середня (ситуації сусідні, правило одне). **Дія:** одне правило в A108 п.4, решта — вказівник.

**С15 · Фокус поля: `outline:none` проти кільця фокуса.**
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:574` — «.inp:focus{outline:none;border-color:var(--border-accent);background:var(--surface-2)}»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:575` — «.sr-inp{outline:none}»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:883` — «**Кільце фокуса** (Tab) — не витік і не прикраса: WCAG 2.4.7»
Певність висока. B3 не має межі «телефон». **Дія:** рядок-межа в B3: «на ПК — `:focus-visible`, A117».

**С16 · Довжина списку: поріг 5 і поріг 15.**
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:736` — «**≤5 варіантів** І прив'язка до конкретного контрола»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:1008` — «список вибору довший за ~15 пунктів»
Певність середня: пороги для різних пристроїв, але жоден цього не каже. **Дія:** в A90 рядок «на ПК — A117 (список) і A119 (15+)».

**С17 · Розділ «НЕ універсальне» з універсальними ✅.**
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:515` — «**НЕ універсальне.**»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:586` — «Нове поле пошуку в продукті береться звідси цілком, не вигадується.»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:635` — «`space-between`/`space-around` з одним flex-дитям — no-op»
`kernel/cookbook/Lens_cookbook_INDEX.md:365` — «B2/B3 насправді універсальні»
Певність висока; індекс сам це знає з липня. **Дія:** B2.1, B3.1, B3.2 — в A-номери (перехід у Частину A); пастку з B5 — окремим рядком в A40 чи A64.

## 3. Дублі

**Д1 · Скрипт теми до першого кадру — двічі, з різними кольорами.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:53` — «var saved = localStorage.getItem('<prod>-theme');»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:103` — «var saved=localStorage.getItem('dl-theme'), mode=saved||'auto';»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:60` — «if (meta) meta.content = dark ? '#0d1117' : '#f7f4ec';»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:108` — «if(meta)meta.content=dark?'#0E1311':'#F4F7F5';»
Певність висока. **Дія:** в A6 §4 лишити вказівник на A5 і лише те, чого в A5 нема.

**Д2 · Числа пружини перемикача — у чотирьох місцях.**
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:65` — «--seg-dur:450ms; --seg-ease:cubic-bezier(.34,1.56,.64,1);»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:135` — «`--seg-dur:500ms` `--seg-ease:cubic-bezier(.34,1.70,.64,1)`»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:152` — «Drive 450ms/(.34,1.56) з wsd 14.13»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:197` — «ніж seg (450/1.56)»
Певність висока. **Дія:** числа — лише в A54; в A57 і A56 — вказівник.

**Д3 · «Ключова тінь + розсіяна» — у трьох рецептах, в одному ще й «без заміру».**
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:380` — «**щільна ключова** біля тіла (зсув 1 px, розмиття 2 px — задає край)»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:474` — «🧪 — правило зі слова Konst, машинного заміру ще нема.»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:641` — «Тільки дальня → предмет висить без ваги.»
Певність висока. **Дія:** дім правила — A96; A66 і A66.2 — вказівник; позначку 🧪 зняти (числа й перевірка «тінь не дістає сусіда» вже в A66).

**Д4 · Кандидати лотка, що вже є в томах (або суперечать їм).**
`kernel/cookbook/Lens_cookbook_delta_running.md:174` — «К-6 (cand.) · Гасити всі `transition` під час перемикання теми» ⟂ `kernel/cookbook/Lens_iOS_cookbook_1_platform.md:195` — «додати `.no-transition` (`transition:none!important`) → `applyTheme()`» — дубль.
`kernel/cookbook/Lens_cookbook_delta_running.md:122` — «К-1 (cand.) · Концентричний радіус вкладеного» ⟂ `kernel/cookbook/Lens_iOS_cookbook_4_components.md:63` — «**Концентричні кути (не на око):**» — дубль.
`kernel/cookbook/Lens_cookbook_delta_running.md:183` — «К-7 (cand.) · `will-change: transform` проти дрейфу 1–2px у Safari iOS» ⟂ `kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:51` — «**без `will-change`** (постійний GPU-шар = композитинг-шви)» і `kernel/cookbook/Lens_iOS_cookbook_5_motion.md:270` — «Не лікує.» — суперечить двом чинним.
Певність висока. **Дія:** на перегляді лотка 19.11.2026 — К-6 і К-1 закрити вказівником на том, К-7 — відкинути або звузити (§9, Р7).

## 4. Застаріле проти сьогоднішньої практики

**В1 · Гілка «зменшити прозорість» на iPhone не спрацьовує.**
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:261` — «@media(prefers-reduced-transparency:reduce){»
BCD (11.11.2026): Chrome 118 · Safari — **ні** · Firefox — за прапорцем. Певність висока щодо підтримки; чи системне «Зменшити прозорість» iOS якось інакше діє на скло в PWA — **не перевірено**. **Дія:** рядок-примітка з датою в A56; гілку не видаляти (у Chrome діє).

**В2 · Стилізований `select` — уже не лише Chromium.**
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:891` — «поза Chromium — нативний (`@supports`)»
BCD: `appearance: base-select` — Chrome 135 · **Safari 27** · Firefox 149 за прапорцем. Певність висока щодо версій; вигляд і поведінка на iPhone з iOS 27 — **не перевірено**. **Дія:** оновити рядок; для продукту, який відкривають і з телефона, — перевірка на пристрої.

**В3 · Причина «чому JS-класи, а не таймлайн прокрутки» застаріла, висновок — ні.**
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:462` — «підтримка в Safari різних версій розходиться (огляди 2026, не перевірено на пристрої)»
BCD: `animation-timeline` — Chrome 115 · Safari 26 · Firefox 159. Тестова база кукбука — iOS 18 (`kernel/cookbook/Lens_cookbook_INDEX.md:345` — «iPhone XS iOS 18 PWA»), там властивості нема. **Дія:** причину (2) переписати одним реченням: «база — iOS 18; з Safari 26 — є».

**В4 · `@starting-style`: 17.5, не 17.4.**
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:55` — «(iOS 17.4+, без UX-виграшу)»
BCD: Safari 17.5. Клас 0.

**В5 · Паспорт свіжості A105 спрацював — за власним правилом.**
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:557` — «якщо від дати звірки минуло >60 днів АБО вийшла нова мінорна iOS»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:560` — «на iOS 27 тик прямого дотику до `switch` **не перевірено**»
Звірено 17.09.2026 → 60 днів спливають 16.11.2026; нова iOS, за самим рецептом, уже вийшла. BCD: `input switch` — лише Safari 17.4+, у Chrome і Firefox нема. Певність висока. **Дія:** до наступного порту — звірка з чотирьох кроків рецепта. Це єдиний рецепт із таким гейтом — зразок для решти (§8, п.7).

**В6 · «Перевірити при наступному мажорному iOS» — три перевірки прострочені; четверта чекає іншої події.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:388` — «**Перевірити при виході наступного»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:438` — «`beforeinstallprompt` у Safari **відсутній**. Перевірити при наступному мажорному iOS.»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:581` — «*Перевірити при наступному мажорному iOS.*»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:518` — «Перевірити при зміні мінімальної цільової версії iOS.»
iOS 27 вийшла 14.09.2026 — це каже сам кукбук (`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:560`). BCD: `BeforeInstallPromptEvent` у Safari досі нема — це спостереження можна закрити датою 11.11.2026; `CompressionStream` — Safari 16.4, без змін. Іконки за темою і квота сховища — **не перевірено**. Черга ядра має сусідній рядок `PLT-1` (спостереження без дати); ці — з датою, але без повторної перевірки. **Дія:** дописати до `PLT-1` або окремий рядок.

**В7 · Мітки «чекає пристрою», яким місяці й яким суперечить сусідній текст.**
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:173` — «**device-test pending**»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:54` — «Свайп календаря — device-test pending.»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:52` — «*Device-validated B29.1.*»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:553` — «Не залочено — device-вирок не винесено.»
`kernel/cookbook/Lens_iOS_cookbook_3_material.md:479` — «прод QR rev 19 (PR бота, чекає Merge)»
Певність висока щодо розбіжності, середня щодо того, яка половина правдива. Рецепт сам описує цю хворобу: `kernel/cookbook/Lens_iOS_cookbook_3_material.md:108` — «значення мігрують між батчами». Прилад §7 рахує такі мітки: 20 на кукбук. **Дія:** перегляд списком (20 рядків) — «закрито датою / живе / невідомо».

**В8 · Драбина тривалостей описує стан одного білда.**
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:113` — «Значення — з batch41, усі device-валідовані.»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:152` — «магічний час поза драбиною (.19s/.35s)»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:66` — «--sh-close:360ms»
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:599` — «transition:width 300ms cubic-bezier(.34,1.3,.64,1)»
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:175` — «down **80ms** (лінійно) / return **280ms**»
Певність висока: пізніші рецепти мають 80, 140, 280, 300, 360, 600 мс — жодного в таблиці. **Дія:** або друга таблиця «після batch41», або назвати драбину чесно — «функціональний відгук до .26s» — і звузити рядок «Анти».

**В9 · Шапки томів, вага, «Кінець» посеред тому.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:11` — «**Записи тому (23):**» (фактично 30) · `kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:11` — «**Записи тому (14):**» (17) · `kernel/cookbook/Lens_iOS_cookbook_3_material.md:11` — «**Записи тому (13):**» (30) · `kernel/cookbook/Lens_iOS_cookbook_4_components.md:11` — «**Записи тому (29):**» (38 разом із B)
`kernel/cookbook/Lens_cookbook_INDEX.md:24` — «56.5 KB» (файл — 83,5 КіБ) · `kernel/cookbook/Lens_cookbook_INDEX.md:27` — «70.6 KB» (122,3)
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:623` — «**Кінець.** Будь-який пункт Частини A валідований на iPhone XS iOS 18 PWA» — після цього рядка в томі ще три рецепти (A110, A111, A115).
Певність висока (прилад §7). **Дія:** не руками — приладом; рядок «Кінець» і Частину C перенести в хвіст тому або прибрати.

**В10 · Лоток описує світ до розпилу; перегляд кандидатів — за 8 днів.**
`kernel/cookbook/Lens_cookbook_delta_running.md:6` — «Вхідний лоток для нових записів `Lens_iOS_cookbook.md`.»
`kernel/cookbook/Lens_cookbook_delta_running.md:8` — «який уже 2000+ рядків і стоїть у черзі на розпил по розділах.»
`kernel/cookbook/Lens_cookbook_delta_running.md:19` — «рядок-вказівник на цей файл тримати у §ПАРКІНГ кожного»
`kernel/cookbook/Lens_cookbook_delta_running.md:80` — «без вироку пристрою, перегляд 19.11.2026»
Певність висока. Розпил відбувся 31.07.2026 (той самий файл, рядок 28). **Дія:** шапку лотка — 5 рядків наново; перегляд 12 кандидатів — §9, Р7.

**В11 · Колір теми у вкладці Safari.** BCD, примітка до `meta name="theme-color"`: «From Safari 26, the theme color is only used for installed web apps». Рецепти A5 і A6 синхронізують цей колір (`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:60`); у встановленому застосунку це й далі діє, у вкладці — ні. Певність середня (примітка BCD, на пристрої не перевірено). **Дія:** рядок-примітка в A5.

## 5. Чого бракує для ПК

**Замір.** Рецептів (`## A… / B… / T…`) — 140. З двома й більше згадками ПК, миші, наведення, Tab чи Esc — 19 (прилад — скрипт у §10). Цілком про ПК — 4: A117–A120. Тестова база в індексі — один телефон: `kernel/cookbook/Lens_cookbook_INDEX.md:345` — «**Тестова база.** iPhone XS iOS 18 PWA». Двері ядра називають кукбук так само: `CLAUDE.md:22` — «інтерфейс iOS / PWA, бот на Workers».

**П1 · ПК-знання сховане в мобільних рецептах, індекс про нього мовчить.** Приписки: `kernel/cookbook/Lens_iOS_cookbook_5_motion.md:99` (A54), `kernel/cookbook/Lens_iOS_cookbook_3_material.md:381` (A66), `kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:425` (A108), `kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:466` і `kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:468` (A109), `kernel/cookbook/Lens_iOS_cookbook_4_components.md:962` (A113), `kernel/cookbook/Lens_iOS_cookbook_1_platform.md:711` (A115), `kernel/cookbook/Lens_iOS_cookbook_5_motion.md:742` (A116), `kernel/cookbook/Lens_iOS_cookbook_5_motion.md:531` (A83), `kernel/cookbook/Lens_iOS_cookbook_4_components.md:616` (B3.2). Рядок індексу A108 — про шіт на телефоні (`kernel/cookbook/Lens_cookbook_INDEX.md:90`), а в рецепті — правило видалення з поверненням для ПК: `kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:425` — «на ПК — без підтвердження: одразу +». Певність висока. **Дія (дешева, клас 0):** 8–10 рядків у §2 індексу з тригером «ПК: …» на ті самі номери.

**П2 · A117 — дванадцять тем під одним номером.** Рядки 865–901 тому 3, близько 9 тис. знаків: родина, матеріали, виділення, оболонка, пояснення в «i», «форма пояснює себе», лічба поля, шапка, якорі, списки, перевірка, два «Анти». В індексі — один рядок. Читати точково неможливо: або весь, або навмання. **Дія:** підзаголовки `###` і рядок §2 на кожен; розпил на окремі номери — рішення Konst (§9, Р2).

**П3 · Нема рецепта оболонки сайту для ПК; мобільні рецепти оболонки на ПК шкодять і цього не кажуть.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:22` — «maximum-scale=1,user-scalable=no,viewport-fit=cover»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:171` — «-webkit-user-select:none; user-select:none;»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:169` — «html,body{ height:100%; overflow:hidden; overscroll-behavior:none; }»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:138` — «(desktop limit)»
Жоден не має межі «лише телефон». Сам кукбук уже описав наслідок: `kernel/cookbook/Lens_iOS_cookbook_3_material.md:901` — «Сайт для ПК, у якого частина екранів — стос мобільних карток по центру, — вада продукту». Що мав би містити рецепт: масштаб сторінки не заборонено; текст виділяється й копіюється; гортається сторінка, а не внутрішній блок; масштаб системи 125 і 150 %; місце під смугу прокрутки (`scrollbar-gutter` — BCD: Chrome 94 · Firefox 97 · Safari 18.2); `color-scheme`. Певність висока, що рецепта нема; перелік — пропозиція.

**П4 · Стани наведення.** У томах 1–5 рядків із `:hover` — **0**; у лотку — 5, усі в кандидаті К-2. Уламки правила є: `kernel/cookbook/Lens_iOS_cookbook_3_material.md:877` — «**Вибране ≠ наведене:**». К-2 уже має другий випадок із приладом: `kernel/cookbook/Lens_cookbook_delta_running.md:139` — «**Другий випадок — AE S117 (30.10.2026, Konst з телефону):**». **Дія:** К-2 — у том (він готовий за власним порогом лотка) і розширити до рецепта «стани контрола на ПК: спокій · наведення · фокус · натиск · вибране · вимкнено».

**П5 · Клавіатура й фокус.** Рецепт доступності — три рядки про атрибути перемикача теми (`kernel/cookbook/Lens_iOS_cookbook_4_components.md:176`). Решта розсипана: кільце фокуса — `kernel/cookbook/Lens_iOS_cookbook_3_material.md:883`; Esc — `kernel/cookbook/Lens_iOS_cookbook_4_components.md:1013` — «**Esc — закрити без змін, `stopPropagation`**»; фокус після закриття — `kernel/cookbook/Lens_iOS_cookbook_4_components.md:1000`; фокус на тексті — `kernel/cookbook/Lens_iOS_cookbook_4_components.md:1053`. Три рецепти вікон (A118–A120) кожен описує Esc і повернення фокуса по-своєму — дубль у зародку. **Дія:** один рецепт «Tab-порядок · кільце · Esc закриває верхній шар · фокус повертається тому, хто відкрив», три рецепти — вказівник.

**П6 · Модальне вікно.** На весь кукбук `<dialog` чи `showModal` — у 4 рядках; рецепта вікна (розмір, тло, закриття, фокус усередині, вікно поверх вікна) нема, хоча на ньому стоять A83, A118, A119, A120. Мобільний відповідник — шіт — має сім рецептів (A17–A21, A108, A109). Певність висока.

**П7 · Рух на ПК.** ПК-чисел у кукбуку три: `kernel/cookbook/Lens_iOS_cookbook_5_motion.md:99` — «(на ПК коротше за мобільні 450 мс)», `kernel/cookbook/Lens_iOS_cookbook_5_motion.md:745` — «**Поява:** 200 мс», і 8 с відліку повернення (`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:425`). Драбина A57 — мобільна. **Дія:** не зараз — таблицю «ПК» в A57 заводити, коли чисел стане п'ять і більше; метод руху — у брифі `kernel/Lens_MOTION-1_brief.md` (не читав).

**П8 · Чого нема зовсім** (греп по заголовках і тілу, певність висока): таблиця даних (липка шапка згадана лише як пастка кромки в A109) · меню «⋯» і контекстне (одна згадка — `kernel/cookbook/Lens_iOS_cookbook_4_components.md:1059`) · тост на ПК (A59 прив'язаний до мобільної панелі: `kernel/cookbook/Lens_iOS_cookbook_4_components.md:447` — «bottom:calc(var(--nav-h,64px) + 14px)», а A108 для ПК тост унизу відкидає) · порожній стан на широкому екрані (`kernel/cookbook/Lens_iOS_cookbook_4_components.md:193` — «min-height:55dvh») · розкладка 1920 (сітка, ширина рядка — лише `kernel/cookbook/Lens_iOS_cookbook_4_components.md:1037` для довгого тексту) · перетягування · незбережені зміни · друк. Це перелік, не план: рецепт з'являється, коли рішення в продукті вже перевірене (поріг кукбука — «наше й device-locked»).

**П9 · Сучасне для ПК, чого кукбук не знає** (зовнішнє, BCD 11.11.2026; у продукті **не перевірено** — гіпотеза): прив'язка до якоря в CSS (`anchor-name`: Chrome 125 · Safari 26 · Firefox 147) — розміщення підказки й меню без власного JS-розміщувача, який сьогодні описують A116 (ПК-варіант) і A53 (`pk-up`). `field-sizing` (Chrome 123 · Safari 26.2 · Firefox 152) A117 уже вживає.

**П10 · Найдешевше, що робить прогалину видимою.** Другий рядок тестової бази в індексі §5 («ПК 1920×1080, Chromium, миша й клавіатура») і позначка пристрою біля ✅ кожного рецепта: 📱 · 🖥 · обидва. Тоді «для ПК не перевірено» видно з мапи індексу, а не з читання 400 тис. знаків. Рішення Konst — §9, Р1.

## 6. Що з індексу й рецептів веде в нікуди

**Н1 · «Джерело правди коду» — файли, яких у репо нема.**
`kernel/cookbook/Lens_cookbook_INDEX.md:342` — «стандартні патерни → `QR_Lens_preview_batch22.html` (grep по назві патерну);»
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:623` — «Точний код — grep у `QR_Lens_preview_batch22.html`»
`kernel/cookbook/Lens_iOS_cookbook_2_navigation.md:191` — «Source-of-truth коду: `Drive_Lens_preview_batch41.html`.»
Прилад §7: названих файлів-джерел поза репо — **26**; дванадцять перевірив ще й руками через `git ls-files` — 0 з 12. У Claude Code «греп у файлі» з рецепта виконати нема де. Чи є ці файли в репо продуктів — **не перевірено**. Певність висока. **Дія:** в індексі §5 сказати прямо: «джерела — в репо продуктів або в Project; у ядрі їх нема»; рецепт, що без джерела не відтворюється, позначити.

**Н2 · Борги індексу §6 чекають сесій, що минули.**
`kernel/cookbook/Lens_cookbook_INDEX.md:364` — «сесія E» · `kernel/cookbook/Lens_cookbook_INDEX.md:366` — «сесія C» · `kernel/cookbook/Lens_cookbook_INDEX.md:367` — «wsd 2.4 (кандидат уже в буфері)»
Сесія E — 01.08.2026 (`kernel/cookbook/Lens_cookbook_delta_running.md:56` — «## ✅ Змерджено 01.08.2026 (сесія E)»). Один із чотирьох боргів закрито деінде й не знято: `kernel/Lens_stagebench_manifest.md:309` — «### 8.6 Правило двох осей — MANIFEST важелів інстанціюється ПЕРШИМ». Решта три (A68 — метод, не рецепт; Частина B; Частина C) не зроблені; у черзі ядра рядків про них нема (греп). Певність висока. **Дія:** §9, Р4.

**Н3 · Номери wsd: зміст переїхав, посилання лишились.**
Прилад §7: «wsd 2.4» — 18 посилань. Сьогодні це `kernel/wsd/Lens_verdict_protocol.md:116` — «## 2.4 Прев'ю-вибір (comparison preview) — коли показувати замість описувати»; те, заради чого посилаються (сповільнений прогін, проміжки кадрів, текстові важелі), виселено в маніфест стенда (`kernel/wsd/Lens_verdict_protocol.md:139`). Чотири посилання — коло:
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:139` — «Гард-набір — wsd 2.4» → там «поїхало в A83» (`kernel/wsd/Lens_verdict_protocol.md:145`) → A83;
`kernel/cookbook/Lens_iOS_cookbook_5_motion.md:476` — «що й лівий accent-rail (wsd 2.4)» · `kernel/cookbook/Lens_iOS_cookbook_5_motion.md:500` — «wsd 2.4 (анти-патерн декоративного акценту)» · `kernel/cookbook/Lens_iOS_cookbook_3_material.md:506` — «wsd 2.4 (маршрут до арсеналу)» → A84.
Інші переїзди (номери живі, файл інший): 6.5 і 6.6 → `kernel/Lens_excel_protocol.md:159` і `:174`; 3.9, 3.10, 10.2, 10.6 → `kernel/wsd/Lens_patch_check_protocol.md`; 14.x → `kernel/wsd/Work_Standard_HISTORY.md`; «Д-9» (`kernel/cookbook/Lens_iOS_cookbook_3_material.md:853`) → тепер 4.5 (`kernel/wsd/Lens_verdict_protocol.md:587`). Певність висока. **Дія:** чотири кола — руками (клас 0); решту тримає прилад рядками ⓘ.

**Н4 · Внутрішні вказівники.**
`kernel/cookbook/Lens_iOS_cookbook_1_platform.md:654` — «(див. уточнення в A11)» — уточнення в A79 (С11).
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:435` — «(правило F12 / B3)» — «F12» більше ніде в `kernel/cookbook/` і `kernel/wsd/` нема.
`kernel/cookbook/Lens_cookbook_INDEX.md:333` — «`Lens_glass_FINDINGS` Ф-3» і `kernel/cookbook/Lens_iOS_cookbook_4_components.md:782` — якоря «Ф-3» у `kernel/Lens_glass_FINDINGS.md` нема (греп).
`kernel/cookbook/Lens_bot_cookbook_6_telegram_workers.md:177` — «(лоток: «i» tip-popover)» — запис змерджено в A116 19.10.2026.
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:755` — «Cookbook том 2 (механіка bottom sheet, свайп, VisualViewport)» — VisualViewport у томі 4 (B2).
`kernel/cookbook/Lens_iOS_cookbook_4_components.md:213` — «фізично стоять між A47 і A48» — після розпилу A48 у томі 3.
Певність висока. **Дія:** шість правок класу 0.

**Н5 · Чого індекс не знає.** A18.1 і A66.1 нема ні в §2, ні в §3 (прилад §7), хоча на A66.1 посилаються рецепти томів 3 і 4. Ланцюги §4: `kernel/cookbook/Lens_cookbook_INDEX.md:332` — «`A93` радіус-мова» — A93 переписано 18.10.2026 («Статус ≠ кнопка»), і всі три записи рядка лежать у томі 4, а в колонці — «4 ← 3». Номери A77, A78, A103 пояснені лише в лотку; A74 веде на файл поза репо (`kernel/cookbook/Lens_cookbook_INDEX.md:37`). **Дія:** два рядки в §3, правка рядка §4, рядок «вибулі номери» в §1.

**Н6 · Межа публічності.** Двері ядра: `CLAUDE.md:8` — «Посилання на приватні репо — лише `Репо:шлях`, без вмісту.» Кілька рецептів несуть заміри й будову приватного продукту, не лише шлях: `kernel/cookbook/Lens_iOS_cookbook_4_components.md:1062`, `kernel/cookbook/Lens_iOS_cookbook_4_components.md:1064`, `kernel/cookbook/Lens_iOS_cookbook_3_material.md:381`. Секретів там нема. Певність середня: це питання межі, не помилка — рецепт без заміру слабший. **Дія:** рішення Konst (§9, Р5): або правило уточнити («заміри продукту в рецепті — можна, дані людей і тексти — ні»), або знеособити.

## 7. Що може тримати машина — чернетка `cookbook_check.py`

Запущена з кореня ядра 11.11.2026 (Python 3, без залежностей, лише читає). Перевіряє: шапка тому ≡ заголовки · вага в індексі ≡ файл (±10 %) · мапа §3 ↔ заголовки · номери wsd → у якому файлі вони сьогодні · названі файли-джерела поза репо · число міток «чекає / перевірити / не перевірено».

Вивід (27 рядків, тут — підсумок і всі ⚠):
```text
⚠ том 1: шапка не знає 7 записів: A79 A80 A81 A85 A110 A111 A115
⚠ том 1: індекс каже 56.5 KB, файл 83.5
⚠ том 2: шапка не знає 3 записів: A18.1 A108 A109
⚠ том 2: індекс каже 46.0 KB, файл 65.4
⚠ том 3: шапка не знає 17 записів: A35.1 A66.1 A66.2 A84 A87 A88 A95 A96 A97 A98 A99 A100 A101 A101-б A102 A104 A117
⚠ том 3: індекс каже 84.4 KB, файл 116.3
⚠ том 4: шапка не знає 1 записів: A89-б
⚠ том 4: індекс каже 70.6 KB, файл 122.3
⚠ A18.1 (том 2:57) — індекс не згадує ніде
⚠ A66.1 (том 3:410) — індекс не згадує ніде
⚠ файлів-джерел поза репо: 26 (напр. StockCheck_session_summary_dpicker_LOCK.md, QR_Lens_preview_batch22.html, Drive_Lens_preview_batch10_2.html)
ⓘ міток «pending / перевірити при / не перевірено»: 20
кукбук: записів 148 · індекс §3 141 · ✗ 0 · ⚠ 11
```
**Зуби:** у копії кукбука заголовок `## A52.` перейменовано → `✗ індекс:212 → A52: заголовка нема в жодному томі`, код виходу 1.
**Чого прилад не бачить:** суперечностей змісту (§2), дублів (§3), застарілих тверджень про платформу (§4) — це лише читанням. «148 записів» — разом із підномерами (A18.1, B3.2 …); «140 рецептів» у §5 — лише заголовки рівня `##`.

```python
#!/usr/bin/env python3
# cookbook_check.py — чернетка FAB-1 (предмет 5): звіряє кукбук сам із собою і з ядром. Лише читає.
# Запуск з кореня ядра: python3 cookbook_check.py [корінь ядра]   · exit 1, коли є ✗
import glob, os, re, subprocess, sys
root = sys.argv[1] if len(sys.argv) > 1 else '.'
cb = os.path.join(root, 'kernel/cookbook')
vols = {v: f for f in sorted(glob.glob(cb + '/Lens_*cookbook_[1-6]_*.md')) for v in [re.search(r'_(\d)_', f).group(1)]}
bad = warn = 0
def out(mark, text):
    global bad, warn
    bad += mark == '✗'; warn += mark == '⚠'; print(mark, text)
heads = {}                                   # номер → (том, рядок)
for v, f in vols.items():
    L = open(f, encoding='utf-8').read().split('\n')
    mine = []
    for i, l in enumerate(L, 1):
        m = re.match(r'^#{2,3}\s+((?:A|B|T)\d+(?:\.\d+)?(?:-б)?)[. ·]', l) or re.match(r'^\*\*((?:A|B)\d+\.\d+)\.', l)
        if m: heads[m.group(1)] = (v, i); mine.append(m.group(1))
    hdr = next((l for l in L[:16] if 'Записи тому' in l and ':**' in l), None)
    if hdr:                                  # 1. шапка тому ≡ заголовки
        said = set(re.findall(r'\b[AB]\d+(?:\.\d+)?', hdr.split(':**', 1)[1]))
        miss = [h for h in mine if h not in said and not h.startswith('B')]
        if miss: out('⚠', f'том {v}: шапка не знає {len(miss)} записів: {" ".join(miss)}')
    kib = os.path.getsize(f) / 1024          # 2. вага в індексі
    idx_txt = open(cb + '/Lens_cookbook_INDEX.md', encoding='utf-8').read()
    m = re.search(r'`' + re.escape(os.path.basename(f)) + r'`.*?\|\s*([\d.]+) KB', idx_txt)
    if m and abs(float(m.group(1)) - kib) / kib > 0.10: out('⚠', f'том {v}: індекс каже {m.group(1)} KB, файл {kib:.1f}')
I = open(cb + '/Lens_cookbook_INDEX.md', encoding='utf-8').read().split('\n')
idx = {}
for i, l in enumerate(I, 1):                 # 3. мапа §3 ↔ заголовки
    m = re.match(r'^\| `((?:A|B|T)[\d.]+)` \|.*\| \*\*(\d)\*\* \|$', l)
    if m: idx[m.group(1)] = (m.group(2), i)
for k, (v, i) in idx.items():
    if k not in heads: out('✗', f'індекс:{i} → {k}: заголовка нема в жодному томі')
    elif heads[k][0] != v: out('✗', f'індекс:{i} → {k}: том {v}, а лежить у томі {heads[k][0]}')
whole = '\n'.join(I)
for k, (v, i) in heads.items():
    if k not in idx and not re.search(r'`' + re.escape(k) + r'[`\s(]', whole): out('⚠', f'{k} (том {v}:{i}) — індекс не згадує ніде')
wsd = {}                                     # 4. номери wsd → де вони сьогодні
for f in glob.glob(root + '/kernel/wsd/*.md') + [root + '/kernel/Lens_excel_protocol.md']:
    for l in open(f, encoding='utf-8'):
        m = re.match(r'^## (\d{1,2}\.\d{1,2}(?:-[а-я])?) ', l)
        if m: wsd.setdefault(m.group(1), []).append(os.path.basename(f))
cited = {}
files = sorted(glob.glob(cb + '/*.md'))
for f in files:
    for i, l in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'(?:wsd|Work_Standard\.md`?) (\d{1,2}\.\d{1,2}|Д-\d+)', l): cited.setdefault(m.group(1), []).append(f'{os.path.basename(f)[5:19]}:{i}')
for n in sorted(cited, key=lambda s: [int(t) for t in re.findall(r'\d+', s)]):
    homes = wsd.get(n, []); home = 'Work_Standard.md' if 'Work_Standard.md' in homes else (homes[0] if homes else None)
    if not home: out('⚠', f'wsd {n}: заголовка нема ({len(cited[n])} посилань, перше {cited[n][0]})')
    elif home != 'Work_Standard.md': print('ⓘ', f'wsd {n} живе в {home} ({len(cited[n])} посилань)')
tracked = {os.path.basename(p) for p in subprocess.run(['git', '-C', root, 'ls-files'], capture_output=True, text=True).stdout.split('\n')}
gone = {}                                    # 5. названі файли-джерела, яких у репо нема
for f in files:
    for i, l in enumerate(open(f, encoding='utf-8'), 1):
        for m in re.finditer(r'(?<![:\w/])`?((?:QR_Lens|Drive_Lens|StockCheck|EquipLens|KPI_Lens|Lens)_[\w.]+\.(?:html|js|py|md))', l):
            if m.group(1) not in tracked: gone.setdefault(m.group(1), f'{os.path.basename(f)[5:19]}:{i}')
if gone: out('⚠', f'файлів-джерел поза репо: {len(gone)} (напр. {", ".join(list(gone)[:3])})')
age = sum(len(re.findall(r'pending|Перевірити при|не перевірено', open(f, encoding='utf-8').read())) for f in files)
print('ⓘ', f'міток «pending / перевірити при / не перевірено»: {age}')   # 6. вік — лише число
print(f'кукбук: записів {len(heads)} · індекс §3 {len(idx)} · ✗ {bad} · ⚠ {warn}')
sys.exit(1 if bad else 0)
```

Куди це могло б піти (пропозиція, §9 Р6): `tools/claude-code/` ядра, рядок ⚠ у `tools/env_check.sh`; шапки томів і вагу краще **не перевіряти, а прибрати** з файлів — число, яке застаріває з кожним рецептом, не має жити в тексті (той самий урок уже записаний у дверях ядра про числа тестів).

## 8. Що взяти першим — за цінністю і ціною

| № | що | ціна | чому першим |
|---|---|---|---|
| 1 | С5: виправити тіло A65 | 4 рядки, правка рецепта | рецепт сьогодні вчить помилки, яку сам визнав |
| 2 | С1, С2: A15 → межа; A17 і A19 під A108 | 1 рядок + переписати два короткі рецепти | найчастіший шлях (панель, шіт) має дві редакції |
| 3 | П1: рядки «ПК: …» в індексі §2 | 8–10 рядків, клас 0 | ПК-знання вже є, його лише не знайти |
| 4 | Н3, Н4, С12: кола wsd 2.4, шість мертвих вказівників, «чотири механізми» | ≈ 13 правок класу 0 | дешево, знімає хибні сліди |
| 5 | §7: прилад у `env_check`, шапки й вагу — геть із тексту | 63 рядки вже є | перестає старіти те, що старіє саме |
| 6 | Р7: перегляд лотка (термін 19.11.2026) | один хід | 3 кандидати закриваються цим звітом, 1 готовий у том |
| 7 | В5–В7: дата повторної перевірки в кожному спостереженні про платформу — за зразком A105 | формат + 20 рядків перегляду | «перевірити при наступному iOS» без дати не спрацьовує |
| 8 | С7: одна відповідь про активний фільтр | вирок Konst + 2 рядки | чотири редакції — чотири різні екрани |
| 9 | П3–П6: рецепти ПК (оболонка · стани · клавіатура й фокус · вікно) | 4 рецепти, окремими ходами | найбільша прогалина, але й найдорожча |
| 10 | П2: розпил A117 | підзаголовки — дешево; номери — дорожче | щоб ПК-рецепт читався точково |

## 9. Рішення для Konst

- **Р1 · Позначка пристрою.** Біля ✅ кожного рецепта — 📱 / 🖥 / обидва, і другий рядок тестової бази в індексі. *Чим краще:* прогалину для ПК видно з мапи. *Ціна:* один хід на 140 рядків мапи; судження «на чому перевірено» — з провенансу рецепта. *Ризик:* частина рецептів без провенансу — позначка «невідомо».
- **Р2 · Рецепти ПК — зараз чи коли попросить другий продукт.** Правило ядра: `CLAUDE.md:6` — «лише те, що потрібне **більш ніж одному** проєкту». Сьогодні продукт для ПК один. Варіанти: (а) писати чотири рецепти зараз із того, що в продукті вже перевірено; (б) лише розкласти наявне (П1, П2) і чекати другого споживача. Моя ставка — (б) плюс К-2 у том: дешево й нічого не вигадує.
- **Р3 · Активний фільтр (С7):** яка редакція чинна — «без заливки, тон і кільце» (16.10.2026) чи «западина» (21.08.2026)? Від відповіді залежить, який рецепт стає вказівником.
- **Р4 · Борги індексу §6:** A68 (метод, не рецепт), Частина B, Частина C — робимо (рядок у чергу ядра) чи закриваємо «не робимо»?
- **Р5 · Заміри приватного продукту в публічних рецептах (Н6):** лишаємо й уточнюємо правило, чи знеособлюємо?
- **Р6 · Прилад `cookbook_check.py`:** у `tools/claude-code/` і `env_check` — чи разовий, лише для цього звіту?
- **Р7 · Перегляд лотка 19.11.2026** — пропозиція по 12 кандидатах: К-6 і К-1 — закрити (вже в томах, Д4) · К-7 — відкинути (суперечить A18 і A70) · К-2 — у том (є другий випадок і прилад) · К-8 — лишити, дописавши межу (`text-wrap: pretty` — BCD: Safari 26, Firefox — ні) · решта сім — лишити з новою датою, вироку пристрою нема.

## 10. Чого тут нема і як перевірити звіт

**Нема / не перевірено:** жодного рецепта не запускав у браузері й на пристрої — усе про поведінку коду (С2, С13, В1) виведено з тексту; репо продуктів не відкривав (Н1); `VOICE.md`, `SHOTS.md`, бриф `MOTION-1` на перетин із кукбуком не звіряв; том 6 (бот) на зовнішні зміни Bot API й лімітів Cloudflare не перевіряв — у ньому знайшов лише вказівник із Н4 і порядок частин (1, 2, 4, 3); номери перевірок `ui_lint`, на які посилаються рецепти (23 номери), звірив лише з шапкою `tools/claude-code/ui_lint.mjs` — усі там є, поведінку не ганяв.

**Звірка цитат цього звіту:** кожне `файл:рядок` — «цитата» перевірено скриптом (цитата є в цьому рядку файла) — ✓ 148 · ✗ 0; посилань без цитати — 31 (перевірено, що файл і рядок існують).

**Як повторити:**
```bash
# з кореня ядра; код приладу — блок у §7 цього файла
python3 - <<'PY' > /tmp/cookbook_check.py
import re; s=open('sessions/FAB-1/FAB-1_cookbook.md',encoding='utf-8').read()
print(re.search(r'```python\n(.*?)```', s, re.S).group(1), end='')
PY
python3 /tmp/cookbook_check.py .          # ✗ 0 · ⚠ 11
# рецептів і згадок ПК (§5)
python3 - <<'PY'
import re,glob
tot=pc=0
for f in sorted(glob.glob('kernel/cookbook/Lens_*cookbook_[1-6]_*.md')):
    L=open(f,encoding='utf-8').read().split('\n'); idx=[i for i,l in enumerate(L) if re.match(r'^## (?:A|B|T)\d+',l)]
    for a,b in zip(idx,idx[1:]+[len(L)]):
        tot+=1; pc+=len(re.findall(r'\bПК\b|1920|миш[ауі]|мишею|наведенн|:hover|Tab\b|Escape|Esc\b','\n'.join(L[a:b])))>=2
print(tot,pc)                              # 140 19
PY
grep -c ':hover' kernel/cookbook/Lens_iOS_cookbook_[1-5]_*.md   # 0 у кожному
```
