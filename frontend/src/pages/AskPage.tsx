import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { TasksApi } from '../api/client'

export default function AskPage() {
  const [q, setQ] = useState('')
  const { mutate, data, isPending, error } = useMutation({
    mutationFn: (question: string) => TasksApi.ask(question),
  })

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!q.trim()) return
    mutate(q.trim())
  }

  return (
    <div className="stack">
      <form className="panel form" onSubmit={onSubmit}>
        <div className="row">
          <input placeholder="Ask about your tasks" value={q} onChange={(e) => setQ(e.target.value)} />
          <button className="btn primary" disabled={isPending}>Ask</button>
        </div>
      </form>
      {isPending && <div className="panel">Thinking…</div>}
      {error && <div className="panel error">Failed to get answer.</div>}
      {data && (
        <div className="panel">
          <div className="answer">{data.answer}</div>
          {data.tasks && data.tasks.length > 0 && (
            <ul className="related">
              {data.tasks.map((t) => (
                <li key={t.id}>{t.title}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

