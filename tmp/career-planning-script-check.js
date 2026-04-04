
        const titleEl = document.getElementById("page-title");
        const themeEl = document.getElementById("page-theme");
        const timeEl = document.getElementById("page-time");
        const countEl = document.getElementById("page-count");
        const roundsEl = document.getElementById("page-rounds");
        const reportEl = document.getElementById("report-body");
        const streamEl = document.getElementById("chat-stream");
        const resultSourceEl = document.getElementById("result-source");
        const dialogueSourceEl = document.getElementById("dialogue-source");

        async function loadText(path, embeddedEl, validator) {
            const embedded = embeddedEl.textContent.trim();

            try {
                const response = await fetch(path, { cache: "no-store" });
                if (response.ok) {
                    const text = await response.text();
                    if (!validator || validator(text)) {
                        return text;
                    }
                }
            } catch (error) {
                // 直接打开 file:// 时通常会走到这里，继续使用内嵌文本即可。
            }

            return embedded;
        }

        async function loadResultMarkdown() {
            return loadText(
                "./career-planning-result.md",
                resultSourceEl,
                (text) => text.includes("# 大学四年规划咨询报告")
            );
        }

        async function loadDialogueMarkdown() {
            return loadText(
                "./career-planning-dialogue.md",
                dialogueSourceEl,
                (text) => text.includes("**用户**") && text.includes("**AI顾问**")
            );
        }

        function extractMeta(markdown) {
            const title = markdown.match(/^#\s+(.+)$/m)?.[1]?.trim() || "职业规划对话实录";
            const time = markdown.match(/\*\*时间\*\*：(.+)/)?.[1]?.trim() || "未标注";
            const theme = markdown.match(/\*\*主题\*\*：(.+)/)?.[1]?.trim() || "从 Markdown 实录生成的聊天记录页。";

            return { title, time, theme };
        }

        function parseMessages(markdown) {
            const normalized = markdown.replace(/\r\n/g, "\n");
            const regex = /^\*\*(用户|AI顾问)\*\*：\s*([\s\S]*?)(?=^\*\*(?:用户|AI顾问)\*\*：|$)/gm;
            const messages = [];

            let match;
            while ((match = regex.exec(normalized)) !== null) {
                const role = match[1];
                const content = match[2]
                    .replace(/^\s*---\s*$/gm, "")
                    .trim();

                if (content) {
                    messages.push({ role, content });
                }
            }

            return messages;
        }

        function escapeHtml(text) {
            return text
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#39;");
        }

        function applyInlineMarkup(text) {
            let value = escapeHtml(text);
            const stash = [];

            value = value.replace(/`([^`]+)`/g, (_, code) => {
                const token = `__CODE_${stash.length}__`;
                stash.push(`<code>${escapeHtml(code)}</code>`);
                return token;
            });

            value = value.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noreferrer noopener">$1</a>');
            value = value.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
            value = value.replace(/(^|[^*])\*(?!\s)(.+?)(?<!\s)\*(?!\*)/g, "$1<em>$2</em>");

            stash.forEach((item, index) => {
                value = value.replace(`__CODE_${index}__`, item);
            });

            return value;
        }

        function splitBlocks(text) {
            const lines = text.split("\n");
            const blocks = [];
            let current = [];

            for (const line of lines) {
                if (!line.trim()) {
                    if (current.length) {
                        blocks.push(current);
                        current = [];
                    }
                    continue;
                }
                current.push(line);
            }

            if (current.length) {
                blocks.push(current);
            }

            return blocks;
        }

        function isTableBlock(block) {
            return block.length >= 2 && block.every((line) => /^\|.*\|$/.test(line.trim()));
        }

        function isListBlock(block) {
            return block.every((line) => /^(\s*)([-*]|\d+\.)\s+/.test(line));
        }

        function parseTableRow(line) {
            return line
                .trim()
                .replace(/^\|/, "")
                .replace(/\|$/, "")
                .split("|")
                .map((cell) => cell.trim());
        }

        function renderTable(block) {
            const rows = block.map(parseTableRow);
            const hasDivider = block[1] && /^[\s|:\-]+$/.test(block[1].trim());
            const header = rows[0] || [];
            const bodyRows = hasDivider ? rows.slice(2) : rows.slice(1);

            const thead = `<thead><tr>${header.map((cell) => `<th>${applyInlineMarkup(cell)}</th>`).join("")}</tr></thead>`;
            const tbody = `<tbody>${bodyRows.map((row) => `<tr>${row.map((cell) => `<td>${applyInlineMarkup(cell)}</td>`).join("")}</tr>`).join("")}</tbody>`;

            return `<div class="table-wrap"><table>${thead}${tbody}</table></div>`;
        }

        function renderList(block) {
            const ordered = /^\s*\d+\.\s+/.test(block[0]);
            const tag = ordered ? "ol" : "ul";
            const items = block.map((line) => {
                const text = ordered
                    ? line.replace(/^\s*\d+\.\s+/, "")
                    : line.replace(/^\s*[-*]\s+/, "");

                return `<li>${applyInlineMarkup(text)}</li>`;
            }).join("");

            return `<${tag}>${items}</${tag}>`;
        }
    

        function renderHeading(block) {
            const first = block[0].trim();
            const level = Math.min(6, Math.max(3, first.match(/^#+/)[0].length + 2));
            const text = first.replace(/^#+\s*/, "");
            return `<h${level}>${applyInlineMarkup(text)}</h${level}>`;
        }

        function renderQuote(block) {
            const content = block.map((line) => applyInlineMarkup(line.replace(/^\s*>\s?/, ""))).join("<br>");
            return `<blockquote>${content}</blockquote>`;
        }

        function renderParagraph(block) {
            return `<p>${block.map((line) => applyInlineMarkup(line)).join("<br>")}</p>`;
        }

        function renderMarkdown(text) {
            return splitBlocks(text)
                .map((block) => {
                    const first = block[0].trim();

                    if (!first || first === "---") {
                        return "";
                    }

                    if (/^#{1,6}\s/.test(first)) {
                        return renderHeading(block);
                    }

                    if (isTableBlock(block)) {
                        return renderTable(block);
                    }

                    if (isListBlock(block)) {
                        return renderList(block);
                    }

                    if (block.every((line) => /^\s*>\s?/.test(line))) {
                        return renderQuote(block);
                    }

                    return renderParagraph(block);
                })
                .join("");
        }

        function renderReport(markdown) {
            reportEl.innerHTML = renderMarkdown(markdown);
        }

        function explodeMessages(messages) {
            const exploded = [];

            messages.forEach((message, index) => {
                const blocks = splitBlocks(message.content).filter((block) => {
                    const first = block[0]?.trim();
                    return first && first !== "---";
                });

                if (!blocks.length) {
                    return;
                }

                blocks.forEach((block, blockIndex) => {
                    exploded.push({
                        role: message.role,
                        content: block.join("\n"),
                        turn: Math.floor(index / 2) + 1,
                        part: blockIndex + 1,
                        totalParts: blocks.length
                    });
                });
            });

            return exploded;
        }

        function renderMessages(messages) {
            streamEl.innerHTML = "";

            messages.forEach((message, index) => {
                const article = document.createElement("article");
                const isUser = message.role === "用户";
                article.className = `message ${isUser ? "is-user" : "is-ai"}`;
                article.style.transitionDelay = `${Math.min(index * 35, 260)}ms`;
                const turnLabel = message.totalParts > 1
                    ? `第 ${String(message.turn).padStart(2, "0")} 轮 · ${message.part}/${message.totalParts}`
                    : `第 ${String(message.turn).padStart(2, "0")} 轮`;

                article.innerHTML = `
                    <div class="avatar">${isUser ? "USER" : "AI"}</div>
                    <div class="bubble-wrap">
                        <div class="speaker-row">
                            <span class="speaker-name">${message.role}</span>
                            <span class="turn-tag">${turnLabel}</span>
                        </div>
                        <section class="bubble">
                            <div class="content">${renderMarkdown(message.content)}</div>
                        </section>
                    </div>
                `;

                streamEl.appendChild(article);
            });
        }

        function revealOnScroll() {
            const cards = [...document.querySelectorAll(".message")];

            if (!("IntersectionObserver" in window)) {
                cards.forEach((card) => card.classList.add("revealed"));
                return;
            }

            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("revealed");
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.14,
                rootMargin: "0px 0px -20px 0px"
            });

            cards.forEach((card) => observer.observe(card));
        }

        async function init() {
            const [resultMarkdown, dialogueMarkdown] = await Promise.all([
                loadResultMarkdown(),
                loadDialogueMarkdown()
            ]);

            const meta = extractMeta(dialogueMarkdown);
            const messages = parseMessages(dialogueMarkdown);
            const segments = explodeMessages(messages);
            const rounds = Math.ceil(messages.length / 2);

            document.title = "大学规划报告 + 对话实录";
            titleEl.textContent = "大学规划报告 + 对话实录";
            themeEl.textContent = "报告区根据 career-planning-result.md 重建，对话区根据 career-planning-dialogue.md 渲染，尽量恢复成“原内容在前，对话补充在后”的结构。";
            timeEl.textContent = meta.time;
            countEl.textContent = `${segments.length} 段`;
            roundsEl.textContent = `${rounds} 轮问答`;

            renderReport(resultMarkdown);
            renderMessages(segments);
            revealOnScroll();
        }

        document.addEventListener("DOMContentLoaded", init);
    
