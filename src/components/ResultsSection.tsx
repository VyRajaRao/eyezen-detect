import { Download, Eye, AlertCircle, CheckCircle2, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import type { PredictionResult } from "@/types";

interface ResultsSectionProps {
  result: PredictionResult | null;
  uploadedImage: string | null;
  isLoading: boolean;
}

export const ResultsSection = ({ result, uploadedImage, isLoading }: ResultsSectionProps) => {
  if (!uploadedImage && !result) return null;

  const generatePDFReport = () => {
    // Mock PDF generation - in real app, this would call backend API
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,AI Eye Scan Report\n\nDisease: ' + result?.disease + '\nConfidence: ' + (result?.confidence ? Math.round(result.confidence * 100) : 0) + '%\nDate: ' + new Date().toLocaleDateString());
    element.setAttribute('download', 'eye-scan-report.txt');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const getResultColor = (disease: string) => {
    if (disease.toLowerCase() === 'normal') return 'text-neon-green';
    if (disease.toLowerCase().includes('diabetic')) return 'text-neon-orange';
    return 'text-neon-pink';
  };

  const getResultIcon = (disease: string) => {
    if (disease.toLowerCase() === 'normal') return CheckCircle2;
    return AlertCircle;
  };

  return (
    <section className="py-20 px-6 bg-muted/20">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-neon-purple to-neon-pink bg-clip-text text-transparent">
            Analysis Results
          </h2>
          <p className="text-muted-foreground text-lg">
            AI-powered eye disease detection results
          </p>
        </div>

        {isLoading && (
          <Card className="border-neon-cyan/30 bg-card/80 backdrop-blur-sm">
            <CardContent className="p-8 text-center">
              <div className="animate-pulse space-y-4">
                <div className="w-16 h-16 bg-neon-cyan/20 rounded-full mx-auto"></div>
                <div className="h-4 bg-muted rounded w-3/4 mx-auto"></div>
                <div className="h-3 bg-muted rounded w-1/2 mx-auto"></div>
              </div>
            </CardContent>
          </Card>
        )}

        {result && (
          <div className="space-y-6">
            {/* Demo mode warning banner */}
            {result.demo_mode && (
              <div className="flex items-start gap-3 p-4 rounded-lg border border-yellow-500/40 bg-yellow-500/5 text-yellow-400 text-sm animate-fade-in-up">
                <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0 text-yellow-500" />
                <div>
                  <p className="font-semibold text-yellow-400">Demo Mode – ML service not running</p>
                  <p className="text-yellow-400/80 mt-1">
                    The Python ML service is unavailable so all scores below are placeholder zeros.
                    Start the Python service (see README) to enable real predictions.
                  </p>
                </div>
              </div>
            )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Main Result Card */}
            <Card className="border-neon-cyan/30 bg-card/80 backdrop-blur-sm animate-fade-in-up">
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  {(() => {
                    const Icon = getResultIcon(result.disease);
                    return <Icon className={`w-6 h-6 ${getResultColor(result.disease)}`} />;
                  })()}
                  Detection Result
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className={`text-2xl font-bold mb-2 ${getResultColor(result.disease)}`}>
                    {result.disease}
                  </h3>
                  <Badge 
                    variant="secondary"
                    className="bg-neon-cyan/10 text-neon-cyan border-neon-cyan/30"
                  >
                    AI Confidence: {Math.round(result.confidence * 100)}%
                  </Badge>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Confidence Score</span>
                    <span>{Math.round(result.confidence * 100)}%</span>
                  </div>
                  <Progress 
                    value={result.confidence * 100} 
                    className="h-3"
                  />
                </div>

                {/* ODIR multi-label breakdown */}
                {result.odir_predictions && result.odir_predictions.length > 0 && (
                  <div className="space-y-2 pt-2">
                    <p className="text-sm font-medium">All condition scores:</p>
                    {result.odir_predictions
                      .slice()
                      .sort((a, b) => b.score - a.score)
                      .map((pred) => (
                        <div key={pred.label} className="flex items-center gap-2 text-xs">
                          <span className="w-40 truncate text-muted-foreground">{pred.label}</span>
                          <Progress value={pred.score * 100} className="h-1.5 flex-1" />
                          <span className="w-10 text-right text-muted-foreground">
                            {Math.round(pred.score * 100)}%
                          </span>
                        </div>
                      ))}
                  </div>
                )}

                <div className="grid grid-cols-2 gap-4 pt-4">
                  <Button
                    variant="outline"
                    className="border-neon-purple/50 hover:border-neon-purple hover:bg-neon-purple/10"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    View Heatmap
                  </Button>
                  <Button
                    onClick={generatePDFReport}
                    className="bg-gradient-to-r from-neon-cyan to-neon-purple hover:shadow-neon"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Download Report
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Analysis Details Card */}
            <Card className="border-neon-purple/30 bg-card/80 backdrop-blur-sm animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <TrendingUp className="w-6 h-6 text-neon-purple" />
                  Analysis Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  {result.model_version && (
                    <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                      <span className="text-sm">Model Version</span>
                      <Badge variant="secondary">{result.model_version}</Badge>
                    </div>
                  )}
                  
                  {result.aptos_dr_grade && (
                    <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                      <span className="text-sm">DR Grade (APTOS)</span>
                      <span className="text-sm text-neon-cyan">{result.aptos_dr_grade}</span>
                    </div>
                  )}
                  
                  <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                    <span className="text-sm">Analysis Date</span>
                    <span className="text-sm">{new Date().toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-border">
                  <h4 className="text-sm font-semibold mb-2">Recommendation</h4>
                  <p className="text-sm text-muted-foreground">
                    {result.disease.toLowerCase() === 'normal' 
                      ? "Your retinal scan appears normal. Continue regular eye exams as recommended by your eye care professional."
                      : "Please consult with an eye care professional for proper evaluation and treatment options. This AI analysis is for informational purposes only."
                    }
                  </p>
                  {result.notes && (
                    <p className="text-xs text-muted-foreground/70 mt-2 italic">{result.notes}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
          </div>
        )}
      </div>
    </section>
  );
};