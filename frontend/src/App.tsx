import { useState } from 'react'
import { ClinicalNoteInput } from './components/ClinicalNoteInput'
import { TreatmentPlanDisplay } from './components/TreatmentPlanDisplay'
import { TreatmentPlanSkeleton } from './components/TreatmentPlanSkeleton'
import { ErrorAlert } from './components/ErrorAlert'
import { apiService, type ProcessResponse } from './lib/api'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<ProcessResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [lastNote, setLastNote] = useState<string>('')

  const handleSubmit = async (note: string) => {
    setIsProcessing(true)
    setResult(null)
    setError(null)
    setLastNote(note)
    
    const response = await apiService.processClinicalnote(note)
    
    if (response.success) {
      setResult(response)
    } else {
      // Determine error type and provide appropriate message
      let errorMessage = response.error || 'Failed to process clinical note.'
      
      if (response.error) {
        if (response.error.includes('fetch')) {
          errorMessage = 'Unable to connect to the server. Please check your internet connection and try again.'
        } else if (response.error.includes('VITE_API')) {
          errorMessage = 'Configuration error. Please contact support.'
        } else if (response.error.includes('status: 401') || response.error.includes('status: 403')) {
          errorMessage = 'Authentication failed. Please check your API key configuration.'
        } else if (response.error.includes('status: 500')) {
          errorMessage = 'Server error. The service may be temporarily unavailable.'
        } else if (response.error.includes('status: 429')) {
          errorMessage = 'Too many requests. Please wait a moment and try again.'
        }
      }
      
      setError(errorMessage)
    }
    
    setIsProcessing(false)
  }

  const handleRetry = () => {
    if (lastNote) {
      handleSubmit(lastNote)
    }
  }

  return (
    <div className="min-h-screen bg-background p-3 sm:p-6 lg:p-8">
      <div className="max-w-5xl mx-auto space-y-4 sm:space-y-6 lg:space-y-8">
        <div className="text-center space-y-2 px-2">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight">
            Heidi Clinical Decision Support
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground max-w-2xl mx-auto">
            Evidence-based treatment recommendations powered by MCP
          </p>
        </div>
        
        <ClinicalNoteInput 
          onSubmit={handleSubmit} 
          isLoading={isProcessing}
        />
        
        {error && (
          <ErrorAlert 
            title="Processing Error"
            message={error}
            onRetry={handleRetry}
          />
        )}
        
        {isProcessing && <TreatmentPlanSkeleton />}
        
        {result && !isProcessing && (
          <TreatmentPlanDisplay data={result} />
        )}
      </div>
    </div>
  )
}

export default App