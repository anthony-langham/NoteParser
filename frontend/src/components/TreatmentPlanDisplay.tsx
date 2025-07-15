import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { CheckCircle2, AlertTriangle, User, Scale, Calendar, Pill, Stethoscope, Clock } from 'lucide-react'
import { ErrorAlert } from './ErrorAlert'

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
  medication_name?: string
  medication?: string
  calculated_dose: number
  dose_per_kg?: number
  patient_weight?: number
  dosing_rationale?: string
  route: string
  frequency: string
  duration: string
  min_dose?: number
  max_dose?: number
}

interface MonitoringInfo {
  frequency?: string
  parameters?: string[]
  duration?: string
  location?: string
}

interface FollowUpInfo {
  timeline?: string
  instructions?: string[]
  parent_education?: string[]
}

interface TreatmentPlan {
  condition_name: string
  severity: string
  medications: any[]
  immediate_actions: string[]
  monitoring: string | MonitoringInfo
  follow_up: string | FollowUpInfo
}

interface Recommendations {
  primary_medication?: CalculatedDose
  monitoring: string | MonitoringInfo
  follow_up: string | FollowUpInfo
}

interface TreatmentPlanResponse {
  success: boolean
  error?: string
  patient_data?: PatientData
  condition?: Condition
  calculated_doses?: CalculatedDose[]
  treatment_plan?: TreatmentPlan
  recommendations?: Recommendations
}

interface TreatmentPlanDisplayProps {
  data: TreatmentPlanResponse
}

