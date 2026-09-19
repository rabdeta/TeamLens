import type { DataSource } from '../types/dataSource'

type DataSourceCardProps = {
  source: DataSource
  onConnect: (provider: string) => void
  onSync: () => void
  isSyncing: boolean
}

function DataSourceCard({
  source,
  onConnect,
  onSync,
  isSyncing,
}: DataSourceCardProps) {
  const statusLabel = source.status.replace('_', ' ')
  const isLinear = source.provider === 'linear'
  const isConnected = source.status === 'connected'
  const canConnect = isLinear && !isConnected
  const canSync = isLinear && isConnected

  let buttonLabel = 'Coming soon'

  if (canSync) {
    buttonLabel = isSyncing ? 'Syncing…' : 'Sync now'
  } else if (canConnect) {
    buttonLabel = 'Connect'
  } else if (isConnected) {
    buttonLabel = 'Connected'
  }

  const handleClick = () => {
    if (canSync) {
      onSync()
    } else if (canConnect) {
      onConnect(source.provider)
    }
  }

  return (
    <article className="data-source-card">
      <div>
        <h3>{source.displayName}</h3>
        <p className={`source-status source-status--${source.status}`}>
          {statusLabel}
        </p>
      </div>

      <button
        type="button"
        disabled={(!canConnect && !canSync) || isSyncing}
        onClick={handleClick}
      >
        {buttonLabel}
      </button>
    </article>
  )
}

export default DataSourceCard