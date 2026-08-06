// Собирает шаблон + CSS + JS + тестовые поля в один документ, рендерит в
// iframe через srcdoc. Ограничения — см. docs/notes.md.

// Тестовые данные word_tree для word-tree.js. Формат — см. docs/notes.md.
const WORD_TREE_SAMPLE = {
	word: "run",
	parts_of_speech: [
		{
			part_of_speech: "verb",
			trans: "/rʌn/",
			trans_type: "(uk)",
			senses: [
				{
					sense: "MOVE",
					definitions: [
						"to move fast using your legs",
						"to go regularly to a place by a particular means of transport",
					],
				},
				{
					sense: "OPERATE",
					definitions: ["to control or manage something, or to make it work"],
				},
			],
		},
		{
			part_of_speech: "noun",
			trans: "/rʌn/",
			trans_type: "(uk)",
			senses: [
				{
					sense: "ACT OF RUNNING",
					definitions: ["a period of running, or a distance covered by running"],
				},
				{
					sense: "",
					definitions: ["an enclosed area where chickens or other animals can move around freely"],
				},
			],
		},
	],
};

// Общий набор полей для всех словарных карточек.
function vocabFields(overrides = {}) {
	return {
		word: "run",
		trans: "/rʌn/", // IPA transcription, not translation
		trans_type: "(uk)", // accent variant: (uk) or (us)
		part_of_speech: "verb",
		sense: "run (verb)",
		definition: "to move quickly on foot so that both feet leave the ground during each stride",
		example_1: "She runs five miles every morning.",
		example_2: "Don't run in the hallway.",
		example_3: "",
		example_4: "",
		example_5: "",
		example_6: "",
		example_7: "",
		audio: "[sound:run.mp3]",
		video: "",
		hints: "irreg;",
		picture: "[picture placeholder]",
		word_tree: JSON.stringify(WORD_TREE_SAMPLE, null, 2),
		...overrides,
	};
}

const GEORGIAN_OVERRIDES = {
	word: "გაქცევა",
	trans: "gakcheva", // transliteration, not translation
	trans_type: "",
	sense: "run (verb)",
	definition: "to move quickly using your legs",
	example_1: "ის სწრაფად გარბის.",
	audio: "[sound:gakcheva.mp3]",
};

