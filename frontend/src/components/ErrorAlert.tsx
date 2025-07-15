import { AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from './ui/alert'
import { Button } from './ui/button'

interface ErrorAlertProps {
  title?: string
  message: string
  onRetry?: () => void
  className?: string
}

export function ErrorAlert({ 
  title = 'Error', 
  message, 
  onRetry,
  className 
}: ErrorAlertProps) {
  return (
    <Alert variant="destructive" className={className}>
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription className="mt-2">
        <p>{message}</p>
        {onRetry && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={onRetry}
            className="mt-3"
          >
            Try Again
          </Button>
        )}
      </AlertDescription>
    </Alert>
  )
}