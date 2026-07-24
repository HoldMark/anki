// Assembles a cards_view template + its deck CSS + its JS files + sample field
// data into one document and renders it inside an iframe via srcdoc, so
// template/CSS/JS changes can be checked in a browser without opening Anki.
//
// Limitations (see plan / README note in preview.html):
// - {{picture}} / {{audio}} stay as plain placeholder text — no wiring to a
//   real collection.media folder.
// - {{type:Field}} typing fields are rendered as static styled text, not
//   Anki's live answer-input/grading box.
// - sentence_typing's request-task-from-python.js / request-task-review-to-python.js
//   are injected at runtime by the review_grammar addon and don't exist as
//   static files here — they are skipped with a console warning.

// Canonical field set/order shared by every vocab card type (word, trans,
// trans_type, part_of_speech, sense, definition, example_1..7, audio, video,
// hints), plus `picture` appended at the end (used by word/definition image
// blocks but not part of the order the user specified). Not every template
// reads every one of these — unused fields just have no visible effect.
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

function substituteFields(html, values) {
	let result = html.replace(/\{\{type:([a-zA-Z0-9_]+)\}\}/g, (_, field) => {
		const value = values[field] ?? "";
		return `<span class="preview-typed-value">${escapeHtml(value)}</span>`;
	});
	result = result.replace(/\{\{([a-zA-Z0-9_]+)\}\}/g, (_, field) => {
		const value = values[field];
		return value === undefined ? "" : escapeHtml(value);
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

	const processedBody = substituteFields(bodyHtml, state.values);

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
