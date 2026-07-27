import { useEffect, useState } from 'react'
import './App.css'
import EmployeeCard from './components/EmployeeCard'
import type { EmployeeProfile } from './types/employee'

function App() {
  const [employees, setEmployees] = useState<EmployeeProfile[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadEmployees = async () => {
      try {
        const response = await fetch('/api/employees')

        if (!response.ok) {
          throw new Error('Failed to load employee profiles')
        }

        const data: EmployeeProfile[] = await response.json()
        setEmployees(data)
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : 'An unexpected error occurred',
        )
      } finally {
        setIsLoading(false)
      }
    }

    loadEmployees()
  }, [])

  const filteredEmployees = employees.filter((employee) => {
    const searchableText =
      `${employee.name} ${employee.role} ${employee.department}`.toLowerCase()

    return searchableText.includes(searchTerm.toLowerCase())
  })

  return (
    <main>
      <header>
        <p>Employee Intelligence Platform</p>
        <h1>Workplace insights without reading employee messages</h1>
        <p>
          Generate privacy-conscious employee profiles from collaboration
          metadata.
        </p>
      </header>

      <section>
        <div className="section-heading">
          <div>
            <h2>Employee profiles</h2>
            <p>Profile data supplied by the Flask API.</p>
          </div>
          <button type="button">Add data source</button>
        </div>

        <label className="search">
          <span>Search employees</span>
          <input
            type="search"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Name, role, or department"
          />
        </label>

        {isLoading && <p>Loading employee profiles…</p>}
        {error && <p role="alert">{error}</p>}

        {!isLoading && !error && (
          <>
            <p className="result-count">
              Showing {filteredEmployees.length} of {employees.length} employees
            </p>

            <div className="employee-grid">
              {filteredEmployees.map((employee) => (
                <EmployeeCard key={employee.id} employee={employee} />
              ))}
            </div>
          </>
        )}
      </section>
    </main>
  )
}

export default App