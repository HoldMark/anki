document.addEventListener("DOMContentLoaded", () => {
});

{
    // .word-tree-data holds the raw word_tree JSON (see SAMPLE_TREE below for its
    // shape). .basic-block-word-tree is the whole "Other meanings" block, including
    // its header/accordion. .body-word-tree is where the rendered pos/sense/
    // definition markup gets appended.
    const dataNode = document.querySelector(".word-tree-data");
    const blockNode = document.querySelector(".basic-block-word-tree");
    const bodyNode = document.querySelector(".body-word-tree");

    // Anki's Card Types editor renders the preview without a note bound to it
    // (e.g. opened from Manage Note Types) by dropping the field name in as
    // placeholder text instead of real field content, so parsing fails. Falls
    // back to sample data in that case, purely so the layout is visible there.
    const SAMPLE_TREE = {
        parts_of_speech: [
            {
                part_of_speech: "verb",
                trans: "/rʌn/",
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

    if (dataNode && blockNode && bodyNode) {
        // JSON written to the note's word_tree field by anki_sync's word-tree
        // command (see sync/src/sync/word_tree.py) — one entry per part of speech
        // the word has, each with its own senses and, under each sense, the list
        // of definitions.
        const raw = dataNode.textContent.trim();

        let tree = null;
        if (raw) {
            try {
                tree = JSON.parse(raw);
            } catch (e) {
                console.log("word-tree: failed to parse JSON, falling back to sample data", e);
            }
        }

        // Use the real tree when there is one; otherwise fall back to sample data
        // (only actually hit in the Card Types editor preview, see comment above).
        let partsOfSpeech = (tree && tree.parts_of_speech) || [];
        if (partsOfSpeech.length === 0) {
            partsOfSpeech = SAMPLE_TREE.parts_of_speech;
        }

        // Total leaf definitions across the whole tree, counted before the
        // current-entry exclusion below. word_tree is built from every note that
        // shares this word, including the current one (see word_tree.py's
        // build_word_trees) — so if the word only has one definition in total,
        // that definition IS the current card's own, and there is nothing "other"
        // left to show no matter how the exclusion below turns out. This is the
        // primary guard for hiding the block on single-meaning words; it doesn't
        // depend on the pos/sense/definition text matching exactly.
        const totalDefinitions = partsOfSpeech.reduce((total, pos) => {
            return total + (pos.senses || []).reduce((s, sense) => s + (sense.definitions || []).length, 0);
        }, 0);

        // Field text read off a data-* attribute can carry HTML tags Anki's rich-
        // text editor wraps content in (e.g. a field edited as multiple lines
        // often becomes "<div>...</div>"). Attribute values aren't HTML-parsed the
        // way element content is, so those tags stay as literal characters instead
        // of being stripped — "<div>a route that leads to a place</div>" instead of
        // "a route that leads to a place". The word_tree JSON's own text doesn't
        // have this problem (it went through dataNode.textContent above, which
        // already discards any real tags), so without normalizing both sides the
        // same way, an unwrapped field would never match its wrapped twin and the
        // card's own entry would stay in the "other meanings" list. Routing the
        // string through a scratch element's innerHTML/textContent strips tags and
        // decodes entities the same way textContent did, and collapsing/trimming
        // whitespace absorbs any formatting differences on top of that.
        function normalizeFieldText(str) {
            const scratch = document.createElement("div");
            scratch.innerHTML = str || "";
            return (scratch.textContent || "").replace(/\s+/g, " ").trim();
        }

        // Card's own part-of-speech/sense/definition, read off data attributes
        // rather than the rendered DOM, since the layout of the main pos/sense/
        // definition differs across card types (definition.html vs word.html etc).
        const currentPos = normalizeFieldText(blockNode.dataset.pos);
        const currentSense = normalizeFieldText(blockNode.dataset.sense);
        const currentDefinition = normalizeFieldText(blockNode.dataset.definition);

        // Drop the current card's own definition from its sense (matched by
        // pos+sense+definition together, so an identical definition string under a
        // different sense/pos is left alone), then drop any sense left with no
        // definitions, and any part-of-speech left with no senses.
        partsOfSpeech = partsOfSpeech
            .map(pos => {
                const senses = (pos.senses || [])
                    .map(sense => {
                        const isCurrentSense = normalizeFieldText(pos.part_of_speech) === currentPos
                            && normalizeFieldText(sense.sense) === currentSense;

                        const definitions = (sense.definitions || []).filter(def => {
                            return !(isCurrentSense && normalizeFieldText(def) === currentDefinition);
                        });

                        return { ...sense, definitions };
                    })
                    .filter(sense => sense.definitions.length > 0);

                return { ...pos, senses };
            })
            .filter(pos => pos.senses.length > 0);

        // Card's own part-of-speech first (if it still has other senses/
        // definitions left after the exclusion above); everything else keeps
        // whatever order build_word_trees produced it in (first-seen, not sorted).
        // Array.sort is stable in every engine Anki's Qt WebEngine runs on, so
        // ties (score 0) preserve their relative order.
        partsOfSpeech.sort((a, b) => {
            const aIsCurrent = normalizeFieldText(a.part_of_speech) === currentPos;
            const bIsCurrent = normalizeFieldText(b.part_of_speech) === currentPos;
            return aIsCurrent === bIsCurrent ? 0 : aIsCurrent ? -1 : 1;
        });

        // Nothing left to show as an "other meaning": either the word never had
        // more than the one (current) definition to begin with (totalDefinitions,
        // the robust check), or the exclusion above emptied the tree some other
        // way. Either way, remove the whole block rather than leaving an empty
        // "Other meanings" header.
        if (totalDefinitions <= 1 || partsOfSpeech.length === 0) {
            blockNode.remove();
            console.log("word-tree: no other meanings, removed block");
        } else {
            // transcription is only shown per part-of-speech when it differs from
            // the card's own trans, held in data-trans (layout of the main trans
            // differs across card types, so it isn't read off the rendered DOM);
            // normalized for the same reason currentPos/Sense/Definition are above
            const mainTrans = normalizeFieldText(blockNode.dataset.trans);

            partsOfSpeech.forEach(pos => {
                const posBlock = document.createElement("div");
                posBlock.className = "word-tree-pos-block";

                const posHeader = document.createElement("div");
                posHeader.className = "word-tree-pos-header";

                const posSpan = document.createElement("span");
                posSpan.className = "pos-span";
                posSpan.textContent = pos.part_of_speech || "";
                posHeader.appendChild(posSpan);

                if (pos.trans && normalizeFieldText(pos.trans) !== mainTrans) {
                    const transSpan = document.createElement("span");
                    transSpan.className = "trans-span";
                    transSpan.textContent = pos.trans;
                    posHeader.appendChild(transSpan);
                }

                posBlock.appendChild(posHeader);

                // One block per sense, each with its own optional heading (senses
                // with no name, e.g. SAMPLE_TREE's second "noun" sense, just show
                // their definitions with no header) and a list of definitions.
                (pos.senses || []).forEach(sense => {
                    const senseBlock = document.createElement("div");
                    senseBlock.className = "word-tree-sense-block";

                    if (sense.sense) {
                        const senseHeader = document.createElement("div");
                        senseHeader.className = "word-tree-sense-header";

                        const senseSpan = document.createElement("span");
                        senseSpan.className = "sense-span";
                        senseSpan.textContent = sense.sense;
                        senseHeader.appendChild(senseSpan);

                        senseBlock.appendChild(senseHeader);
                    }

                    const defsList = document.createElement("ul");
                    defsList.className = "word-tree-definitions-list";

                    (sense.definitions || []).forEach(def => {
                        const li = document.createElement("li");
                        li.textContent = def;
                        defsList.appendChild(li);
                    });

                    senseBlock.appendChild(defsList);
                    posBlock.appendChild(senseBlock);
                });

                bodyNode.appendChild(posBlock);
            });

            console.log("word-tree: rendered " + partsOfSpeech.length + " parts of speech");

            // accordion: open by default, click the header to collapse/expand
            const headerNode = document.querySelector(".header-word-tree");
            if (headerNode) {
                headerNode.addEventListener("click", () => {
                    blockNode.classList.toggle("word-tree-collapsed");
                });
            }
        }
    }
}
