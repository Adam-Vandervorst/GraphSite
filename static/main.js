const rel = id => document.getElementById(id)
const cels = (...tags) => tags.map(tag => document.createElement(tag))

const chose_view = view => ["content", "date", "related", "labels"]
    .forEach(n => rel(n + "_view").style.display = view == n ? "" : "none")

const construct_button = (name, action, highlight = false) => {
    const [li] = cels("li")
    li.innerText = name
    li.onclick = action
    li.style.color = highlight ? "red" : ""
    return li
}

const to_page_button = page_id => construct_button(pages[page_id].data,
    e => e.stopPropagation() || replace_main(pages[page_id]))

const construct_date_view = date => {
    const [buttons, links] = cels("ul", "ul")
    const dates = Object.values(pages)
        .map(p => p.date)
        .filter((d, i, ds) => ds.indexOf(d) == i)
        .sort()
    buttons.replaceChildren(...dates
        .map(d => construct_button(d, _ => construct_date_view(d), d == date)))
    links.replaceChildren(...Object.keys(pages)
        .filter(jd => date === undefined || pages[jd].date == date)
        .map(jd => to_page_button(jd)))
    rel("date_view").replaceChildren(buttons, links)
    chose_view("date")
}

const construct_link = (name, related) => {
    const [enclosing, from_link, links_to] = cels("li", "p", "ul")
    from_link.innerText = name
    links_to.replaceChildren(...related
        .map(jd => to_page_button(jd)))
    enclosing.replaceChildren(from_link, links_to)
    return enclosing
}

const construct_related_view = () => {
    const [links] = cels("ul")
    links.replaceChildren(...Object.entries(pages)
        .map(([id, {data, related}]) => construct_link(data, related)))
    rel("related_view").replaceChildren(links)
    chose_view("related")
}

const construct_labels_view = label => {
    const [buttons, links] = cels("ul", "ul")
    const labels = Object.values(pages)
        .flatMap(p => p.labels)
        .filter((d, i, ds) => ds.indexOf(d) == i)
        .sort()
    buttons.replaceChildren(...labels
        .map(l => construct_button(l, _ => construct_labels_view(l), l == label)))
    links.replaceChildren(...Object.keys(pages)
        .filter(k => label === undefined || pages[k].labels.includes(label))
        .map(jd => to_page_button(jd)))
    rel("labels_view").replaceChildren(buttons, links)
    chose_view("labels")
}

const populate_page = page => {
    rel("date").innerText = page.date
    rel("date").onclick = e => e.stopPropagation() || construct_date_view(page.date)
    rel("date_area").onclick = _ => construct_date_view()

    rel("related").replaceChildren(...page.related
        .map(jd => to_page_button(jd)))
    rel("related_area").onclick = _ => construct_related_view()

    rel("labels").replaceChildren(...page.labels
        .map(l => construct_button(l, e => e.stopPropagation() || construct_labels_view(l))))
    rel("labels_area").onclick = _ => construct_labels_view()
}

window.onpopstate = e => {
    rel("page").innerHTML = e.state.html
    document.title = e.state.name
    populate_page(e.state)
    chose_view("content")
}

const replace_main = page => fetch(`/pages/${page.data}.html`)
    .then(r => r.text())
    .then(t => {
        rel("page").innerHTML = t
        document.title = page.data
        populate_page(page)
        chose_view("content")
        history.pushState({html: t, ...page}, page.data, "?page=" + page.data)
    })

const params = new URLSearchParams(window.location.search)
const start_id = parseInt(params.get("page")) || 0
fetch("/generated_objects.json")
    .then(r => r.json())
    .then(j => pages = j)
    .then(j => replace_main(j[start_id]))
