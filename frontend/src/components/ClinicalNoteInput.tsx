import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Textarea } from './ui/textarea'
import { Button } from './ui/button'
import { Loader2, Shuffle } from 'lucide-react'

interface ClinicalNoteInputProps {
  onSubmit: (note: string) => void
  onClear?: () => void
  isLoading?: boolean
}

export function ClinicalNoteInput({ onSubmit, onClear, isLoading = false }: ClinicalNoteInputProps) {
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
    },
    {
      title: "David M. - Adult Acute Asthma",
      note: `Patient: David M.
DOB: 15/04/1985
Age: 38 years
Weight: 78 kg

Presenting complaint:
David presented with a 6-hour history of progressive shortness of breath, wheezing, and chest tightness. Known asthmatic, usually well controlled on salbutamol PRN. Triggered by exposure to fresh paint at work. Peak flow on arrival 180 L/min (usual best 450 L/min).

Assessment:
Moderate acute asthma exacerbation. Peak flow 40% of predicted. Audible wheezing, able to speak in sentences but clearly distressed.

Plan:
- Nebulized salbutamol and ipratropium
- Oral prednisolone
- Monitor response`
    },
    {
      title: "Margaret T. - COPD Exacerbation",
      note: `Patient: Margaret T.
DOB: 22/11/1955
Age: 68 years
Weight: 65 kg

Presenting complaint:
Margaret presented with a 3-day history of increased dyspnea, increased cough, and increased sputum production with change in sputum color to green. Known COPD, usual medications include tiotropium and salbutamol. Temperature 38.2°C, looks unwell.

Assessment:
Acute exacerbation of COPD with purulent sputum and fever, likely infective cause.

Plan:
- Antibiotics
- Prednisolone course
- Bronchodilator therapy
- Oxygen therapy (target 88-92%)`
    },
    {
      title: "Sarah J. - Adult Pneumonia",
      note: `Patient: Sarah J.
DOB: 08/09/1992
Age: 31 years
Weight: 68 kg

Presenting complaint:
Sarah presented with a 2-day history of fever (39.1°C), cough with productive sputum (yellow), and right-sided chest pain. Reports dyspnea on exertion and feeling generally unwell with loss of appetite. No significant past medical history.

Assessment:
Clinical features consistent with community-acquired pneumonia. CURB-65 score 1 (age <65, confusion absent, urea normal, respiratory rate 22, BP stable).

Plan:
- Chest X-ray
- Oral antibiotics
- Supportive care
- Safety netting advice`
    },
    {
      title: "Tommy R. - Pediatric Pneumonia",
      note: `Patient: Tommy R.
DOB: 14/03/2019
Age: 5 years
Weight: 18 kg

Presenting complaint:
Tommy brought in by parents with 48-hour history of fever (38.8°C), cough with productive sputum, and dyspnea. Parents report he's been off his food and complaining of chest pain. Respiratory rate 35/min, appears unwell.

Assessment:
Clinical features suggestive of pneumonia. Increased work of breathing, decreased air entry left base, dull percussion note.

Plan:
- Chest X-ray
- Oral antibiotics
- Paracetamol for fever
- Review in 24-48 hours`
    },
    {
      title: "Lily W. - Pediatric Gastroenteritis",
      note: `Patient: Lily W.
DOB: 20/06/2021
Age: 3 years
Weight: 14 kg

Presenting complaint:
Lily presented with a 2-day history of vomiting and diarrhea. Parents report 6-8 loose stools per day and frequent vomiting, particularly after trying to drink. Appears lethargic and has reduced wet nappies. Mild abdominal pain reported.

Assessment:
Gastroenteritis with mild to moderate dehydration. Decreased skin turgor, dry mucous membranes, but alert and responsive.

Plan:
- Oral rehydration therapy
- Anti-emetic if needed
- Dietary advice
- Safety netting for dehydration`
    },
    {
      title: "Robert H. - Severe Asthma",
      note: `Patient: Robert H.
DOB: 05/12/1975
Age: 48 years
Weight: 85 kg

Presenting complaint:
Robert brought in by ambulance with severe shortness of breath and wheezing. Unable to complete sentences, peak flow 120 L/min (usual best 380 L/min). Use of accessory muscles evident, appears exhausted.

Assessment:
Severe acute asthma exacerbation. Peak flow <33% predicted, silent chest in places, significant respiratory distress.

Plan:
- High-flow oxygen
- Continuous nebulizers
- IV corticosteroids
- Consider magnesium sulfate
- Urgent senior review`
    },
    {
      title: "Charlie B. - Infant Gastroenteritis",
      note: `Patient: Charlie B.
DOB: 18/01/2023
Age: 18 months
Weight: 11 kg

Presenting complaint:
Charlie presented with a 24-hour history of frequent watery diarrhea and vomiting. Parents report 8 loose stools and 4 vomits since yesterday. Still taking some fluids but less than usual. No fever. Mild abdominal pain evident from crying.

Assessment:
Viral gastroenteritis with mild dehydration. Alert and interactive, good capillary refill, moist mucous membranes.

Plan:
- Oral rehydration solution
- Continue breastfeeding/formula
- Probiotics
- Return if worsening`
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
    if (onClear) {
      onClear()
    }
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