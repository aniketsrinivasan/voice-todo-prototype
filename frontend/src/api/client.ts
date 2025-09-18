import type { AskResponse, Task, TaskCreate } from './types';

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(text || `${res.status}`);
  }
  return res.json();
}

export const TasksApi = {
  list: (params: Record<string, string | undefined>) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (typeof v === 'string' && v.length > 0) q.append(k, v);
    }
    return api<{ tasks: Task[] }>(`/list_tasks?${q.toString()}`);
  },
  addJson: (body: TaskCreate) => api<{ task: Task }>(`/add_task`, { method: 'POST', body: JSON.stringify(body) }),
  addAudio: async (file: File) => {
    const form = new FormData();
    form.append('audio', file);
    const res = await fetch(`${API_BASE}/add_task`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`${res.status}`);
    return res.json() as Promise<{ task: Task }>;
  },
  complete: (payload: { id?: string; title?: string }) => api<{ updated: number }>(`/complete`, { method: 'POST', body: JSON.stringify(payload) }),
  ask: (question: string) => api<AskResponse>(`/ask`, { method: 'POST', body: JSON.stringify({ question }) }),
};

