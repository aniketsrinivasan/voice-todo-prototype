import { useId } from 'react'

export interface TaskFilters {
  status?: 'todo' | 'done';
  due?: 'today' | 'week' | 'overdue';
  q?: string;
  category?: string;
}

export function FiltersBar({ value, onChange }: { value: TaskFilters; onChange: (v: TaskFilters) => void }) {
  const statusId = useId();
  const dueId = useId();
  const qId = useId();
  const catId = useId();

  return (
    <form className="filters" onSubmit={(e) => e.preventDefault()}>
      <label htmlFor={statusId}>Status</label>
      <select
        id={statusId}
        value={value.status ?? ''}
        onChange={(e) => onChange({ ...value, status: (e.target.value || undefined) as any })}
      >
        <option value="">All</option>
        <option value="todo">Todo</option>
        <option value="done">Done</option>
      </select>

      <label htmlFor={dueId}>Due</label>
      <select
        id={dueId}
        value={value.due ?? ''}
        onChange={(e) => onChange({ ...value, due: (e.target.value || undefined) as any })}
      >
        <option value="">Any</option>
        <option value="today">Today</option>
        <option value="week">This week</option>
        <option value="overdue">Overdue</option>
      </select>

      <label htmlFor={qId}>Search</label>
      <input
        id={qId}
        type="search"
        placeholder="Find tasks"
        value={value.q ?? ''}
        onChange={(e) => onChange({ ...value, q: e.target.value || undefined })}
      />

      <label htmlFor={catId}>Category</label>
      <input
        id={catId}
        type="text"
        placeholder="Category"
        value={value.category ?? ''}
        onChange={(e) => onChange({ ...value, category: e.target.value || undefined })}
      />
    </form>
  )
}

