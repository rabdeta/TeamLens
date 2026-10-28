import type { EmployeeProfile } from '../types/employee'

type EmployeeCardProps = {
  employee: EmployeeProfile
  onSelect: (employeeId: string) => void
}

function EmployeeCard({ employee, onSelect }: EmployeeCardProps) {
  const lastSynced = new Date(employee.lastSyncedAt).toLocaleString()

  return (
    <article className="employee-card">
      <div>
        <p>{employee.department}</p>
        <h3>{employee.name}</h3>
        <p>{employee.role}</p>
      </div>

      <dl className="metrics">
        <div>
          <dt>Response time</dt>
          <dd>{employee.responseTimeMinutes} min</dd>
        </div>
        <div>
          <dt>Meeting RSVPs</dt>
          <dd>
            {employee.acceptedMeetingCount}/
            {employee.scheduledMeetingCount} accepted (
            {employee.meetingAcceptancePercent}%)
          </dd>
        </div>
        <div>
          <dt>Scheduled meeting time</dt>
          <dd>{employee.scheduledMeetingMinutes} min</dd>
        </div>
      </dl>

      <p>{employee.summary}</p>

      <button
        type="button"
        className="profile-button"
        onClick={() => onSelect(employee.id)}
      >
        View profile
      </button>

      <footer className="data-context">
        <span>Period: {employee.measurementPeriodDays} days</span>
        <span>Coverage: {employee.dataCoveragePercent}%</span>
        <span>Synced: {lastSynced}</span>
      </footer>
    </article>
  )
}

export default EmployeeCard