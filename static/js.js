window.addEventListener(`DOMContentLoaded`, () => {
	const root = []
	const children = {}
	const replies = document.querySelector(`.replies`)

	if (replies == null)
		return

	const frag = document.createDocumentFragment()

	const getId = node => Number(node.getAttribute("post_id"))
	const getParentId = node => Number(node.getAttribute("parent_id"))
	const handleNode = node => {
		frag.appendChild(node)
		const id = getId(node)
		children[id]
			.sort((a, b) => getId(a) - getId(b))
			.forEach(v => handleNode(v))
	}
	
	for (let i = 0; i < replies.children.length; i++) {
		const node = replies.children[i]
		const parent_id = getParentId(node)
		const id = getId(node)
		if (parent_id == 0)
			root.push(node)
		else
			children[parent_id].push(node)

		children[id] = []
	}

	root
		.sort((a, b) => getId(a) - getId(b))
		.forEach(v => handleNode(v))

	replies.appendChild(frag)
})
