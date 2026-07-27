import type { EmployeeProfile } from '../types/employee'

type EmployeeCardProps = {
  employee: EmployeeProfile
}

function EmployeeCard({ employee }: EmployeeCardProps) {
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
          <dt>Meeting attendance</dt>
          <dd>{employee.meetingAttendancePercent}%</dd>
        </div>
        <div>
          <dt>Tasks completed</dt>
          <dd>{employee.tasksCompleted}</dd>
        </div>
        <div>
          <dt>Collaboration</dt>
          <dd>{employee.collaborationScore}/100</dd>
        </div>
      </dl>

      <p>{employee.summary}</p>
    </article>
  )
}

export default EmployeeCard