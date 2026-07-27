import './App.css'
import EmployeeCard from './components/EmployeeCard'
import { mockEmployees } from './data/mockEmployees'

function App() {
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

        <div className="employee-grid">
          {mockEmployees.map((employee) => (
            <EmployeeCard key={employee.id} employee={employee} />
          ))}
        </div>
      </section>
    </main>
  )
}

export default App