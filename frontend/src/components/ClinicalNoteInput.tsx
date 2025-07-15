import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Textarea } from './ui/textarea'
import { Button } from './ui/button'
import { Loader2, Shuffle } from 'lucide-react'

interface ClinicalNoteInputProps {
  onSubmit: (note: string) => void
  isLoading?: boolean
}

export function ClinicalNoteInput({ onSubmit, isLoading = false }: ClinicalNoteInputProps) {
  const [note, setNote] = useState('')
  const [error, setError] = useState('')

  const sampleNotes = [
    {
      title: "Jack T. - Moderate Croup",
      note: `Patient: Jack T.
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
    },
    {
      title: "Emma S. - Mild Croup",
      note: `Patient: Emma S.
DOB: 15/08/2021
Age: 2 years 11 months
Weight: 12.8 kg

Presenting complaint:
Emma presented with a 1-day history of occasional barky cough and mild hoarse voice. No fever reported. Child appears comfortable and is eating and drinking normally.

Assessment:
Mild croup symptoms. No stridor at rest, no respiratory distress.

Plan:
- Supportive care
- Safety netting advice`
    },
    {
      title: "Oliver M. - Severe Croup",
      note: `Patient: Oliver M.
DOB: 10/06/2020
Age: 4 years 1 month
Weight: 16.5 kg

Presenting complaint:
Oliver brought in by parents with severe respiratory distress. 3-day history of barky cough and hoarse voice, now with prominent inspiratory stridor audible from the end of the bed. Marked suprasternal and intercostal retractions. Child appears agitated and is drooling.

Assessment:
Severe croup with significant respiratory distress. Concerned about impending respiratory failure.

Plan:
- Urgent corticosteroids
- Consider nebulized adrenaline
- Close monitoring`
    },
    {
      title: "Baby Sophie - Young Infant Croup",
      note: `Patient: Baby Sophie R.
DOB: 12/01/2024
Age: 6 months
Weight: 7.2 kg

Presenting complaint:
Sophie presented with a 12-hour history of barky cough and mild stridor. Low-grade fever of 37.8°C. Parents report she has been feeding well but sounds congested.

Assessment:
Early croup symptoms in young infant. Mild to moderate presentation.

Plan:
- Close observation
- Consider steroids if worsening`
    }
  ]

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

  const handleLoadRandomSample = () => {
    const randomIndex = Math.floor(Math.random() * sampleNotes.length)
    const selectedSample = sampleNotes[randomIndex]
    setNote(selectedSample.note)
    setError('')
  }

  const handleClear = () => {
    setNote('')
    setError('')
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-4 sm:pb-6">
        <CardTitle className="text-lg sm:text-xl">Clinical Note Input</CardTitle>
        <CardDescription className="text-sm sm:text-base">
          Enter a clinical note to receive evidence-based treatment recommendations and dose calculations
        </CardDescription>
      </CardHeader>
      <CardContent className="px-4 sm:px-6">
        <form onSubmit={handleSubmit} className="space-y-3 sm:space-y-4">
          <div className="space-y-2">
            <Textarea
              placeholder="Enter clinical note here..."
              value={note}
              onChange={(e) => {
                setNote(e.target.value)
                setError('')
              }}
              className="min-h-[200px] sm:min-h-[250px] lg:min-h-[300px] font-mono text-sm resize-y"
              disabled={isLoading}
            />
            {error && (
              <div className="bg-destructive/10 border border-destructive/20 rounded-md p-2 sm:p-3">
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}
          </div>
          
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
            <Button 
              type="submit" 
              disabled={isLoading || !note.trim()}
              className="w-full sm:w-auto sm:flex-1 lg:flex-none lg:min-w-[200px]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  <span className="hidden sm:inline">Processing...</span>
                  <span className="sm:hidden">Processing</span>
                </>
              ) : (
                <>
                  <span className="hidden sm:inline">Process Clinical Note</span>
                  <span className="sm:hidden">Process Note</span>
                </>
              )}
            </Button>
            
            <div className="flex flex-row gap-2 sm:gap-3">
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleLoadRandomSample}
                disabled={isLoading}
                className="flex-1 sm:flex-none"
              >
                <Shuffle className="mr-1 h-3 w-3 sm:h-4 sm:w-4" />
                <span className="hidden sm:inline">Load Random Sample</span>
                <span className="sm:hidden">Random</span>
              </Button>
              
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleClear}
                disabled={isLoading}
                className="flex-1 sm:flex-none"
              >
                Clear
              </Button>
            </div>
          </div>
          
          <div className="text-xs sm:text-sm text-muted-foreground bg-muted/30 p-2 sm:p-3 rounded-md">
            <p><strong>Note:</strong> This tool is for clinical decision support only. All recommendations should be validated by qualified medical professionals.</p>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}