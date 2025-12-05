import { useState, useRef } from 'react'
import { chatApi } from '../services/api'

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [history, setHistory] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const append = (lines: string[]) => setHistory((h) => [...h, ...lines])

  const sendMessage = async () => {
    if (!message) return
    setLoading(true)
    try {
      const res = await chatApi.message(message)
      append([`You: ${message}`, `Co-Pilot: ${res.data.response}`])
    } catch (e: any) {
      append([`You: ${message}`, `Error: ${e?.message || 'Failed to send'}`])
    } finally {
      setMessage('')
      setLoading(false)
    }
  }

  const sendStream = async () => {
    if (!message) return
    const controller = new AbortController()
    abortRef.current = controller
    setStreaming(true)
    append([`You: ${message}`, 'Co-Pilot (streaming)...'])
    try {
      const res = await chatApi.stream(message, undefined)
      if (!res.body) throw new Error('No stream body')
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() || ''
        for (const part of parts) {
          const line = part.trim()
          if (!line.startsWith('data:')) continue
          const payload = JSON.parse(line.replace('data:', '').trim())
          if (payload.chunk) {
            append([`Co-Pilot: ${payload.chunk}`])
          }
        }
      }
    } catch (e: any) {
      append([`Error: ${e?.message || 'Stream failed'}`])
    } finally {
      setMessage('')
      setStreaming(false)
    }
  }

  const send = () => {
    if (streaming || loading) return
    sendMessage()
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
              disabled={loading || streaming}
            />
            <button
              className="bg-blue-600 text-white text-sm px-3 py-1 rounded disabled:opacity-50"
              onClick={send}
              disabled={loading || streaming}
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Streaming uses /chat/stream</span>
            <button
              className="text-blue-600 disabled:opacity-50"
              onClick={sendStream}
              disabled={streaming || loading}
            >
              {streaming ? 'Streaming...' : 'Stream'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
