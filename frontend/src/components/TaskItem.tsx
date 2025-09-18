import type { Task } from '../api/types'

export function TaskItem({ task, onComplete }: { task: Task; onComplete: (id: string) => void }) {
  return (
    <div className={`task ${task.completed ? 'completed' : ''}`}>
      <div className="task-main">
        <div className="task-title">{task.title}</div>
        {task.description ? <div className="task-desc">{task.description}</div> : null}
        <div className="task-meta">
          {task.category ? <span className="chip">{task.category}</span> : null}
          <span className={`chip ${task.priority}`}>{task.priority}</span>
          {task.due_date ? <span className="chip">Due {new Date(task.due_date).toLocaleDateString()}</span> : null}
        </div>
      </div>
      {!task.completed && (
        <button className="btn" onClick={() => onComplete(task.id)} aria-label={`Complete ${task.title}`}>
          Complete
        </button>
      )}
    </div>
  )
}

