import { useQuery } from '@tanstack/react-query'
import { TasksApi } from '../api/client'
import { TaskItem } from './TaskItem'
import type { Task } from '../api/types'
import type { TaskFilters } from './FiltersBar'

export function TaskList({ filters, onComplete }: { filters: TaskFilters; onComplete: (id: string) => void }) {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => TasksApi.list({
      status: filters.status,
      due: filters.due,
      q: filters.q,
      category: filters.category,
    }),
  })

  if (isLoading) return <div className="panel">Loading tasks…</div>
  if (isError) return <div className="panel error">Failed to load tasks.</div>

  const tasks = (data?.tasks ?? []) as Task[]
  if (tasks.length === 0) return <div className="panel">No tasks.</div>

  return (
    <div className="tasklist">
      {tasks.map((t) => (
        <TaskItem key={t.id} task={t} onComplete={onComplete} />
      ))}
    </div>
  )
}

