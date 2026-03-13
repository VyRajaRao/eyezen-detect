import { AlertTriangle, Shield, Users, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

export const DisclaimerSection = () => {
  return (
    <section className="py-20 px-6 bg-muted/10">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4 text-neon-orange">
            Important Medical Disclaimer
          </h2>
          <p className="text-muted-foreground text-lg">
            Please read carefully before using our AI eye disease detection system
          </p>
        </div>

        <Alert className="mb-8 border-neon-orange/50 bg-neon-orange/5">
          <AlertTriangle className="h-4 w-4 text-neon-orange" />
          <AlertDescription className="text-foreground">
            <strong>This AI tool is for educational and informational purposes only.</strong> 
            It is not intended to diagnose, treat, cure, or prevent any disease. Always consult with 
            a qualified healthcare professional for proper medical evaluation and treatment.
          </AlertDescription>
        </Alert>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <Shield className="w-6 h-6 text-neon-cyan" />
                Not a Medical Device
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-muted-foreground">
              <p>• This AI system has not been approved by the FDA or other medical regulatory bodies</p>
              <p>• Results should not be used as the sole basis for medical decisions</p>
              <p>• The technology is designed for research and educational demonstration</p>
              <p>• False positives and negatives are possible with any AI system</p>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <Users className="w-6 h-6 text-neon-purple" />
                Professional Consultation
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-muted-foreground">
              <p>• Always seek advice from qualified ophthalmologists or optometrists</p>
              <p>• Regular professional eye exams are essential for eye health</p>
              <p>• If you have concerns about your vision, contact a healthcare provider</p>
              <p>• Emergency eye conditions require immediate professional attention</p>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <FileText className="w-6 h-6 text-neon-pink" />
                Data & Privacy
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-muted-foreground">
              <p>• Uploaded images are processed locally and not stored permanently</p>
              <p>• No personal health information is collected or retained</p>
              <p>• Images are automatically deleted after processing</p>
              <p>• This demo does not create medical records</p>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                <AlertTriangle className="w-6 h-6 text-neon-green" />
                Limitations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-muted-foreground">
              <p>• AI accuracy varies based on image quality and conditions</p>
              <p>• Some rare conditions may not be detected by the current model</p>
              <p>• Results are probabilistic estimates, not definitive diagnoses</p>
              <p>• System performance may vary across different populations</p>
            </CardContent>
          </Card>
        </div>

        <div className="mt-12 p-6 bg-card/30 rounded-lg border border-border/50 backdrop-blur-sm">
          <h3 className="text-xl font-semibold mb-4 text-center">When to Seek Immediate Medical Attention</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-muted-foreground">
            <div>
              <p className="font-semibold text-neon-orange mb-2">Urgent Symptoms:</p>
              <ul className="space-y-1 text-sm">
                <li>• Sudden vision loss</li>
                <li>• Severe eye pain</li>
                <li>• Flashing lights or new floaters</li>
                <li>• Curtain-like vision loss</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold text-neon-orange mb-2">Regular Check-ups:</p>
              <ul className="space-y-1 text-sm">
                <li>• Annual eye exams for adults</li>
                <li>• More frequent if you have diabetes</li>
                <li>• Family history of eye disease</li>
                <li>• Age-related risk factors</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};