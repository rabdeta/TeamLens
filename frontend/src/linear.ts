export type LinearMemberMetric = {
  id: string
  name: string
  active: boolean
  tasksCompleted: number
  measurementPeriodDays: number
}

export type LinearMetricsResponse = {
  members: LinearMemberMetric[]
  count: number
}