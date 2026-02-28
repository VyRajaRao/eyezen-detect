import { useState } from "react";
import { HeroSection } from "@/components/HeroSection";
import { UploadSection } from "@/components/UploadSection";
import { ResultsSection } from "@/components/ResultsSection";
import { AboutSection } from "@/components/AboutSection";
import { DisclaimerSection } from "@/components/DisclaimerSection";
import { Footer } from "@/components/Footer";
import { ChatBot } from "@/components/ChatBot";
import { useToast } from "@/hooks/use-toast";
import type { PredictionResult } from "@/types";

const Index = () => {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleImageUpload = async (imageFile: File, imageUrl: string) => {
    setUploadedImage(imageUrl);
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", imageFile);

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const message =
          errorData?.message ||
          (response.status === 400
            ? "The uploaded image does not appear to be a retinal fundus image."
            : "Prediction failed. Please try again.");
        toast({
          title: "Analysis failed",
          description: message,
          variant: "destructive",
        });
        setIsLoading(false);
        return;
      }

      const result = await response.json();
      setPredictionResult(result);
      if (result.demo_mode) {
        toast({
          title: "Demo mode – no ML service running",
          description: "Showing placeholder predictions. Start the Python service for real analysis.",
        });
      }
    } catch (_err) {
      toast({
        title: "Connection error",
        description: "Could not reach the analysis service. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetAnalysis = () => {
    setUploadedImage(null);
    setPredictionResult(null);
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="relative">
        <HeroSection />
        <UploadSection 
          onImageUpload={handleImageUpload}
          uploadedImage={uploadedImage}
          isLoading={isLoading}
          onReset={resetAnalysis}
        />
        <ResultsSection 
          result={predictionResult}
          uploadedImage={uploadedImage}
          isLoading={isLoading}
        />
        <AboutSection />
        <DisclaimerSection />
        <Footer />
        <ChatBot />
      </div>
    </div>
  );
};

export default Index;