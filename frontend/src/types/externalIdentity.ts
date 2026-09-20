export type ExternalIdentity = {
  id: string
  employeeId: string | null
  dataSourceId: string
  externalUserId: string
  displayName: string
  active: boolean
  lastSyncedAt: string
}