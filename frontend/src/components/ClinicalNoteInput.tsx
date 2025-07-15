import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Textarea } from './ui/textarea'
import { Button } from './ui/button'
import { Loader2 } from 'lucide-react'

interface ClinicalNoteInputProps {
  onSubmit: (note: string) => void
  isLoading?: boolean
}

export function ClinicalNoteInput({ onSubmit, isLoading = false }: ClinicalNoteInputProps) {
  const [note, setNote] = useState('')
  const [error, setError] = useState('')

  const sampleNote = `Patient: Jack T.
DOB: 12/03/2022
Age: 3 years
Weight: 14.2 kg

Presenting complaint:
Jack presented with a 2-day history of barky cough, hoarse voice, and low-grade fever. Symptoms worsened overnight, with increased work of breathing and stridor noted at rest this morning.

Assessment:
Jack presents with classic features of moderate croup (laryngotracheobronchitis), likely viral in origin.

Plan:
- Administer corticosteroids
- Plan as per local guidelines for croup`

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (!note.trim()) {
      setError('Please enter a clinical note')
      return
    }

    if (note.trim().length < 50) {
      setError('Clinical note should be more detailed (at least 50 characters)')
      return
    }

    onSubmit(note)
  }

  const handleLoadSample = () => {
    setNote(sampleNote)
    setError('')
  }

  const handleClear = () => {
    setNote('')
    setError('')
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Clinical Note Input</CardTitle>
        <CardDescription>
          Enter a clinical note to receive evidence-based treatment recommendations and dose calculations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Textarea
              placeholder="Enter clinical note here..."
              value={note}
              onChange={(e) => {
                setNote(e.target.value)
                setError('')
              }}
              className="min-h-[300px] font-mono text-sm"
              disabled={isLoading}
            />
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </div>
          
          <div className="flex flex-col sm:flex-row gap-2">
            <Button 
              type="submit" 
              disabled={isLoading || !note.trim()}
              className="flex-1 sm:flex-none"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                'Process Clinical Note'
              )}
            </Button>
            
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleLoadSample}
              disabled={isLoading}
            >
              Load Sample
            </Button>
            
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleClear}
              disabled={isLoading}
            >
              Clear
            </Button>
          </div>
          
          <div className="text-xs text-muted-foreground">
            <p>Note: This tool is for clinical decision support only. All recommendations should be validated by qualified medical professionals.</p>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}