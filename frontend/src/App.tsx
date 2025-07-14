import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Input } from './components/ui/input'
import { Textarea } from './components/ui/textarea'

function App() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Heidi Clinical Decision Support</CardTitle>
            <CardDescription>shadcn/ui components test</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input placeholder="Test input component" />
            <Textarea placeholder="Test textarea component" />
            <Button>Test Button</Button>
            <Button variant="outline">Outline Button</Button>
            <Button variant="secondary">Secondary Button</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App