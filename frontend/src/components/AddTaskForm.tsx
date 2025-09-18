import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { TasksApi } from '../api/client'
import type { TaskCreate } from '../api/types'

export function AddTaskForm() {
  const qc = useQueryClient()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('')
  const [priority, setPriority] = useState<'low' | 'med' | 'high'>('med')
  const [due, setDue] = useState('')

  const { mutate, isPending } = useMutation({
    mutationFn: (body: TaskCreate) => TasksApi.addJson(body),
    onSuccess: () => {
      setTitle(''); setDescription(''); setCategory(''); setPriority('med'); setDue('')
      qc.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim()) return
    mutate({
      title: title.trim(),
      description: description.trim() || undefined,
      category: category.trim() || undefined,
      priority,
      due_date: due || undefined,
    })
  }

  return (
    <form className="panel form" onSubmit={onSubmit}>
      <div className="row">
        <input placeholder="Task title" value={title} onChange={(e) => setTitle(e.target.value)} required />
      </div>
      <div className="row">
        <input placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
      </div>
      <div className="row">
        <input placeholder="Category" value={category} onChange={(e) => setCategory(e.target.value)} />
        <select value={priority} onChange={(e) => setPriority(e.target.value as any)}>
          <option value="low">Low</option>
          <option value="med">Medium</option>
          <option value="high">High</option>
        </select>
        <input type="date" value={due} onChange={(e) => setDue(e.target.value)} />
      </div>
      <div className="row">
        <button className="btn primary" disabled={isPending}>Add Task</button>
      </div>
    </form>
  )
}

