import { useEffect, useState } from 'react'
import './App.css'
import EmployeeCard from './components/EmployeeCard'
import type { EmployeeProfile } from './types/employee'
import DataSourceCard from './components/DataSourceCard'
import type { DataSource } from './types/dataSource'

function App() {
  const [employees, setEmployees] = useState<EmployeeProfile[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedEmployee, setSelectedEmployee] =
    useState<EmployeeProfile | null>(null)
  const [isDetailLoading, setIsDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [dataSources, setDataSources] = useState<DataSource[]>([])
  const [dataSourcesError, setDataSourcesError] = useState('')

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

  useEffect(() => {
    const loadDataSources = async () => {
      try {
        const response = await fetch('/api/data-sources')

        if (!response.ok) {
          throw new Error('Failed to load data sources')
        }

        const data: DataSource[] = await response.json()
        setDataSources(data)
      } catch (caughtError) {
        setDataSourcesError(
          caughtError instanceof Error
            ? caughtError.message
            : 'An unexpected error occurred',
        )
      }
    }

    loadDataSources()
  }, [])

  const handleSelectEmployee = async (employeeId: string) => {
    setIsDetailLoading(true)
    setDetailError('')
    setSelectedEmployee(null)

    try {
      const response = await fetch(`/api/employees/${employeeId}`)

      if (!response.ok) {
        throw new Error('Failed to load employee details')
      }

      const employee: EmployeeProfile = await response.json()
      setSelectedEmployee(employee)
    } catch (caughtError) {
      setDetailError(
        caughtError instanceof Error
          ? caughtError.message
          : 'An unexpected error occurred',
      )
    } finally {
      setIsDetailLoading(false)
    }
  }

  const handleConnectDataSource = (provider: string) => {
    if (provider === 'linear') {
      window.location.assign(
        'http://127.0.0.1:5000/api/integrations/linear/connect',
      )
    }
  }

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
                <EmployeeCard
                  key={employee.id}
                  employee={employee}
                  onSelect={handleSelectEmployee}
                />
              ))}
            </div>
          </>
        )}
      </section>

      <section className="data-sources-section">
        <div>
          <h2>Data sources</h2>
          <p>Available metadata integrations and their connection status.</p>
        </div>

        {dataSourcesError && <p role="alert">{dataSourcesError}</p>}

        <div className="data-source-grid">
          {dataSources.map((source) => (
            <DataSourceCard
              key={source.id}
              source={source}
              onConnect={handleConnectDataSource}
            />
          ))}
        </div>
      </section>

      {isDetailLoading && <p>Loading employee details…</p>}
      {detailError && <p role="alert">{detailError}</p>}

      {selectedEmployee && (
        <section className="profile-detail">
          <div className="section-heading">
            <div>
              <p>{selectedEmployee.department}</p>
              <h2>{selectedEmployee.name}</h2>
              <p>{selectedEmployee.role}</p>
            </div>
            <button
              type="button"
              onClick={() => setSelectedEmployee(null)}
            >
              Close
            </button>
          </div>

          <p>{selectedEmployee.summary}</p>
          <p>
            These metrics cover {selectedEmployee.measurementPeriodDays} days
            with {selectedEmployee.dataCoveragePercent}% data coverage.
          </p>
        </section>
      )}
    </main>
  )
}

export default App