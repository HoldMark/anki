document.addEventListener("DOMContentLoaded", () => {
});

{
    // .word-tree-data holds the raw word_tree JSON (see sync/src/sync/word_tree.py).
    const dataNode = document.querySelector(".word-tree-data");
    const blockNode = document.querySelector(".basic-block-word-tree");
    const bodyNode = document.querySelector(".body-word-tree");

    if (dataNode && blockNode && bodyNode) {
        const raw = dataNode.textContent.trim();

        let tree = null;
        let parseFailed = false;
        if (raw) {
            try {
                tree = JSON.parse(raw);
            } catch (e) {
                parseFailed = true;
                console.error("word-tree: failed to parse JSON", e);
            }
        }

        if (parseFailed) {
            // Corrupted field: show an error state instead of hiding the block or
            // showing unrelated data. No click handler attached, so it can't expand.
            blockNode.classList.add("word-tree-error");
            const titleNode = blockNode.querySelector(".collapsible-title");
            if (titleNode) {
                titleNode.textContent = "JSON error";
            }
        } else {
            let partsOfSpeech = (tree && tree.parts_of_speech) || [];

            // word_tree includes the current card's own definition too, so a word
            // with only one definition total has nothing "other" to show.
            const totalDefinitions = partsOfSpeech.reduce((total, pos) => {
                return total + (pos.senses || []).reduce((s, sense) => s + (sense.definitions || []).length, 0);
            }, 0);

            // Strips HTML and collapses whitespace, so text read off data-*
            // attributes (which can carry tags Anki's editor added) lines up with
            // the plain-text word_tree JSON when compared below.
            function normalizeFieldText(str) {
                const scratch = document.createElement("div");
                scratch.innerHTML = str || "";
                return (scratch.textContent || "").replace(/\s+/g, " ").trim();
            }

            const currentPos = normalizeFieldText(blockNode.dataset.pos);
            const currentSense = normalizeFieldText(blockNode.dataset.sense);
            const currentDefinition = normalizeFieldText(blockNode.dataset.definition);

            // Drop the card's own definition, then any sense/pos left empty by that.
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

            // Card's own part-of-speech first; everything else keeps build_word_trees'
            // first-seen order (stable sort).
            partsOfSpeech.sort((a, b) => {
                const aIsCurrent = normalizeFieldText(a.part_of_speech) === currentPos;
                const bIsCurrent = normalizeFieldText(b.part_of_speech) === currentPos;
                return aIsCurrent === bIsCurrent ? 0 : aIsCurrent ? -1 : 1;
            });

            if (totalDefinitions <= 1 || partsOfSpeech.length === 0) {
                blockNode.remove();
                console.log("word-tree: no other meanings, removed block");
            } else {
                // Only shown per part-of-speech when it differs from the card's own.
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
            }
        }
    }
}
