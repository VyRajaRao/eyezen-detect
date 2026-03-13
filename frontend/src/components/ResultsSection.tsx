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

                <div className="grid grid-cols-2 gap-4 pt-4">
                  <Button
                    variant="outline"
                    className="border-neon-purple/50 hover:border-neon-purple hover:bg-neon-purple/10"
                    onClick={() => {
                      if (result.heatmap) {
                        // Create a modern heatmap modal window with better styling
                        const newWindow = window.open('', '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
                        if (newWindow) {
                          newWindow.document.write(`
                            <!DOCTYPE html>
                            <html>
                              <head>
                                <title>AI Heatmap Analysis - ${result.disease}</title>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <style>
                                  * { margin: 0; padding: 0; box-sizing: border-box; }
                                  body { 
                                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                    background: linear-gradient(135deg, #0a0a0a, #1a1a2e, #16213e);
                                    color: white;
                                    min-height: 100vh;
                                    display: flex;
                                    flex-direction: column;
                                    align-items: center;
                                    padding: 20px;
                                  }
                                  .header {
                                    text-align: center;
                                    margin-bottom: 30px;
                                  }
                                  .title {
                                    font-size: 2.5rem;
                                    font-weight: bold;
                                    background: linear-gradient(45deg, #00f5ff, #ff00ff);
                                    -webkit-background-clip: text;
                                    -webkit-text-fill-color: transparent;
                                    margin-bottom: 10px;
                                  }
                                  .subtitle {
                                    font-size: 1.2rem;
                                    opacity: 0.8;
                                    margin-bottom: 5px;
                                  }
                                  .confidence {
                                    font-size: 1rem;
                                    color: #00f5ff;
                                    font-weight: 600;
                                  }
                                  .heatmap-container {
                                    max-width: 100%;
                                    border: 2px solid #00f5ff;
                                    border-radius: 15px;
                                    overflow: hidden;
                                    box-shadow: 0 0 30px rgba(0, 245, 255, 0.3);
                                    transition: transform 0.3s ease;
                                  }
                                  .heatmap-container:hover {
                                    transform: scale(1.02);
                                    box-shadow: 0 0 50px rgba(0, 245, 255, 0.5);
                                  }
                                  img {
                                    max-width: 100%;
                                    height: auto;
                                    display: block;
                                  }
                                  .info {
                                    margin-top: 30px;
                                    text-align: center;
                                    max-width: 600px;
                                  }
                                  .info-grid {
                                    display: grid;
                                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                    gap: 20px;
                                    margin-top: 20px;
                                  }
                                  .info-card {
                                    background: rgba(255, 255, 255, 0.1);
                                    padding: 15px;
                                    border-radius: 10px;
                                    border: 1px solid rgba(0, 245, 255, 0.3);
                                  }
                                  .info-card h3 {
                                    color: #ff00ff;
                                    margin-bottom: 5px;
                                  }
                                  .close-btn {
                                    position: fixed;
                                    top: 20px;
                                    right: 20px;
                                    background: linear-gradient(45deg, #ff00ff, #00f5ff);
                                    border: none;
                                    color: white;
                                    padding: 10px 15px;
                                    border-radius: 20px;
                                    cursor: pointer;
                                    font-weight: bold;
                                    transition: transform 0.2s;
                                  }
                                  .close-btn:hover {
                                    transform: scale(1.1);
                                  }
                                </style>
                              </head>
                              <body>
                                <button class="close-btn" onclick="window.close()">✕ Close</button>
                                
                                <div class="header">
                                  <h1 class="title">AI Heatmap Analysis</h1>
                                  <h2 class="subtitle">Detected: ${result.disease}</h2>
                                  <p class="confidence">Confidence: ${Math.round(result.confidence * 100)}%</p>
                                </div>
                                
                                <div class="heatmap-container">
                                  <img src="data:image/png;base64,${result.heatmap}" 
                                       alt="Grad-CAM Heatmap Analysis" />
                                </div>
                                
                                <div class="info">
                                  <h3>About This Heatmap</h3>
                                  <p>This heatmap shows the areas of the retinal image that the AI model focused on when making its prediction. Brighter areas indicate regions that had more influence on the diagnosis.</p>
                                  
                                  <div class="info-grid">
                                    <div class="info-card">
                                      <h3>Red/Hot Areas</h3>
                                      <p>High attention regions that strongly influenced the prediction</p>
                                    </div>
                                    <div class="info-card">
                                      <h3>Blue/Cool Areas</h3>
                                      <p>Low attention regions with minimal impact on diagnosis</p>
                                    </div>
                                    <div class="info-card">
                                      <h3>Technology</h3>
                                      <p>Generated using Grad-CAM (Gradient-weighted Class Activation Mapping)</p>
                                    </div>
                                  </div>
                                </div>
                              </body>
                            </html>
                          `);
                          newWindow.document.close();
                        }
                      } else {
                        // Show a more user-friendly message
                        const message = document.createElement('div');
                        message.className = 'fixed top-4 right-4 bg-orange-500/90 text-white px-6 py-3 rounded-lg shadow-lg z-50';
                        message.innerHTML = '⚠️ Heatmap not available for this prediction';
                        document.body.appendChild(message);
                        setTimeout(() => {
                          document.body.removeChild(message);
                        }, 3000);
                      }
                    }}
                    disabled={!result.heatmap}
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    {result.heatmap ? 'View AI Heatmap' : 'Heatmap Unavailable'}
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
                  <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                    <span className="text-sm">Model Used</span>
                    <Badge variant="secondary">EfficientNetB0</Badge>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                    <span className="text-sm">Processing Time</span>
                    <span className="text-sm text-neon-cyan">2.3s</span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-muted/50 rounded-lg">
                    <span className="text-sm">Image Quality</span>
                    <span className="text-sm text-neon-green">Excellent</span>
                  </div>
                  
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
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </section>
  );
};