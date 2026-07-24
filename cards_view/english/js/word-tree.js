document.addEventListener("DOMContentLoaded", () => {
});

{
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
        const raw = dataNode.textContent.trim();

        let tree = null;
        if (raw) {
            try {
                tree = JSON.parse(raw);
            } catch (e) {
                console.log("word-tree: failed to parse JSON, falling back to sample data", e);
            }
        }

        let partsOfSpeech = (tree && tree.parts_of_speech) || [];
        if (partsOfSpeech.length === 0) {
            partsOfSpeech = SAMPLE_TREE.parts_of_speech;
        }

        // Excludes the card's own entry from the tree, held in data-pos/data-sense/
        // data-definition (layout of the main pos/sense/definition differs across
        // card types, so it isn't read off the rendered DOM). A sense left with no
        // definitions, or a part-of-speech left with no senses, is dropped too.
        const currentPos = (blockNode.dataset.pos || "").trim();
        const currentSense = (blockNode.dataset.sense || "").trim();
        const currentDefinition = (blockNode.dataset.definition || "").trim();

        partsOfSpeech = partsOfSpeech
            .map(pos => {
                const senses = (pos.senses || [])
                    .map(sense => {
                        const isCurrentSense = (pos.part_of_speech || "").trim() === currentPos
                            && (sense.sense || "").trim() === currentSense;

                        const definitions = (sense.definitions || []).filter(def => {
                            return !(isCurrentSense && def.trim() === currentDefinition);
                        });

                        return { ...sense, definitions };
                    })
                    .filter(sense => sense.definitions.length > 0);

                return { ...pos, senses };
            })
            .filter(pos => pos.senses.length > 0);

        if (partsOfSpeech.length === 0) {
            blockNode.remove();
            console.log("word-tree: no data, removed block");
        } else {
            // transcription is only shown per part-of-speech when it differs from
            // the card's own trans, held in data-trans (layout of the main trans
            // differs across card types, so it isn't read off the rendered DOM)
            const mainTrans = (blockNode.dataset.trans || "").trim();

            partsOfSpeech.forEach(pos => {
                const posBlock = document.createElement("div");
                posBlock.className = "word-tree-pos-block";

                const posHeader = document.createElement("div");
                posHeader.className = "word-tree-pos-header";

                const posSpan = document.createElement("span");
                posSpan.className = "pos-span";
                posSpan.textContent = pos.part_of_speech || "";
                posHeader.appendChild(posSpan);

                if (pos.trans && pos.trans !== mainTrans) {
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
