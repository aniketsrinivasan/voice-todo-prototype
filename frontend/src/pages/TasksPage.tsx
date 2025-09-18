import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { TasksApi } from '../api/client'
import { FiltersBar, type TaskFilters } from '../components/FiltersBar'
import { TaskList } from '../components/TaskList'
import { AddTaskForm } from '../components/AddTaskForm'

export default function TasksPage() {
  const [filters, setFilters] = useState<TaskFilters>({ status: 'todo' })
  const qc = useQueryClient()
  const { mutate: complete } = useMutation({
    mutationFn: (id: string) => TasksApi.complete({ id }),
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  return (
    <div className="stack">
      <FiltersBar value={filters} onChange={setFilters} />
      <AddTaskForm />
      <TaskList filters={filters} onComplete={(id) => complete(id)} />
    </div>
  )
}

