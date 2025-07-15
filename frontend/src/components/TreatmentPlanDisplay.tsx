import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { CheckCircle2, AlertTriangle, User, Scale, Calendar, Pill, Stethoscope, Clock } from 'lucide-react'

interface PatientData {
  name?: string
  age?: string
  weight?: number
  severity?: string
}

interface Condition {
  name: string
  confidence: number
  matched_symptoms: string[]
}

interface CalculatedDose {
  success: boolean
  medication_name: string
  calculated_dose: number
  route: string
  frequency: string
  duration: string
  min_dose?: number
  max_dose?: number
}

interface TreatmentPlan {
  condition_name: string
  severity: string
  medications: any[]
  immediate_actions: string[]
  monitoring: any
  follow_up: any
}

interface Recommendations {
  primary_medication?: CalculatedDose
  monitoring: string
  follow_up: string
}

interface TreatmentPlanResponse {
  success: boolean
  patient_data: PatientData
  condition: Condition
  calculated_doses: CalculatedDose[]
  treatment_plan: TreatmentPlan
  recommendations: Recommendations
}

interface TreatmentPlanDisplayProps {
  data: TreatmentPlanResponse
}

export function TreatmentPlanDisplay({ data }: TreatmentPlanDisplayProps) {
  if (!data.success) {
    return (
      <Card className="w-full border-destructive">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Processing Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {(data as any).error || 'An error occurred while processing the clinical note.'}
          </p>
        </CardContent>
      </Card>
    )
  }

  const { patient_data, condition, calculated_doses, treatment_plan, recommendations } = data

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 border-green-200'
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    return 'bg-red-100 text-red-800 border-red-200'
  }

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'mild': return 'bg-green-100 text-green-800 border-green-200'
      case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'severe': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="w-full space-y-6">
      {/* Header with Success Indicator */}
      <Card className="border-green-200 bg-green-50/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-800">
            <CheckCircle2 className="h-5 w-5" />
            Clinical Analysis Complete
          </CardTitle>
          <CardDescription>
            Evidence-based treatment recommendations generated successfully
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Patient Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Patient Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {patient_data.name && (
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground">Name</p>
                <p className="text-sm">{patient_data.name}</p>
              </div>
            )}
            {patient_data.age && (
              <div className="space-y-1 flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Age</p>
                  <p className="text-sm">{patient_data.age}</p>
                </div>
              </div>
            )}
            {patient_data.weight && (
              <div className="space-y-1 flex items-center gap-2">
                <Scale className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Weight</p>
                  <p className="text-sm">{patient_data.weight} kg</p>
                </div>
              </div>
            )}
            {patient_data.severity && (
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground">Severity</p>
                <Badge className={getSeverityColor(patient_data.severity)}>
                  {patient_data.severity}
                </Badge>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Condition Identification */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Stethoscope className="h-5 w-5" />
            Condition Identification
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold">{condition.name}</h3>
            <Badge className={getConfidenceColor(condition.confidence)}>
              {Math.round(condition.confidence * 100)}% confidence
            </Badge>
          </div>
          
          {condition.matched_symptoms.length > 0 && (
            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">Matched Symptoms:</p>
              <div className="flex flex-wrap gap-2">
                {condition.matched_symptoms.map((symptom, index) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {symptom}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Medication Doses */}
      {calculated_doses.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Pill className="h-5 w-5" />
              Calculated Medication Doses
            </CardTitle>
            <CardDescription>
              Weight-based dosing calculations with safety limits
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {calculated_doses.map((dose, index) => (
                <div key={index} className="border rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold text-base">{dose.medication_name}</h4>
                    {dose.success ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                  
                  {dose.success && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="font-medium text-muted-foreground">Dose: </span>
                        <span className="font-semibold">{dose.calculated_dose} mg</span>
                      </div>
                      <div>
                        <span className="font-medium text-muted-foreground">Route: </span>
                        <span>{dose.route}</span>
                      </div>
                      <div>
                        <span className="font-medium text-muted-foreground">Frequency: </span>
                        <span>{dose.frequency}</span>
                      </div>
                      <div>
                        <span className="font-medium text-muted-foreground">Duration: </span>
                        <span>{dose.duration}</span>
                      </div>
                    </div>
                  )}
                  
                  {dose.min_dose && dose.max_dose && (
                    <p className="text-xs text-muted-foreground">
                      Dose range: {dose.min_dose}-{dose.max_dose} mg
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Treatment Plan */}
      <Card>
        <CardHeader>
          <CardTitle>Treatment Plan</CardTitle>
          <CardDescription>
            Evidence-based management recommendations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Immediate Actions */}
          {treatment_plan.immediate_actions && treatment_plan.immediate_actions.length > 0 && (
            <div>
              <h4 className="font-semibold mb-2">Immediate Actions</h4>
              <ul className="space-y-1">
                {treatment_plan.immediate_actions.map((action, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Monitoring */}
          {recommendations.monitoring && (
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Monitoring
              </h4>
              <p className="text-sm text-muted-foreground">{recommendations.monitoring}</p>
            </div>
          )}

          {/* Follow-up */}
          {recommendations.follow_up && (
            <div>
              <h4 className="font-semibold mb-2">Follow-up</h4>
              <p className="text-sm text-muted-foreground">{recommendations.follow_up}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Clinical Disclaimer */}
      <Card className="border-amber-200 bg-amber-50/50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <p className="text-sm font-medium text-amber-800">Clinical Decision Support Tool</p>
              <p className="text-xs text-amber-700">
                This tool provides evidence-based recommendations for clinical decision support only. 
                All calculations and recommendations must be validated by qualified medical professionals. 
                This system does not replace clinical judgment or medical expertise.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}