const CARD_TYPES = [
	{
		id: "english-word",
		label: "english / word",
		dir: "../english/cards/word/",
		css: "../english/style.css",
		jsDir: "../english/js/",
		fields: vocabFields(),
	},
	{
		id: "english-definition",
		label: "english / definition",
		dir: "../english/cards/definition/",
		css: "../english/style.css",
		jsDir: "../english/js/",
		fields: vocabFields(),
	},
	{
		id: "english-typing",
		label: "english / typing",
		dir: "../english/cards/typing/",
		css: "../english/style.css",
		jsDir: "../english/js/",
		fields: vocabFields(),
	},
	{
		id: "english-sentence_typing",
		label: "english / sentence_typing",
		dir: "../english/cards/sentence_typing/",
		css: "../english/style.css",
		jsDir: "../english/js/",
		fields: vocabFields(),
	},
	{
		id: "georgian-word",
		label: "georgian / word",
		dir: "../georgian/word/",
		css: "../georgian/style.css",
		jsDir: "../georgian/js/",
		fields: vocabFields(GEORGIAN_OVERRIDES),
	},
	{
		id: "georgian-definition",
		label: "georgian / definition",
		dir: "../georgian/definition/",
		css: "../georgian/style.css",
		jsDir: "../georgian/js/",
		fields: vocabFields(GEORGIAN_OVERRIDES),
	},
	{
		id: "task",
		label: "task",
		dir: "../task/",
		css: "../task/style.css",
		jsDir: null,
		fields: {
			theme: "present simple",
			question: "Write a sentence using \"run\" in the present simple.",
			answer: "She runs every morning.",
		},
	},
	{
		id: "common-base",
		label: "common / base",
		dir: "../common/base/",
		css: "../common/style.css",
		jsDir: null,
		fields: {
			theme: "theme",
			question: "Question text goes here.",
			answer: "Answer text goes here.",
		},
	},
	{
		id: "common-typing",
		label: "common / typing",
		dir: "../common/typing/",
		css: "../common/style.css",
		jsDir: null,
		fields: {
			theme: "theme",
			question: "Question text goes here.",
			answer: "Answer text goes here.",
		},
	},
	{
		id: "common-verses",
		label: "common / verses",
		dir: "../common/verses/",
		css: "../common/verses/style.css",
		jsDir: "../common/verses/",
		rawFields: ["verse"],
		fields: {
			name: "Исповедь",
			author: "Редьярд Киплинг",
            verse:
                "<p>Владей собой среди толпы смятенной,</p>\n" +
                "<p>Тебя клянущей за смятенье всех, </p>\n" +
                "<p>Верь сам в себя, наперекор вселенной, </p>\n" +
                "<p>И маловерным отпусти их грех; </p>\n" +
                "<p>Пусть час не пробил, жди, не уставая, </p>\n" +
                "<p>Пусть лгут лжецы, не снисходи до них; </p>\n" +
                "<p>Умей прощать и не кажись, прощая, </p>\n" +
                "<p>Великодушней и мудрей других.</p>\n" +
                "<br>\n" +
                "<p>Умей мечтать, не став рабом мечтанья, </p>\n" +
                "<p>И мыслить, мысли не обожествив; </p>\n" +
                "<p>Равно встречай успех и поруганье, </p>\n" +
                "<p>Не забывая, что их голос лжив; </p>\n" +
                "<p>Останься тих, когда твое же слово </p>\n" +
                "<p>Калечит плут, чтоб уловить глупцов, </p>\n" +
                "<p>Когда вся жизнь разрушена, и снова </p>\n" +
                "<p>Ты должен все воссоздавать с основ.</p>\n" +
                "<br>\n" +
                "<p>Умей поставить в радостной надежде </p>\n" +
                "<p>На карту все, что накопил с трудом,</p>\n" +
                "<p>Все проиграть и нищим стать, как прежде,</p>\n" +
                "<p>И никогда не пожалеть о том. </p>\n" +
                "<p>Умей принудить сердце, нервы, тело</p>\n" +
                "<p>Тебе служить, когда в твоей груди </p>\n" +
                "<p>Уже давно все пусто, все сгорело, </p>\n" +
                "<p>И только воля говорит: «Иди»!</p>\n" +
                "<br>\n" +
                "<p>Останься прост, беседуя с царями,</p>\n" +
                "<p>Будь честен, говоря с толпой; </p>\n" +
                "<p>Будь прям и тверд с врагами и друзьями.</p>\n" +
                "<p>Пусть все в свой час считаются с тобой; </p>\n" +
                "<p>Наполни смыслом каждое мгновенье </p>\n" +
                "<p>Часов и дней неуловимый бег- </p>\n" +
                "<p>Тогда весь мир ты примешь во владенье, </p>\n" +
                "<p>Тогда, мой сын, ты будешь человек.</p>\n",
		},
	},
];

const state = {
	cardType: CARD_TYPES[0],
	side: "front",
	values: { ...CARD_TYPES[0].fields },
};

const $ = (id) => document.getElementById(id);

function escapeHtml(str) {
	return str
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;");
}

function setStatus(message) {
	const el = $("status");
	if (!message) {
		el.textContent = "";
		el.classList.remove("visible");
		return;
	}
	el.textContent = message;
	el.classList.add("visible");
}

function populateCardTypeSelect() {
	const select = $("cardType");
	select.innerHTML = "";
	for (const entry of CARD_TYPES) {
		const option = document.createElement("option");
		option.value = entry.id;
		option.textContent = entry.label;
		select.appendChild(option);
	}
	select.value = state.cardType.id;
}

