import { Brain, Database, Target, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const AboutSection = () => {
  const features = [
    {
      icon: Brain,
      title: "Advanced AI Model",
      description: "EfficientNetB0 CNN trained on 50,000+ retinal images",
      color: "text-neon-cyan",
      bgColor: "bg-neon-cyan/10"
    },
    {
      icon: Database,
      title: "Quality Datasets",
      description: "APTOS 2019 & ODIR datasets for comprehensive training",
      color: "text-neon-purple",
      bgColor: "bg-neon-purple/10"
    },
    {
      icon: Target,
      title: "High Accuracy",
      description: "89% accuracy on validation set with continuous improvement",
      color: "text-neon-pink",
      bgColor: "bg-neon-pink/10"
    },
    {
      icon: Users,
      title: "Multiple Conditions",
      description: "Detects diabetic retinopathy, glaucoma, cataracts, and AMD",
      color: "text-neon-green",
      bgColor: "bg-neon-green/10"
    }
  ];

  const metrics = [
    { label: "Training Images", value: "50,000+", color: "text-neon-cyan" },
    { label: "Model Accuracy", value: "89%", color: "text-neon-purple" },
    { label: "Diseases Detected", value: "4+", color: "text-neon-pink" },
    { label: "Processing Time", value: "< 3s", color: "text-neon-green" }
  ];

  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-pink bg-clip-text text-transparent">
            About Our AI Technology
          </h2>
          <p className="text-muted-foreground text-lg max-w-3xl mx-auto">
            Our AI system uses state-of-the-art deep learning algorithms trained on extensive medical datasets 
            to provide accurate eye disease detection and analysis.
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          {metrics.map((metric, index) => (
            <Card key={metric.label} className="text-center border-border/50 bg-card/50 backdrop-blur-sm animate-fade-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
              <CardContent className="p-6">
                <div className={`text-3xl font-bold mb-2 ${metric.color}`}>
                  {metric.value}
                </div>
                <div className="text-sm text-muted-foreground">
                  {metric.label}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
          {features.map((feature, index) => (
            <Card key={feature.title} className="border-border/50 bg-card/50 backdrop-blur-sm hover:shadow-glow transition-all duration-300 animate-fade-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${feature.bgColor}`}>
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Technical Details */}
        <Card className="border-neon-cyan/30 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="text-2xl text-center">
              Technical Specifications
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-neon-cyan">Model Architecture</h4>
                <div className="space-y-2">
                  <Badge variant="secondary" className="block">EfficientNetB0</Badge>
                  <Badge variant="secondary" className="block">Input: 224x224</Badge>
                  <Badge variant="secondary" className="block">Classes: 5</Badge>
                </div>
              </div>
              
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-neon-purple">Training Data</h4>
                <div className="space-y-2">
                  <Badge variant="secondary" className="block">APTOS 2019</Badge>
                  <Badge variant="secondary" className="block">ODIR Dataset</Badge>
                  <Badge variant="secondary" className="block">Data Augmentation</Badge>
                </div>
              </div>
              
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-neon-pink">Performance</h4>
                <div className="space-y-2">
                  <Badge variant="secondary" className="block">Accuracy: 89%</Badge>
                  <Badge variant="secondary" className="block">F1-Score: 0.87</Badge>
                  <Badge variant="secondary" className="block">AUC: 0.92</Badge>
                </div>
              </div>
            </div>
            
            <div className="text-center pt-6 border-t border-border">
              <p className="text-muted-foreground">
                Our model was trained using transfer learning on EfficientNetB0, fine-tuned specifically for retinal disease classification. 
                The training process included extensive data augmentation and cross-validation to ensure robust performance across different image qualities and conditions.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};