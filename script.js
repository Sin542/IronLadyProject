const chat = document.getElementById('chat')
const msg = document.getElementById('msg')
const send = document.getElementById('send')

function addBubble(text, role){
    const div = document.createElement('div')
    div.className = `msg ${role}`
    div.textContent = text
    chat.appendChild(div)
    // Smooth scroll to bottom
    chat.scrollTo({ top: chat.scrollHeight, behavior: 'smooth' })
}

async function ask(){
    const text = msg.value.trim()
    if(!text) return
    addBubble(text, 'user')
    msg.value = ''
    send.disabled = true
    try{
        const r = await fetch('/api/chat', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({message:text})
        })
        const data = await r.json()
        addBubble(data.reply || 'Sorry, something went wrong.', 'bot')
    }catch(e){
        addBubble('Network error. Try again.', 'bot')
    }finally{
        send.disabled = false
        msg.focus()
    }
}

send.addEventListener('click', ask)
msg.addEventListener('keydown', e => { if(e.key==='Enter') ask() })
window.addEventListener('load', () => {
    addBubble('Hi! Ask me about programs, duration, mode, certificates, or mentors.', 'bot')
    msg.focus()
})
