export type Priority = 'low' | 'med' | 'high';

export interface Task {
  id: string;
  title: string;
  description?: string | null;
  category?: string | null;
  priority: Priority;
  due_date?: string | null;
  completed: boolean;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  category?: string | null;
  priority?: Priority;
  due_date?: string | null;
}

export interface AskResponse {
  answer: string;
  tasks?: Task[];
}

