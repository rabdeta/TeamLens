export type EmployeeProfile = {
  id: string
  name: string
  role: string
  department: string
  responseTimeMinutes: number
  meetingAttendancePercent: number
  scheduledMeetingCount: number
  acceptedMeetingCount: number
  scheduledMeetingMinutes: number
  meetingAcceptancePercent: number
  tasksCompleted: number
  collaborationScore: number
  summary: string
  measurementPeriodDays: number
  dataCoveragePercent: number
  lastSyncedAt: string
}