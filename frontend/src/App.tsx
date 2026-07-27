import { useState } from 'react'
import './App.css'
import EmployeeCard from './components/EmployeeCard'
import { mockEmployees } from './data/mockEmployees'

function App() {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredEmployees = mockEmployees.filter((employee) => {
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
            <p>Demonstration data for the initial frontend.</p>
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

        <p className="result-count">
          Showing {filteredEmployees.length} of {mockEmployees.length} employees
        </p>

        <div className="employee-grid">
          {filteredEmployees.map((employee) => (
            <EmployeeCard key={employee.id} employee={employee} />
          ))}
        </div>
      </section>
    </main>
  )
}

export default App