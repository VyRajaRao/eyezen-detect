import { Brain, Database, Target, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export const AboutSection = () => {
  const features = [
    {
      icon: Brain,
      title: "Transfer-Learning CNN",
      description: "EfficientNet backbone fine-tuned on publicly available retinal datasets using transfer learning.",
      color: "text-neon-cyan",
      bgColor: "bg-neon-cyan/10"
    },
    {
      icon: Database,
      title: "Public Datasets",
      description: "Training pipelines for APTOS 2019 (DR grading) and ODIR-5K (multi-label ocular disease) datasets.",
      color: "text-neon-purple",
      bgColor: "bg-neon-purple/10"
    },
    {
      icon: Target,
      title: "Research Quality",
      description: "Designed for research exploration. Accuracy depends on training data and configuration — see the disclaimer.",
      color: "text-neon-pink",
      bgColor: "bg-neon-pink/10"
    },
    {
      icon: Users,
      title: "Multiple Conditions",
      description: "Covers ODIR-5K categories: normal, diabetic retinopathy, glaucoma, cataract, AMD, hypertension, myopia, and other.",
      color: "text-neon-green",
      bgColor: "bg-neon-green/10"
    }
  ];

  const metrics = [
    { label: "Supported Datasets", value: "2", color: "text-neon-cyan" },
    { label: "ODIR Conditions", value: "8", color: "text-neon-purple" },
    { label: "DR Grades (APTOS)", value: "5", color: "text-neon-pink" },
    { label: "Model Architecture", value: "EfficientNet", color: "text-neon-green" }
  ];

  return (
    <section className="py-20 px-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-pink bg-clip-text text-transparent">
            About Our AI Technology
          </h2>
          <p className="text-muted-foreground text-lg max-w-3xl mx-auto">
            A research-grade deep learning system built with PyTorch, trained on public retinal 
            image datasets. For educational and research use only — not a medical device.
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
                  <Badge variant="secondary" className="block">EfficientNet-B0</Badge>
                  <Badge variant="secondary" className="block">Input: 224×224</Badge>
                  <Badge variant="secondary" className="block">PyTorch</Badge>
                </div>
              </div>
              
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-neon-purple">Training Data</h4>
                <div className="space-y-2">
                  <Badge variant="secondary" className="block">APTOS 2019</Badge>
                  <Badge variant="secondary" className="block">ODIR-5K</Badge>
                  <Badge variant="secondary" className="block">Data Augmentation</Badge>
                </div>
              </div>
              
              <div className="text-center">
                <h4 className="font-semibold mb-3 text-neon-pink">Evaluation</h4>
                <div className="space-y-2">
                  <Badge variant="secondary" className="block">Per-label AUC/F1</Badge>
                  <Badge variant="secondary" className="block">Accuracy + Confusion Matrix</Badge>
                  <Badge variant="secondary" className="block">Stratified Val Split</Badge>
                </div>
              </div>
            </div>
            
            <div className="text-center pt-6 border-t border-border">
              <p className="text-muted-foreground">
                This system uses transfer learning on EfficientNet-B0, fine-tuned for retinal image classification.
                Model performance depends on the training dataset you supply.
                Evaluation metrics (AUC, F1, accuracy) are printed during training.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
};