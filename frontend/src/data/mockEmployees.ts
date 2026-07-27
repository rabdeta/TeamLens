import type { EmployeeProfile } from '../types/employee'

export const mockEmployees: EmployeeProfile[] = [
  {
    id: 'emp-001',
    name: 'Maya Chen',
    role: 'Software Engineer',
    department: 'Engineering',
    responseTimeMinutes: 42,
    meetingAttendancePercent: 96,
    tasksCompleted: 18,
    collaborationScore: 88,
    summary:
      'Consistent collaborator who completes planned work and participates reliably in team meetings.',
  },
]