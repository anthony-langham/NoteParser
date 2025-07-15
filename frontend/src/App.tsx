import { useState } from 'react'
import { ClinicalNoteInput } from './components/ClinicalNoteInput'
import { TreatmentPlanDisplay } from './components/TreatmentPlanDisplay'

// Sample response for demonstration (will be replaced with actual API in task #023)
const sampleResponse = {
  success: true,
  patient_data: {
    name: "Jack T.",
    age: "3 years",
    weight: 14.2,
    severity: "moderate"
  },
  condition: {
    name: "Croup (Laryngotracheobronchitis)",
    confidence: 0.85,
    matched_symptoms: ["barky cough", "hoarse voice", "stridor", "low-grade fever"]
  },
  calculated_doses: [
    {
      success: true,
      medication_name: "Prednisolone",
      calculated_dose: 14.2,
      route: "oral",
      frequency: "single dose",
      duration: "once",
      min_dose: 5,
      max_dose: 20
    }
  ],
  treatment_plan: {
    condition_name: "Croup",
    severity: "moderate",
    medications: [],
    immediate_actions: [
      "Administer oral prednisolone 1mg/kg (14.2mg for this patient)",
      "Monitor respiratory status closely",
      "Ensure adequate hydration",
      "Consider nebulized budesonide if severe"
    ],
    monitoring: {},
    follow_up: {}
  },
  recommendations: {
    monitoring: "Monitor for respiratory distress, oxygen saturation, and response to treatment. Assess for signs of improvement or deterioration every 2-4 hours.",
    follow_up: "Follow up with primary care provider within 24-48 hours. Return immediately if breathing difficulties worsen or new symptoms develop."
  }
}

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState<any>(null)

  const handleSubmit = async (_note: string) => {
    setIsProcessing(true)
    setResult(null)
    
    // For now, simulate processing with sample data
    // In the next task (#023), this will call the actual API
    setTimeout(() => {
      setResult(sampleResponse)
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
          <TreatmentPlanDisplay data={result} />
        )}
      </div>
    </div>
  )
}

export default App