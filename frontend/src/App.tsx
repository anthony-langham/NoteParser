import { useState } from 'react'
import { ClinicalNoteInput } from './components/ClinicalNoteInput'
import { TreatmentPlanDisplay } from './components/TreatmentPlanDisplay'
import { apiService, type ProcessResponse } from './lib/api'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<ProcessResponse | null>(null)

  const handleSubmit = async (note: string) => {
    setIsProcessing(true)
    setResult(null)
    
    try {
      const response = await apiService.processClinicalnote(note)
      setResult(response)
    } catch (error) {
      console.error('Error processing clinical note:', error)
      setResult({
        success: false,
        error: 'Failed to process clinical note. Please try again.'
      })
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-4 sm:p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Heidi Clinical Decision Support</h1>
          <p className="text-muted-foreground">
            Evidence-based treatment recommendations powered by MCP
          </p>
        </div>
        
        <ClinicalNoteInput 
          onSubmit={handleSubmit} 
          isLoading={isProcessing}
        />
        
        {result && (
          <TreatmentPlanDisplay data={result} />
        )}
      </div>
    </div>
  )
}

export default App