const BLOCK_PLACEHOLDER = '\u0000CODE_BLOCK_'

export function renderMarkdown(input = '') {
  const codeBlocks: string[] = []
  let text = escapeHtml(input)

  text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, (_, lang = '', code = '') => {
    const index = codeBlocks.length
    codeBlocks.push(
      `<pre class="md-code"><code data-lang="${escapeAttribute(lang)}">${code.trim()}</code></pre>`,
    )
    return `${BLOCK_PLACEHOLDER}${index}\u0000`
  })

  const lines = text.split(/\r?\n/)
  const html: string[] = []
  let list: string[] = []
  let paragraph: string[] = []

  const flushParagraph = () => {
    if (!paragraph.length) return
    html.push(`<p>${inline(paragraph.join('<br>'))}</p>`)
    paragraph = []
  }
  const flushList = () => {
    if (!list.length) return
    html.push(`<ul>${list.map((item) => `<li>${inline(item)}</li>`).join('')}</ul>`)
    list = []
  }

  for (const line of lines) {
    if (line.startsWith(BLOCK_PLACEHOLDER)) {
      flushParagraph()
      flushList()
      html.push(line)
      continue
    }

    const heading = /^(#{1,4})\s+(.+)$/.exec(line)
    if (heading) {
      flushParagraph()
      flushList()
      html.push(`<h${heading[1].length}>${inline(heading[2])}</h${heading[1].length}>`)
      continue
    }

    const listItem = /^\s*[-*]\s+(.+)$/.exec(line)
    if (listItem) {
      flushParagraph()
      list.push(listItem[1])
      continue
    }

    const orderedItem = /^\s*\d+\.\s+(.+)$/.exec(line)
    if (orderedItem) {
      flushParagraph()
      list.push(orderedItem[1])
      continue
    }

    if (!line.trim()) {
      flushParagraph()
      flushList()
      continue
    }

    flushList()
    paragraph.push(line)
  }

  flushParagraph()
  flushList()

  return html
    .join('')
    .replace(new RegExp(`${BLOCK_PLACEHOLDER}(\\d+)\\u0000`, 'g'), (_, index) => codeBlocks[Number(index)] || '')
}

function inline(text: string) {
  return text
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label = '', href = '') => link(label, href))
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

function link(label: string, href: string) {
  const normalized = href.trim()
  if (!isSafeHref(normalized)) return label
  return `<a href="${escapeAttributeValue(normalized)}" target="_blank" rel="noopener noreferrer">${label}</a>`
}

function isSafeHref(href: string) {
  return /^(https?:\/\/|mailto:|\/(?!\/)|#)/i.test(href)
}

function escapeHtml(text: string) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

function escapeAttribute(text: string) {
  return text.replace(/[^a-zA-Z0-9_-]/g, '')
}

function escapeAttributeValue(text: string) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}
