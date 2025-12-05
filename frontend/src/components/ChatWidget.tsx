import { useState } from 'react'

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [history, setHistory] = useState<string[]>([])

  const send = () => {
    if (!message) return
    setHistory((h) => [...h, `You: ${message}`, 'Co-Pilot: (response placeholder)'])
    setMessage('')
  }

  return (
    <div className="fixed bottom-4 right-4 w-72 bg-white shadow-lg rounded-lg border">
      <div className="p-3 border-b flex justify-between items-center">
        <div className="font-semibold text-sm">Co-Pilot</div>
        <button className="text-blue-600 text-sm" onClick={() => setOpen(!open)}>
          {open ? 'Hide' : 'Open'}
        </button>
      </div>
      {open && (
        <div className="p-3 space-y-3">
          <div className="h-40 overflow-y-auto text-xs text-gray-700 space-y-1">
            {history.map((h, idx) => (
              <div key={idx}>{h}</div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              className="border rounded px-2 py-1 text-sm flex-1"
              placeholder="Ask a question"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
            <button className="bg-blue-600 text-white text-sm px-3 py-1 rounded" onClick={send}>
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
