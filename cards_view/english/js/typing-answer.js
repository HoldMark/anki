document.addEventListener("DOMContentLoaded", () => {
});

{
    // {{type:word}} isn't rendered when reviewing through a browser (AnkiWeb, whether on desktop
    // or mobile Safari/Chrome) - .body-typing stays empty there instead of getting Anki's native
    // #typeans input. Anki's own apps (desktop, AnkiMobile, AnkiDroid) all expose a pycmd() bridge
    // for template JS to call into native code; AnkiWeb has no native side, so it never defines
    // pycmd. That's the only reliable signal available here, so it gates this whole script -
    // everywhere pycmd exists, {{type:word}} already works natively and this script stays out.
    const isBrowserReview = typeof pycmd !== "function";
    console.log("typing-answer: isBrowserReview =", isBrowserReview);

    if (isBrowserReview) {
        // Front and back are separate template renders (separate script executions), so the typed
        // answer is handed off between them via localStorage, keyed by the note's stable
        // _system_note_uuid (a card id would also work but changes per review; the note uuid doesn't).
        const STORAGE_PREFIX = "typingAnswer:";

        function storageKey(uuid) {
            return STORAGE_PREFIX + uuid;
        }

        // Selector-based lookup is the primary path; text match is a fallback for when AnkiWeb
        // changes its button classes (the label itself is far less likely to change).
        function findShowAnswerButton() {
            const bySelector = document.querySelector("#ansarea button.btn.btn-primary.btn-lg:not(.m-1)");
            if (bySelector) {
                return bySelector;
            }

            const byText = Array.from(document.querySelectorAll("#ansarea button")).find(button => {
                return button.textContent.trim().toLowerCase() === "show answer";
            });
            console.log("typing-answer: show-answer button found via text fallback =", !!byText);
            return byText || null;
        }

        const frontContent = document.querySelector(".typing-front-content");
        const backContent = document.querySelector(".typing-back-content");

        if (frontContent) {
            console.log("typing-answer: front detected");

            const uuid = frontContent.dataset.noteUuid;
            const bodyTyping = frontContent.querySelector(".body-typing");

            console.log("typing-answer: front uuid =", uuid, "bodyTyping found =", !!bodyTyping);

            if (uuid && bodyTyping) {
                const input = document.createElement("input");
                input.type = "text";
                input.className = "typing-answer-input";
                input.autocomplete = "off";
                input.autocapitalize = "off";
                input.spellcheck = false;
                bodyTyping.appendChild(input);
                input.focus();
                console.log("typing-answer: input injected into .body-typing");

                function saveAnswer() {
                    localStorage.setItem(storageKey(uuid), input.value);
                    console.log("typing-answer: saved answer for", uuid, "->", JSON.stringify(input.value));
                }

                input.addEventListener("input", saveAnswer);

                const showAnswerButton = findShowAnswerButton();
                console.log("typing-answer: show-answer button found =", !!showAnswerButton);
                if (showAnswerButton) {
                    showAnswerButton.addEventListener("click", saveAnswer);
                }
            } else {
                console.log("typing-answer: front skipped (missing uuid or .body-typing)");
            }
        }

        function escapeHtml(str) {
            return str
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;");
        }

        function isLetterOrDigit(ch) {
            return /[a-z0-9]/i.test(ch);
        }

        function span(ch, cls) {
            return '<span class="diff-char ' + cls + '">' + escapeHtml(ch) + "</span>";
        }

        // Same block-matching approach as Python's difflib.SequenceMatcher / Anki's own type-answer
        // diff: recursively find the longest common contiguous run, then recurse on what's left on
        // either side. This is what produces things like "od-na" in "gsod-na-uredly" matching "good-
        // naturedly" as one run, rather than a naive char-by-char longest-common-subsequence.
        function findLongestMatch(a, b, aLo, aHi, bLo, bHi) {
            let bestI = aLo;
            let bestJ = bLo;
            let bestSize = 0;
            let runsEndingAt = {};

            for (let i = aLo; i < aHi; i++) {
                const newRuns = {};
                const ch = a[i].toLowerCase();
                for (let j = bLo; j < bHi; j++) {
                    if (b[j].toLowerCase() === ch) {
                        const runLen = (runsEndingAt[j - 1] || 0) + 1;
                        newRuns[j] = runLen;
                        if (runLen > bestSize) {
                            bestI = i - runLen + 1;
                            bestJ = j - runLen + 1;
                            bestSize = runLen;
                        }
                    }
                }
                runsEndingAt = newRuns;
            }

            return { aStart: bestI, bStart: bestJ, size: bestSize };
        }

        function getMatchingBlocks(a, b) {
            const blocks = [];
            const queue = [[0, a.length, 0, b.length]];

            while (queue.length > 0) {
                const [aLo, aHi, bLo, bHi] = queue.pop();
                const match = findLongestMatch(a, b, aLo, aHi, bLo, bHi);

                if (match.size > 0) {
                    blocks.push(match);
                    if (aLo < match.aStart && bLo < match.bStart) {
                        queue.push([aLo, match.aStart, bLo, match.bStart]);
                    }
                    if (match.aStart + match.size < aHi && match.bStart + match.size < bHi) {
                        queue.push([match.aStart + match.size, aHi, match.bStart + match.size, bHi]);
                    }
                }
            }

            blocks.sort((x, y) => x.aStart - y.aStart);
            return blocks;
        }

        // Walks the matching blocks and the gaps between them, turning them into
        // equal/delete/insert/replace regions - same vocabulary as difflib's get_opcodes().
        function getOpcodes(a, b) {
            const blocks = getMatchingBlocks(a, b);
            const opcodes = [];
            let aPos = 0;
            let bPos = 0;

            function pushGap(aEnd, bEnd) {
                const aGapLen = aEnd - aPos;
                const bGapLen = bEnd - bPos;
                if (aGapLen > 0 && bGapLen > 0) {
                    opcodes.push({ type: "replace", aStart: aPos, aEnd, bStart: bPos, bEnd });
                } else if (aGapLen > 0) {
                    opcodes.push({ type: "delete", aStart: aPos, aEnd, bStart: bPos, bEnd: bPos });
                } else if (bGapLen > 0) {
                    opcodes.push({ type: "insert", aStart: aPos, aEnd: aPos, bStart: bPos, bEnd });
                }
            }

            for (const block of blocks) {
                pushGap(block.aStart, block.bStart);
                if (block.size > 0) {
                    opcodes.push({
                        type: "equal",
                        aStart: block.aStart,
                        aEnd: block.aStart + block.size,
                        bStart: block.bStart,
                        bEnd: block.bStart + block.size,
                    });
                }
                aPos = block.aStart + block.size;
                bPos = block.bStart + block.size;
            }
            pushGap(a.length, b.length);

            return opcodes;
        }

        // Renders the two diff lines from the opcodes. Matched runs are green on both sides.
        // Typed-only chars (delete/replace) are red, unless they're punctuation (e.g. a stray "-")
        // which reads as noise rather than a real mistake, so it's shown neutral gray instead.
        // Correct-only chars (insert/replace) are always gray "you needed this"; the typed line
        // gets a dash placeholder of the same length so both lines stay easy to scan side by side.
        function buildDiffLines(typed, correct) {
            const aChars = Array.from(typed);
            const bChars = Array.from(correct);
            const opcodes = getOpcodes(aChars, bChars);

            let typedHtml = "";
            let correctHtml = "";

            for (const op of opcodes) {
                if (op.type === "equal") {
                    for (let i = op.aStart; i < op.aEnd; i++) {
                        typedHtml += span(aChars[i], "diff-match");
                    }
                    for (let j = op.bStart; j < op.bEnd; j++) {
                        correctHtml += span(bChars[j], "diff-match");
                    }
                } else if (op.type === "delete") {
                    for (let i = op.aStart; i < op.aEnd; i++) {
                        typedHtml += span(aChars[i], isLetterOrDigit(aChars[i]) ? "diff-wrong" : "diff-missing");
                    }
                } else if (op.type === "insert") {
                    // Nothing was typed for this stretch at all - fill the typed line with dash
                    // placeholders so both lines stay the same number of "columns" to scan.
                    for (let j = op.bStart; j < op.bEnd; j++) {
                        correctHtml += span(bChars[j], "diff-missing");
                        typedHtml += span("-", "diff-missing");
                    }
                } else if (op.type === "replace") {
                    // Something *was* typed here, just not the right thing - show it as-is rather
                    // than padding with placeholders.
                    for (let i = op.aStart; i < op.aEnd; i++) {
                        typedHtml += span(aChars[i], isLetterOrDigit(aChars[i]) ? "diff-wrong" : "diff-missing");
                    }
                    for (let j = op.bStart; j < op.bEnd; j++) {
                        correctHtml += span(bChars[j], "diff-missing");
                    }
                }
            }

            return { typedHtml, correctHtml };
        }

        if (backContent) {
            console.log("typing-answer: back detected");

            const uuid = backContent.dataset.noteUuid;
            const bodyTyping = backContent.querySelector(".body-typing");
            const checkBlock = backContent.querySelector(".typing-answer-check");
            const typedLine = backContent.querySelector(".typing-diff-typed");
            const arrowNode = backContent.querySelector(".typing-diff-arrow");
            const correctLine = backContent.querySelector(".typing-diff-correct");

            console.log(
                "typing-answer: back uuid =", uuid,
                "bodyTyping found =", !!bodyTyping,
                "checkBlock found =", !!checkBlock,
                "typedLine found =", !!typedLine,
                "arrowNode found =", !!arrowNode,
                "correctLine found =", !!correctLine
            );

            if (uuid && bodyTyping && checkBlock && typedLine && arrowNode && correctLine) {
                const correctWord = bodyTyping.textContent.trim();

                // .body-typing is Anki's own render of {{type:word}}, which on a browser just
                // shows the plain correct word - .typing-answer-check replaces that role entirely,
                // so keeping both around would show the word twice.
                bodyTyping.style.display = "none";

                const savedAnswer = localStorage.getItem(storageKey(uuid));
                const typedAnswer = savedAnswer ? savedAnswer.trim() : "";

                console.log("typing-answer: correctWord =", JSON.stringify(correctWord), "typedAnswer =", JSON.stringify(typedAnswer));

                const isCorrect = typedAnswer.length > 0 && typedAnswer.toLowerCase() === correctWord.toLowerCase();
                console.log("typing-answer: isCorrect =", isCorrect);

                if (typedAnswer.length === 0) {
                    typedLine.innerHTML = span("(no answer)", "diff-wrong");
                    arrowNode.style.display = "none";
                    correctLine.style.display = "none";
                } else if (isCorrect) {
                    typedLine.innerHTML = Array.from(typedAnswer)
                        .map(ch => span(ch, "diff-match"))
                        .join("");
                    arrowNode.style.display = "none";
                    correctLine.style.display = "none";
                } else {
                    const { typedHtml, correctHtml } = buildDiffLines(typedAnswer, correctWord);
                    typedLine.innerHTML = typedHtml;
                    correctLine.innerHTML = correctHtml;
                    arrowNode.style.display = "";
                    correctLine.style.display = "";
                }

                checkBlock.classList.add(isCorrect ? "typing-answer-correct" : "typing-answer-incorrect");
                checkBlock.style.display = "block";

                // One-shot: don't let a stale answer leak into the next time this note is reviewed.
                localStorage.removeItem(storageKey(uuid));
            } else {
                console.log("typing-answer: back skipped (missing uuid or expected elements)");
            }
        }
    }
}
