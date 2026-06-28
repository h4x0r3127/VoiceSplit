'use client'

import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
  FileAudio, X, RefreshCw, CheckCircle, XCircle,
  Loader2, Ban, ExternalLink,
} from 'lucide-react'
import { useUploadQueue, type QueueItem } from '@/hooks/useUploadQueue'
import { formatBytes } from '@/lib/utils'
import { cn } from '@/lib/utils'

const STATUS_CONFIG = {
  pending:   { label: 'Queued',     color: 'text-muted',        icon: FileAudio },
  uploading: { label: 'Uploading',  color: 'text-brand-cyan',   icon: Loader2 },
  uploaded:  { label: 'Uploaded',   color: 'text-success',      icon: CheckCircle },
  error:     { label: 'Failed',     color: 'text-danger',       icon: XCircle },
  cancelled: { label: 'Cancelled',  color: 'text-muted',        icon: Ban },
}

function QueueItemRow({
  item,
  onCancel,
  onRemove,
  onRetry,
}: {
  item: QueueItem
  onCancel: (id: string) => void
  onRemove: (id: string) => void
  onRetry: (id: string) => void
}) {
  const cfg = STATUS_CONFIG[item.status]
  const Icon = cfg.icon

  return (
    <motion.div
      layout
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="flex items-center gap-3 py-3 px-4 border-b border-brand-cyan/10 last:border-0">
        {/* Icon */}
        <div className="w-8 h-8 rounded-lg bg-brand-cyan/10 flex items-center justify-center flex-shrink-0">
          <Icon
            className={cn(
              'w-4 h-4',
              cfg.color,
              item.status === 'uploading' && 'animate-spin',
            )}
          />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium text-white truncate">{item.file.name}</p>
            <span className={cn('text-xs font-medium flex-shrink-0', cfg.color)}>
              {cfg.label}
            </span>
          </div>

          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-muted">{formatBytes(item.file.size)}</span>
            {item.status === 'uploading' && (
              <span className="text-xs text-brand-cyan tabular-nums">{item.progress}%</span>
            )}
          </div>

          {/* Progress bar */}
          {item.status === 'uploading' && (
            <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-brand-cyan to-brand-blue rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${item.progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          )}

          {/* Error */}
          {item.status === 'error' && item.error && (
            <p className="text-xs text-danger mt-1 truncate">{item.error}</p>
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {item.status === 'uploaded' && item.jobId && (
            <Link href={`/processing/${item.jobId}`}>
              <button
                title="View processing status"
                className="w-7 h-7 rounded-lg glass flex items-center justify-center text-muted hover:text-brand-cyan transition-colors"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </Link>
          )}
          {item.status === 'error' && (
            <button
              onClick={() => onRetry(item.id)}
              title="Retry upload"
              className="w-7 h-7 rounded-lg glass flex items-center justify-center text-muted hover:text-brand-cyan transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          )}
          {item.status === 'uploading' && (
            <button
              onClick={() => onCancel(item.id)}
              title="Cancel upload"
              className="w-7 h-7 rounded-lg glass flex items-center justify-center text-muted hover:text-danger transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
          {(item.status === 'uploaded' || item.status === 'error' || item.status === 'cancelled') && (
            <button
              onClick={() => onRemove(item.id)}
              title="Remove from queue"
              className="w-7 h-7 rounded-lg glass flex items-center justify-center text-muted hover:text-danger transition-colors"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </motion.div>
  )
}

interface UploadQueueProps {
  className?: string
}

export function UploadQueue({ className }: UploadQueueProps) {
  const { items, retry, cancelItem, removeItem, clearCompleted } = useUploadQueue()

  if (items.length === 0) return null

  const completedCount = items.filter(
    (i) => i.status === 'uploaded' || i.status === 'cancelled',
  ).length

  return (
    <div className={cn('glass rounded-2xl border border-brand-cyan/10 overflow-hidden', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-brand-cyan/10">
        <h3 className="text-sm font-semibold text-white">
          Upload queue{' '}
          <span className="text-muted font-normal">({items.length})</span>
        </h3>
        {completedCount > 0 && (
          <button
            onClick={clearCompleted}
            className="text-xs text-muted hover:text-brand-cyan transition-colors"
          >
            Clear completed
          </button>
        )}
      </div>

      {/* Items */}
      <div>
        <AnimatePresence initial={false}>
          {items.map((item) => (
            <QueueItemRow
              key={item.id}
              item={item}
              onCancel={cancelItem}
              onRemove={removeItem}
              onRetry={retry}
            />
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}
