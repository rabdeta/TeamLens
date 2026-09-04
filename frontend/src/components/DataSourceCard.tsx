import type { DataSource } from '../types/dataSource'

type DataSourceCardProps = {
  source: DataSource
}

function DataSourceCard({ source }: DataSourceCardProps) {
  const statusLabel = source.status.replace('_', ' ')

  return (
    <article className="data-source-card">
      <div>
        <h3>{source.displayName}</h3>
        <p className={`source-status source-status--${source.status}`}>
          {statusLabel}
        </p>
      </div>

      <button type="button" disabled>
        Connect
      </button>
    </article>
  )
}

export default DataSourceCard