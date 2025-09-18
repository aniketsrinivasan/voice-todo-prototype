import { Link, NavLink, Route, Routes } from 'react-router-dom'
import './App.css'
import TasksPage from './pages/TasksPage'
import AskPage from './pages/AskPage'

function App() {
  return (
    <div className="container">
      <header className="topbar">
        <Link to="/" className="brand">Voice Todo</Link>
        <nav className="nav">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'navlink active' : 'navlink'}>Tasks</NavLink>
          <NavLink to="/ask" className={({ isActive }) => isActive ? 'navlink active' : 'navlink'}>Ask</NavLink>
        </nav>
      </header>
      <main className="main">
        <Routes>
          <Route path="/" element={<TasksPage />} />
          <Route path="/ask" element={<AskPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