export function TreatmentPlanDisplay({ data }: TreatmentPlanDisplayProps) {
  if (!data.success) {
    return (
      <ErrorAlert 
        title="Processing Error"
        message={data.error || 'An error occurred while processing the clinical note.'}
        className="w-full"
      />
    )
  }

  const { patient_data, condition, calculated_doses, treatment_plan } = data

  // Handle cases where data might be undefined
  if (!patient_data && !condition && !calculated_doses && !treatment_plan) {
    return (
      <ErrorAlert 
        title="No Data Available"
        message="No clinical data was returned from the processing request."
        className="w-full"
      />
    )
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
    <div className="w-full space-y-4 sm:space-y-6">
      {/* Header with Success Indicator */}
      <Card className="border-green-200 bg-green-50/50">
        <CardHeader className="pb-4 sm:pb-6">
          <CardTitle className="flex items-center gap-2 text-green-800 text-base sm:text-lg">
            <CheckCircle2 className="h-4 w-4 sm:h-5 sm:w-5" />
            Clinical Analysis Complete
          </CardTitle>
          <CardDescription className="text-sm sm:text-base">
            Evidence-based treatment recommendations generated successfully
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Patient Information */}
      {patient_data && (
        <Card>
          <CardHeader className="pb-4 sm:pb-6">
            <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
              <User className="h-4 w-4 sm:h-5 sm:w-5" />
              Patient Information
            </CardTitle>
          </CardHeader>
          <CardContent className="px-4 sm:px-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 sm:gap-4">
              {patient_data.name && (
                <div className="space-y-1">
                  <p className="text-xs sm:text-sm font-medium text-muted-foreground">Name</p>
                  <p className="text-sm sm:text-base font-medium">{patient_data.name}</p>
                </div>
              )}
              {patient_data.age && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
                    <p className="text-xs sm:text-sm font-medium text-muted-foreground">Age</p>
                  </div>
                  <p className="text-sm sm:text-base font-medium">{patient_data.age}</p>
                </div>
              )}
              {patient_data.weight && (
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <Scale className="h-3 w-3 sm:h-4 sm:w-4 text-muted-foreground" />
                    <p className="text-xs sm:text-sm font-medium text-muted-foreground">Weight</p>
                  </div>
                  <p className="text-sm sm:text-base font-medium">{patient_data.weight} kg</p>
                </div>
              )}
              {patient_data.severity && (
                <div className="space-y-1">
                  <p className="text-xs sm:text-sm font-medium text-muted-foreground">Severity</p>
                  <Badge className={`${getSeverityColor(patient_data.severity)} text-xs sm:text-sm`}>
                    {patient_data.severity}
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Condition Identification */}
      {condition && (
        <Card>
          <CardHeader className="pb-4 sm:pb-6">
            <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
              <Stethoscope className="h-4 w-4 sm:h-5 sm:w-5" />
              Condition Identification
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 sm:space-y-4 px-4 sm:px-6">
            <div className="flex items-center gap-3">
              <h3 className="text-base sm:text-lg font-semibold">{condition.name}</h3>
            </div>
            
            {condition.matched_symptoms.length > 0 && (
              <div>
                <p className="text-xs sm:text-sm font-medium text-muted-foreground mb-2">Matched Symptoms:</p>
                <div className="flex flex-wrap gap-1.5 sm:gap-2">
                  {condition.matched_symptoms.map((symptom, index) => (
                    <Badge key={index} variant="secondary" className="text-xs break-words">
                      {symptom}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Medication Doses */}
      {calculated_doses && calculated_doses.length > 0 && (
        <Card>
          <CardHeader className="pb-4 sm:pb-6">
            <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
              <Pill className="h-4 w-4 sm:h-5 sm:w-5" />
              Calculated Medication Doses
            </CardTitle>
            <CardDescription className="text-sm sm:text-base">
              Weight-based dosing calculations with safety limits
            </CardDescription>
          </CardHeader>
          <CardContent className="px-4 sm:px-6">
            <div className="space-y-3 sm:space-y-4">
              {calculated_doses.map((dose, index) => (
                <div key={index} className="border rounded-lg p-3 sm:p-4 space-y-2 sm:space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="font-semibold text-sm sm:text-base break-words">{dose.medication_name || dose.medication}</h4>
                    {dose.success ? (
                      <CheckCircle2 className="h-4 w-4 sm:h-5 sm:w-5 text-green-600 flex-shrink-0" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 sm:h-5 sm:w-5 text-red-600 flex-shrink-0" />
                    )}
                  </div>
                  
                  {dose.success && (
                    <div className="space-y-2 sm:space-y-3">
                      {/* Dosing Calculation */}
                      {dose.dose_per_kg && dose.patient_weight && (
                        <div className="bg-blue-50 border border-blue-200 rounded-md p-2 sm:p-3">
                          <div className="text-xs font-medium text-blue-800 mb-1">Weight-Based Calculation</div>
                          <div className="text-xs sm:text-sm text-blue-700 break-words">
                            <span className="font-semibold">{dose.dose_per_kg} mg/kg</span> × <span className="font-semibold">{dose.patient_weight} kg</span> = <span className="font-semibold">{dose.calculated_dose} mg</span>
                          </div>
                          {dose.dosing_rationale && (
                            <div className="text-xs text-blue-600 mt-1 break-words">{dose.dosing_rationale}</div>
                          )}
                        </div>
                      )}
                      
                      {/* Medication Details */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 text-xs sm:text-sm">
                        <div className="space-y-1">
                          <span className="font-medium text-muted-foreground block">Final Dose:</span>
                          <span className="font-semibold">{dose.calculated_dose} mg</span>
                        </div>
                        <div className="space-y-1">
                          <span className="font-medium text-muted-foreground block">Route:</span>
                          <span>{dose.route}</span>
                        </div>
                        <div className="space-y-1">
                          <span className="font-medium text-muted-foreground block">Frequency:</span>
                          <span>{dose.frequency}</span>
                        </div>
                        <div className="space-y-1">
                          <span className="font-medium text-muted-foreground block">Duration:</span>
                          <span>{dose.duration}</span>
                        </div>
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
      {treatment_plan && (
        <Card>
          <CardHeader className="pb-4 sm:pb-6">
            <CardTitle className="text-base sm:text-lg">Treatment Plan</CardTitle>
            <CardDescription className="text-sm sm:text-base">
              Evidence-based management recommendations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 sm:space-y-4 px-4 sm:px-6">
            {/* Immediate Actions */}
            {treatment_plan.immediate_actions && treatment_plan.immediate_actions.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 text-sm sm:text-base">Immediate Actions</h4>
                <ul className="space-y-1.5 sm:space-y-2">
                  {treatment_plan.immediate_actions.map((action, index) => (
                    <li key={index} className="flex items-start gap-2 text-xs sm:text-sm">
                      <CheckCircle2 className="h-3 w-3 sm:h-4 sm:w-4 text-green-600 mt-0.5 flex-shrink-0" />
                      <span className="break-words">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Treatment Plan Monitoring */}
            {treatment_plan.monitoring && (
              <div>
                <h4 className="font-semibold mb-2 flex items-center gap-2 text-sm sm:text-base">
                  <Clock className="h-3 w-3 sm:h-4 sm:w-4" />
                  Treatment Monitoring
                </h4>
                {typeof treatment_plan.monitoring === 'string' ? (
                  <p className="text-xs sm:text-sm text-muted-foreground break-words">{treatment_plan.monitoring}</p>
                ) : (
                  <div className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
                    {treatment_plan.monitoring.frequency && (
                      <p className="break-words"><span className="font-medium">Frequency:</span> {treatment_plan.monitoring.frequency}</p>
                    )}
                    {treatment_plan.monitoring.parameters && Array.isArray(treatment_plan.monitoring.parameters) && (
                      <div>
                        <span className="font-medium">Parameters:</span>
                        <ul className="list-disc list-inside ml-3 sm:ml-4 space-y-0.5 sm:space-y-1 mt-1">
                          {treatment_plan.monitoring.parameters.map((param: string, idx: number) => (
                            <li key={idx} className="break-words">{param}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {treatment_plan.monitoring.duration && (
                      <p className="break-words"><span className="font-medium">Duration:</span> {treatment_plan.monitoring.duration}</p>
                    )}
                    {treatment_plan.monitoring.location && (
                      <p className="break-words"><span className="font-medium">Location:</span> {treatment_plan.monitoring.location}</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Treatment Plan Follow-up */}
            {treatment_plan.follow_up && (
              <div>
                <h4 className="font-semibold mb-2 text-sm sm:text-base">Treatment Follow-up</h4>
                {typeof treatment_plan.follow_up === 'string' ? (
                  <p className="text-xs sm:text-sm text-muted-foreground break-words">{treatment_plan.follow_up}</p>
                ) : (
                  <div className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
                    {treatment_plan.follow_up.timeline && (
                      <p className="break-words"><span className="font-medium">Timeline:</span> {treatment_plan.follow_up.timeline}</p>
                    )}
                    {treatment_plan.follow_up.instructions && Array.isArray(treatment_plan.follow_up.instructions) && (
                      <div>
                        <span className="font-medium">Instructions:</span>
                        <ul className="list-disc list-inside ml-3 sm:ml-4 space-y-0.5 sm:space-y-1 mt-1">
                          {treatment_plan.follow_up.instructions.map((instruction: string, idx: number) => (
                            <li key={idx} className="break-words">{instruction}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {treatment_plan.follow_up.parent_education && Array.isArray(treatment_plan.follow_up.parent_education) && (
                      <div>
                        <span className="font-medium">Parent Education:</span>
                        <ul className="list-disc list-inside ml-3 sm:ml-4 space-y-0.5 sm:space-y-1 mt-1">
                          {treatment_plan.follow_up.parent_education.map((education: string, idx: number) => (
                            <li key={idx} className="break-words">{education}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

          </CardContent>
        </Card>
      )}

      {/* Clinical Disclaimer */}
      <Card className="border-amber-200 bg-amber-50/50">
        <CardContent className="pt-4 sm:pt-6 px-4 sm:px-6">
          <div className="flex items-start gap-2 sm:gap-3">
            <AlertTriangle className="h-4 w-4 sm:h-5 sm:w-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="space-y-1">
              <p className="text-xs sm:text-sm font-medium text-amber-800">Clinical Decision Support Tool</p>
              <p className="text-xs sm:text-sm text-amber-700 break-words">
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