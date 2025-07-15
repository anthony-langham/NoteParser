import { useState } from 'react'
import { ClinicalNoteInput } from './components/ClinicalNoteInput'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const handleSubmit = async (note: string) => {
    setIsProcessing(true)
    setResult(null)
    
    // For now, just simulate processing
    // In the next task (#023), this will call the actual API
    setTimeout(() => {
      setResult(`Received clinical note with ${note.length} characters. API integration coming in task #023.`)
      setIsProcessing(false)
    }, 2000)
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
          <div className="rounded-lg border bg-muted p-4">
            <p className="text-sm">{result}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App