import type { DataSource } from '../types/dataSource'

type DataSourceCardProps = {
  source: DataSource
  onConnect: (provider: string) => void
}

function DataSourceCard({
  source,
  onConnect,
}: DataSourceCardProps) {
  const statusLabel = source.status.replace('_', ' ')
  const isConnected = source.status === 'connected'
  const canConnect = source.provider === 'linear' && !isConnected

  let buttonLabel = 'Coming soon'

  if (isConnected) {
    buttonLabel = 'Connected'
  } else if (canConnect) {
    buttonLabel = 'Connect'
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
        disabled={!canConnect}
        onClick={() => onConnect(source.provider)}
      >
        {buttonLabel}
      </button>
    </article>
  )
}

export default DataSourceCard