function buildFieldsForm() {
	const form = $("fieldsForm");
	form.innerHTML = "";
	for (const fieldName of Object.keys(state.cardType.fields)) {
		const row = document.createElement("div");
		row.className = "field-row";

		const label = document.createElement("label");
		label.textContent = fieldName;
		label.setAttribute("for", `field-${fieldName}`);

		const textarea = document.createElement("textarea");
		textarea.id = `field-${fieldName}`;
		textarea.value = state.values[fieldName] ?? "";
		textarea.addEventListener("input", () => {
			state.values[fieldName] = textarea.value;
			scheduleRender();
		});

		row.appendChild(label);
		row.appendChild(textarea);
		form.appendChild(row);
	}
}

async function fetchText(url) {
	const response = await fetch(url, { cache: "no-store" });
	if (!response.ok) {
		throw new Error(`${response.status} ${url}`);
	}
	return response.text();
}

function substituteFields(html, values, rawFields = []) {
	let result = html.replace(/\{\{type:([a-zA-Z0-9_]+)\}\}/g, (_, field) => {
		const value = values[field] ?? "";
		return `<span class="preview-typed-value">${escapeHtml(value)}</span>`;
	});
	result = result.replace(/\{\{([a-zA-Z0-9_]+)\}\}/g, (_, field) => {
		const value = values[field];
		if (value === undefined) return "";
		return rawFields.includes(field) ? value : escapeHtml(value);
	});
	return result;
}

async function render() {
	const entry = state.cardType;
	const templateUrl = `${entry.dir}${state.side}.html`;

	let templateHtml;
	let css;
	try {
		[templateHtml, css] = await Promise.all([fetchText(templateUrl), fetchText(entry.css)]);
	} catch (err) {
		setStatus(`Failed to load template/CSS: ${err.message}`);
		return;
	}

	const scriptSrcs = [...templateHtml.matchAll(/<script\s+src="([^"]+)"><\/script>/g)].map((m) => m[1]);
	const bodyHtml = templateHtml.replace(/<script\s+src="[^"]+"><\/script>\s*/g, "");

	const scriptResults = await Promise.allSettled(
		scriptSrcs.map((src) => fetchText(`${entry.jsDir ?? entry.dir}${src}`)),
	);

	const missing = [];
	const scripts = [];
	scriptResults.forEach((result, i) => {
		if (result.status === "fulfilled") {
			scripts.push(result.value);
		} else {
			missing.push(scriptSrcs[i]);
			console.warn(`Preview: skipping missing script "${scriptSrcs[i]}" for ${entry.id} — ${result.reason}`);
		}
	});

	if (missing.length > 0) {
		setStatus(
			`${missing.length} script(s) skipped (not found as static files — likely injected at runtime by an addon): ${missing.join(", ")}. See console.`,
		);
	} else {
		setStatus("");
	}

	const processedBody = substituteFields(bodyHtml, state.values, entry.rawFields ?? []);

	const doc = `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>${css}</style>
</head>
<body class="card">
${processedBody}
<script>
${scripts.join("\n")}
</script>
</body>
</html>`;

	$("cardFrame").srcdoc = doc;
}

let renderTimer = null;
function scheduleRender() {
	clearTimeout(renderTimer);
	renderTimer = setTimeout(render, 250);
}

function selectCardType(id) {
	const entry = CARD_TYPES.find((c) => c.id === id);
	if (!entry) return;
	state.cardType = entry;
	state.values = { ...entry.fields };
	buildFieldsForm();
	render();
}

function selectSide(side) {
	state.side = side;
	$("sideFront").classList.toggle("active", side === "front");
	$("sideBack").classList.toggle("active", side === "back");
	render();
}

$("cardType").addEventListener("change", (e) => selectCardType(e.target.value));
$("sideFront").addEventListener("click", () => selectSide("front"));
$("sideBack").addEventListener("click", () => selectSide("back"));

populateCardTypeSelect();
buildFieldsForm();
render();
